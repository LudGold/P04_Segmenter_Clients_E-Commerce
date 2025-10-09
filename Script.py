# olist_dashboard_cte.py
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(r"C:\Users\lza\Documents\P04_Segmenter_Clients_E-Commerce\olist.db")
OUT_DIR = Path("exports")
OUT_DIR.mkdir(exist_ok=True)

def run_query(conn, sql, name, params=None, preview=10, export=True):
    df = pd.read_sql_query(sql, conn, params=params or ())
    print(f"\n=== {name} ===")
    print(df.head(preview))
    if export:
        out = OUT_DIR / f"{name}.csv"
        # On passe le chemin sans nommer l'argument.
        df.to_csv(str(out), index=False) 
        print(f"Export -> {out}")
    return df

with sqlite3.connect(DB_PATH) as conn:
    
    # 1) Bornes du dataset
    q_minmax = """
    WITH orders_base AS (
        SELECT order_purchase_timestamp
        FROM orders
    )
    SELECT 
        MIN(order_purchase_timestamp) AS min_ts,
        MAX(order_purchase_timestamp) AS max_ts,
        COUNT(*) AS n
    FROM orders_base;
    """
    run_query(conn, q_minmax, "01_bornes_dataset")

    #Commandes livrées en retard (>= 3 jours) sur les 3 derniers mois du dataset
    # Filtrer les commandes livrées et non annulées avec les dates
    q_retards = """
    WITH delivered AS (
        SELECT
            o.order_id,
            o.customer_id,
            o.order_status,
            DATE(o.order_purchase_timestamp)         AS purchase_date,
            DATE(o.order_delivered_customer_date)    AS delivered_date,
            DATE(o.order_estimated_delivery_date)    AS estimated_date
        FROM orders o
        WHERE o.order_status NOT IN ('canceled','cancelled')
          AND o.order_delivered_customer_date IS NOT NULL
          AND o.order_estimated_delivery_date IS NOT NULL
    ),
    max_delivered AS (
    
        SELECT MAX(delivered_date) AS max_deliv_date FROM delivered
    ),
    delayed AS (
          SELECT
            d.*,
            CAST(JULIANDAY(d.delivered_date) - JULIANDAY(d.estimated_date) AS INTEGER) AS days_late
        FROM delivered d
        WHERE (JULIANDAY(d.delivered_date) - JULIANDAY(d.estimated_date)) >= 3
    ),
    recent_delayed AS (
    
        SELECT
            dl.*
        FROM delayed dl
        CROSS JOIN max_delivered m
        WHERE DATE(dl.delivered_date) >= DATE(m.max_deliv_date, '-3 months')
    )
    
    SELECT
        order_id,
        customer_id,
        order_status,
        purchase_date AS order_purchase_timestamp,
        delivered_date AS order_delivered_customer_date,
        estimated_date AS order_estimated_delivery_date,
        days_late
    FROM recent_delayed
    ORDER BY days_late DESC, delivered_date DESC;
    """
    run_query(conn, q_retards, "02_commandes_retards_3m")

    # 3) Vendeurs avec CA > 100 000 R$ (commandes livrées)
    q_top_sellers = """
    WITH delivered_items AS (
        SELECT 
            oi.seller_id,
            oi.price
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.order_status = 'delivered'
    ),
    revenue_by_seller AS (
        SELECT
            seller_id,
            SUM(price) AS total_revenue
        FROM delivered_items
        GROUP BY seller_id
    )
    SELECT
        seller_id,
        total_revenue
    FROM revenue_by_seller
    WHERE total_revenue > 100000
    ORDER BY total_revenue DESC;
    """
    run_query(conn, q_top_sellers, "03_top_sellers_revenue_gt_100k")

    # 4) Nouveaux vendeurs (<3 mois d'ancienneté) déjà engagés (>30 produits vendus dans leurs 3 premiers mois)
    q_new_engaged = """
    WITH delivered_items AS (
        SELECT 
            oi.seller_id,
            o.order_purchase_timestamp AS purchase_ts
        FROM order_items AS oi
        JOIN orders AS o ON oi.order_id = o.order_id
        WHERE o.order_status = 'delivered'
    ),
    per_seller_first AS (
        SELECT 
            seller_id,
            MIN(purchase_ts) AS first_sale_ts
        FROM delivered_items
        GROUP BY seller_id
    ),
    dataset_max AS (
        SELECT MAX(purchase_ts) AS max_ts FROM delivered_items
    ),
    sold_in_first_3m AS (
        SELECT 
            di.seller_id,
            COUNT(*) AS products_3m
        FROM delivered_items di
        JOIN per_seller_first ps ON di.seller_id = ps.seller_id
        WHERE di.purchase_ts < DATE(ps.first_sale_ts, '+3 months')
        GROUP BY di.seller_id
    )
    SELECT 
        ps.seller_id,
        ps.first_sale_ts,
        s.products_3m,
        CAST(JULIANDAY(dm.max_ts) - JULIANDAY(ps.first_sale_ts) AS INTEGER) AS tenure_days
    FROM per_seller_first ps
    JOIN sold_in_first_3m s ON s.seller_id = ps.seller_id
    CROSS JOIN dataset_max dm
    WHERE (JULIANDAY(dm.max_ts) - JULIANDAY(ps.first_sale_ts)) < 90
      AND s.products_3m > 30
    ORDER BY s.products_3m DESC, ps.first_sale_ts ASC;
    """
    run_query(conn, q_new_engaged, "04_new_sellers_engaged")

    # 5) Pires codes postaux (moyenne reviews) sur 12 derniers mois, avec >30 reviews
    q_worst_zips = """
    WITH reviews_12m AS (
        SELECT 
            r.order_id,
            CAST(r.review_score AS INTEGER) AS review_score,
            DATE(r.review_creation_date) AS review_date
        FROM order_reviews r
        WHERE DATE(r.review_creation_date) >= DATE(
            (SELECT MAX(review_creation_date) FROM order_reviews), '-12 months'
        )
    ),
    reviews_by_zip AS (
        SELECT 
            c.customer_zip_code_prefix AS zip_code,
            rv.review_score
        FROM reviews_12m rv
        JOIN orders o    ON rv.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
    )
    SELECT
        zip_code,
        COUNT(*)                      AS n_reviews,
        ROUND(AVG(review_score), 2)   AS avg_review_score
    FROM reviews_by_zip
    GROUP BY zip_code
    HAVING COUNT(*) > 30
    ORDER BY avg_review_score ASC, n_reviews DESC
    LIMIT 5;
    """
    run_query(conn, q_worst_zips, "05_worst_zipcodes_reviews_12m")

print("\nTerminé.")

