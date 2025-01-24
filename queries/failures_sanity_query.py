def get_failures_query(parser_list):
    parser_str = ", ".join([f"'{parser}'" for parser in parser_list])
    return f"""
    SELECT ROUND(SUM(n_has_fullblast)/SUM(orders_L3Y+n_has_fullblast),2) 
    FROM `dataops.dashboard_failures`
        WHERE parser_name IN ({parser_str})
            """

def get_sanity_query(parser_list):
    parser_str = ", ".join([f"'{parser}'" for parser in parser_list])
    return f"""
    SELECT ROUND(SUM(nb_fullblast)/SUM(nb_orders_3y+nb_fullblast),2) 
    FROM `dataops.dashboard_sanity`
    WHERE parser_name IN ({parser_str})
            """