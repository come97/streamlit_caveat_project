def get_parser_query(merchant_name, scope):
    return f"""
        SELECT
            REGEXP_REPLACE(NORMALIZE(LOWER(p.parser_name), NFD), r'\\pM', '') as parser_name
        FROM `assets_foxbrain_backoffice.merchant_has_scopes` mhs
        LEFT JOIN `assets_foxbrain_backoffice.merchants` m ON m.id_merchant = mhs.fk_merchant
        LEFT JOIN `assets_foxbrain_backoffice.scopes` s ON s.id_scope = mhs.fk_scope
        LEFT JOIN `assets_foxbrain_backoffice.merchant_has_scopes_has_parsers` mhshp ON mhshp.fk_merchant_has_scopes = id_merchant_has_scopes
        LEFT JOIN `assets_foxbrain_backoffice.parsers` p ON p.id_parser = mhshp.fk_parser
        WHERE REPLACE(LOWER(m.merchant_name), " ", "") = '{merchant_name.lower().replace(" ", "")}' 
          AND LOWER(s.scope_name) = '{scope.lower()}'
    """
