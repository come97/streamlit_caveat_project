def get_gaming_query(merchant_name, parser_list):
    parser_str = ", ".join([f"'{parser}'" for parser in parser_list])
    return f"""
    SELECT 
    date_trunc(order_datetime, MONTH) AS month,
    ROUND(
         100.0 * COUNT(DISTINCT CASE WHEN order_original_order_number_raw IS NOT NULL THEN order_foxid END) 
        / NULLIF(COUNT(DISTINCT order_foxid), 0), 
        2
    ) AS completion_order_original_order_number_raw,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN order_total_paid IS NOT NULL THEN order_foxid END) 
        / NULLIF(COUNT(DISTINCT order_foxid), 0), 
        2
    ) AS completion_order_total_paid,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN order_total_fees IS NOT NULL THEN order_foxid END) 
        / NULLIF(COUNT(DISTINCT order_foxid), 0), 
        2
    ) AS completion_order_total_fees,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN product_name IS NOT NULL THEN order_foxid END) 
        / NULLIF(COUNT(DISTINCT order_foxid), 0), 
        2
    ) AS completion_product_name,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN seller_name IS NOT NULL THEN order_foxid END) 
        / NULLIF(COUNT(DISTINCT order_foxid), 0), 
        2
    ) AS completion_seller_name,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN order_currency IS NOT NULL THEN order_foxid END) 
        / NULLIF(COUNT(DISTINCT order_foxid), 0), 
        2
    ) AS completion_order_currency,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN order_item_billing_address IS NOT NULL THEN order_foxid END) 
        / NULLIF(COUNT(DISTINCT order_foxid), 0), 
        2
    ) AS completion_order_item_billing_address,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN order_item_original_order_number_raw IS NOT NULL THEN order_foxid END) 
        / NULLIF(COUNT(DISTINCT order_foxid), 0), 
        2
    ) AS completion_order_item_original_order_number_raw,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN order_item_currency IS NOT NULL THEN order_foxid END) 
        / NULLIF(COUNT(DISTINCT order_foxid), 0), 
        2
    ) AS completion_order_item_currency,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN payment_method_name IS NOT NULL THEN order_foxid END) 
        / NULLIF(COUNT(DISTINCT order_foxid), 0), 
        2
    ) AS completion_payment_method_name,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN order_item_total_price_paid IS NOT NULL THEN order_foxid END) 
        / NULLIF(COUNT(DISTINCT order_foxid), 0), 
        2
    ) AS completion_order_item_total_price_paid,
    COUNT(DISTINCT order_foxid) AS total_orders
FROM `foxdata_views_persisted.order_items_info`

---- COMPLETE WITH YOUR PARSERS -----
WHERE merchant_name = '{merchant_name}'
                              AND parser_name IN ({parser_str})
                              AND order_datetime >= "2022-01-01"
                              GROUP BY date_trunc(order_datetime, MONTH)
                              ORDER BY month;
    """