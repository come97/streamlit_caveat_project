def get_order_foxid_query(merchant_name, parser_list):
    parser_str = ", ".join([f"'{parser}'" for parser in parser_list])
    return f"""
        SELECT
            DATE_TRUNC(order_datetime, MONTH) AS month,
            parser_name,
            COUNT(DISTINCT order_foxid) AS total_orders
        FROM `foxdata_views_persisted.order_items_info`
        WHERE merchant_name = '{merchant_name}'
          AND parser_name IN ({parser_str})
          AND order_datetime >= "2022-01-01"
        GROUP BY DATE_TRUNC(order_datetime, MONTH), parser_name
        ORDER BY month, parser_name;
    """
