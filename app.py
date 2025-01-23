import streamlit as st
from queries.parser_query import get_parser_query
from queries.ecom_query import get_ecom_query
from services.bigquery_service import execute_query
import plotly.express as px

# Titre
st.title("Caveat Merchant Registration")

# Sélecteur d'industrie
industries = {
    "Ecom 🛒": "ecom",
    "Payment 💳": "payment",
    "Cab 🚖": "cab",
    "Food Delivery 🍔": "food_delivery",
    "Mobile Gaming 📱🎮": "mobile_gaming",
    "Gaming 🎮": "gaming"
}

selected_industry = st.selectbox(
    "Choisissez une industrie",
    options=list(industries.keys()),
    help="Sélectionnez l'industrie pour personnaliser la requête."
)

# Obtenez l'identifiant technique de l'industrie
industry_id = industries[selected_industry]

# Champs d'entrée
merchant_name = st.text_input("Enter merchant name", placeholder="Exemple : zara")
scope = st.text_input("Enter scope", placeholder="Exemple : fr")

# Exécution des requêtes
if st.button("Exécuter les requêtes"):
    if not merchant_name or not scope:
        st.warning("Veuillez entrer un nom de marchand et un scope.")
    else:
        # Récupération des parser_name
        query_parser = get_parser_query(merchant_name, scope)
        parser_results = execute_query(query_parser)
        
        if parser_results.empty:
            st.warning("Aucun parser_name trouvé.")
        else:
            parser_list = parser_results['parser_name'].tolist()
            st.success(f"Parsers trouvés : {', '.join(parser_list)}")

            # Sélection dynamique de la requête en fonction de l'industrie
            if industry_id == "ecom":
                from queries.ecom_query import get_ecom_query as get_industry_query
            elif industry_id == "payment":
                from queries.payment_query import get_payment_query as get_industry_query
            elif industry_id == "cab":
                from queries.cab_query import get_cab_query as get_industry_query
            elif industry_id == "food_delivery":
                from queries.food_delivery_query import get_food_delivery_query as get_industry_query
            elif industry_id == "mobile_gaming":
                from queries.mobile_gaming_query import get_mobile_gaming_query as get_industry_query
            elif industry_id == "gaming":
                from queries.gaming_query import get_gaming_query as get_industry_query

            # Obtenez la requête spécifique à l'industrie
            query = get_industry_query(merchant_name, parser_list)
            industry_results = execute_query(query)

            if industry_results.empty:
                st.warning("Aucun résultat trouvé pour l'industrie sélectionnée.")
            else:
                st.success(f"Résultats récupérés avec succès pour {selected_industry} !")
                st.session_state["industry_results"] = industry_results

# Affichage d'un graphique combiné pour les champs sélectionnés
if "industry_results" in st.session_state:
    industry_results = st.session_state["industry_results"]
    fields = [col for col in industry_results.columns if col.startswith("completion")]

    # Sélection dynamique des champs
    selected_fields = st.multiselect(
        "Fields to be displayed",
        options=fields,
        default=fields,
        help="Select the fields you want to see on a single graph."
    )

    if selected_fields:
        # Créer un graphique combiné
        fig = px.line(
            industry_results,
            x="month",
            y=selected_fields,
            title=f"Completion rate per month for {selected_industry}",
            labels={"value": "Completion rate (%)", "variable": "Fields"},
            markers=True
        )
        fig.update_traces(hovertemplate="Month : %{x}<br>Valeur : %{y}%")
        fig.update_layout(
            hovermode="x unified",
            yaxis=dict(range=[0, 100])  # Limites de l'axe Y de 0 à 100
        )
        st.plotly_chart(fig)
    else:
        st.warning("Please select at least one field to display.")