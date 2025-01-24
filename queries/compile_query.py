def generate_query(merchant_name, parser_list, fields):
    parser_str = ", ".join([f"'{parser}'" for parser in parser_list])
    
    # Générer les colonnes dynamiques
    dynamic_columns = ",\n".join([
        f"""
        ROUND(
            100.0 * COUNT(DISTINCT CASE WHEN {field} IS NOT NULL THEN order_foxid END) 
            / NULLIF(COUNT(DISTINCT order_foxid), 0), 
            2
        ) AS completion_{field.replace('.', '_')}"""
        for field in fields
    ])
    
    # Générer la requête complète
    query = f"""
    SELECT
        date_trunc(order_datetime, MONTH) AS month,
        {dynamic_columns},
    FROM `foxdata_views_persisted.order_items_info`
    WHERE merchant_name = '{merchant_name}'
    AND parser_name IN ({parser_str})
    AND order_datetime >= "2022-01-01"
    GROUP BY date_trunc(order_datetime, MONTH)
    ORDER BY month;
    """
    return query