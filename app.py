import streamlit as st
from queries.parser_query import get_parser_query
from queries.compile_query import generate_query
from services.bigquery_service import execute_query
from queries.failures_sanity_query import get_failures_query, get_sanity_query
from queries.order_foxid_query import get_order_foxid_query
import plotly.express as px
from functions.full_period import generate_full_period as generate_full_period
from functions.simplify_period import format_periods as format_periods
import pandas as pd
from datetime import datetime
from config.fields_by_industry import FIELDS_BY_INDUSTRY
from front.frontend import render_header, add_custom_css

render_header()
# Sélecteur d'industrie
industries = {
    "Ecom 🛒": "ecom",
    "Payment 💳": "payment",
    "Cab 🚖": "cab",
    "Food Delivery 🍔": "food_delivery",
    "Mobile Gaming 📱🎮": "mobile_gaming",
    "Gaming 🎮": "gaming",
    "Travel ✈️": "travel"
}
selected_industry = st.selectbox(
    "Choisissez une industrie",
    options=list(industries.keys()),
    help="Sélectionnez l'industrie pour personnaliser la requête."
)

industry_id = industries[selected_industry]


merchant_name = st.text_input("Enter merchant name", placeholder="Exemple : zara")
scope = st.text_input("Enter scope", placeholder="Exemple : fr")

st.session_state.setdefault("parser_results", None)
st.session_state.setdefault("industry_results", None)
st.session_state.setdefault("order_foxid_results", None)
st.session_state.setdefault("failures_rate", 0.0)
st.session_state.setdefault("sanity_rate", 0.0)

# Exécution des requêtes
if st.button("Exécuter les requêtes"):
    if not merchant_name or not scope:
        st.warning("Veuillez entrer un nom de marchand et un scope.")
    else:
        query_parser = get_parser_query(merchant_name, scope)
        parser_results = execute_query(query_parser)

        if parser_results.empty:
            st.warning("Aucun parser_name trouvé.")
            st.session_state["parser_results"] = None
        else:
            parser_list = parser_results['parser_name'].tolist()
            st.success(f"Parsers trouvés : {', '.join(parser_list)}")
            st.session_state["parser_results"] = parser_results

            if industry_id not in FIELDS_BY_INDUSTRY:
                st.error("Aucun champ configuré pour cette industrie.")
            else:
                fields_with_priorities = FIELDS_BY_INDUSTRY[industry_id]
                fields = list(fields_with_priorities.keys())

                query = generate_query(merchant_name, parser_list, fields)

                industry_results = execute_query(query)

                if industry_results.empty:
                    st.warning("Aucun résultat trouvé pour l'industrie sélectionnée.")
                    st.session_state["industry_results"] = None
                else:
                    st.success(f"Résultats récupérés avec succès pour {selected_industry} !")
                    st.session_state["industry_results"] = industry_results

            order_foxid_query = get_order_foxid_query(merchant_name, parser_list)
            order_foxid_results = execute_query(order_foxid_query)

            if order_foxid_results.empty:
                st.warning("No data found for order_foxid.")
                st.session_state["order_foxid_results"] = None
            else:
                st.session_state["order_foxid_results"] = order_foxid_results

            # Calcul des rates failures et sanity
            failures_query = get_failures_query(parser_list)
            failures_results = execute_query(failures_query)

            if failures_results.empty or failures_results.iloc[0, 0] is None:
                st.session_state["failures_rate"] = 0.0
            else:
                st.session_state["failures_rate"] = failures_results.iloc[0, 0] * 100

            sanity_query = get_sanity_query(parser_list)
            sanity_results = execute_query(sanity_query)

            if sanity_results.empty or sanity_results.iloc[0, 0] is None:
                st.session_state["sanity_rate"] = 0.0
            else:
                st.session_state["sanity_rate"] = sanity_results.iloc[0, 0] * 100


# Affichage des graphiques et Caveats
if "industry_results" in st.session_state and st.session_state["industry_results"] is not None:
    industry_results = st.session_state["industry_results"]
    
    fields_with_priorities = FIELDS_BY_INDUSTRY[industry_id]

    renamed_columns = {
        f"completion_{field.replace('.', '_')}": f"completion_{field.replace('.', '_')} - {priority}"
        for field, priority in fields_with_priorities.items()
    }

    industry_results = industry_results.rename(columns=renamed_columns)

    fields = [col for col in industry_results.columns if col.startswith("completion")]

    full_period = pd.date_range(start="2022-01-01", end=datetime.today(), freq="MS")
    # Fusionner avec les données existantes pour inclure tous les mois
    industry_results = (
        pd.DataFrame({"month": full_period})
        .merge(industry_results, on="month", how="left")
        .fillna(0)  
    )

    selected_fields = st.multiselect(
        "Fields to be displayed",
        options=fields,
        default=fields,
        help="Select the fields you want to see on a single graph.",
        key="completion_multiselect"
    )

    if selected_fields:
        fig = px.line(
            industry_results,
            x="month",
            y=selected_fields,
            title=f"Completion rate per month for {selected_industry}",
            labels={"value": "Completion rate (%)", "variable": "Fields"},
            markers=True
        )
        fig.update_traces(hovertemplate="Month : %{x}<br>Valeur : %{y}%")
        fig.update_layout(hovermode="x unified", yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig)

if "order_foxid_results" in st.session_state and st.session_state["order_foxid_results"] is not None:
    order_foxid_results = st.session_state["order_foxid_results"]
    # Générer la plage complète de mois entre janvier 2022 et aujourd'hui
    full_period = pd.date_range(start="2022-01-01", end=datetime.today(), freq="MS")
    
    # Ajouter les mois manquants pour chaque parser_name avec total_orders=0
    parser_names = order_foxid_results["parser_name"].unique()
    full_period_df = pd.DataFrame({"month": full_period})
    all_parsers_data = []

    for parser_name in parser_names:
        parser_data = order_foxid_results[order_foxid_results["parser_name"] == parser_name]
        parser_full_data = (
            full_period_df
            .merge(parser_data, on="month", how="left")
            .fillna({"parser_name": parser_name, "total_orders": 0})  # Remplace les NaN
        )
        all_parsers_data.append(parser_full_data)

    # Combiner les données de tous les parsers
    order_foxid_results = pd.concat(all_parsers_data)

    # Supprimer les parsers où tous les mois sont à 0
    non_zero_parsers = order_foxid_results.groupby("parser_name")["total_orders"].sum()
    valid_parsers = non_zero_parsers[non_zero_parsers > 0].index
    order_foxid_results = order_foxid_results[order_foxid_results["parser_name"].isin(valid_parsers)]

    # Tracer le graphique
    fig = px.line(
        order_foxid_results,
        x="month",
        y="total_orders",
        color="parser_name",
        title="Total Orders by Parser Name Over Time",
        labels={"total_orders": "Total Orders", "month": "Month", "parser_name": "Parser Name"},
        markers=True
    )
    fig.update_traces(hovertemplate="Month : %{x}<br>Orders : %{y}<br>Parser: %{marker.color}")
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)

    # Afficher les métriques des taux de failures et sanity après le graphique
    st.markdown("### Failures and Sanity Rates")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Failures Rate", value=f"{st.session_state['failures_rate']:.2f}%")
    with col2:
        st.metric(label="Sanity Rate", value=f"{st.session_state['sanity_rate']:.2f}%")

# Création des Caveats
    st.markdown("### Caveats to Create")
caveats = []

failures_rate = st.session_state["failures_rate"]
sanity_rate = st.session_state["sanity_rate"]

if failures_rate > 0 or sanity_rate > 0:
    caveats.append(f"- **Failures or Sanity issue detected:** Failures Rate = {failures_rate:.2f}%, Sanity Rate = {sanity_rate:.2f}%")

if "order_foxid_results" in st.session_state and st.session_state["order_foxid_results"] is not None:
    order_foxid_results = st.session_state["order_foxid_results"]
    # Calculer la période complète entre janvier 2022 et aujourd'hui
    full_period = generate_full_period(
        start_date=datetime(2022, 1, 1),
        end_date=datetime.today().replace(day=1)
    )
    # Obtenir les mois où il y a du volume
    active_months = order_foxid_results["month"].dt.to_pydatetime().tolist()
    # Identifier les mois sans volume
    missing_months = [month for month in full_period if month not in active_months]
    if missing_months:
        formatted_periods = format_periods(missing_months)
        caveats.append(f"- **Volume gap detected:** No orders during {formatted_periods}.")

if "industry_results" in st.session_state and st.session_state["industry_results"] is not None:
    industry_results = st.session_state["industry_results"]

    # Parcourir les champs avec priorités
    fields_with_priorities = FIELDS_BY_INDUSTRY[industry_id]
    for field, priority in fields_with_priorities.items():
        # Ajouter le préfixe `completion_` pour vérifier les colonnes dans industry_results
        column_name = f"completion_{field}"

        # Récupération des périodes à 0% de completion
        zero_completion = industry_results[industry_results[column_name] == 0]

        if priority == "P0":
            # Règle pour les P0 : Enregistrer les périodes à 0%
            if not zero_completion.empty:
                periods = zero_completion["month"].dt.to_pydatetime().tolist()
                formatted_periods = format_periods(periods)
                caveats.append(f"- **Completion issue detected:** Field **'{column_name}'** is 0% during {formatted_periods}.")
                st.write(f"Caveat added for P0 field '{column_name}':", formatted_periods)
        
        elif priority == "P1":
            # Règle pour les P1 : Ignorer si entièrement absent
            all_zero = len(zero_completion) == len(industry_results)
            if not all_zero and not zero_completion.empty:
                # S'il y a des périodes à 0%, mais pas entièrement absent
                periods = zero_completion["month"].dt.to_pydatetime().tolist()
                formatted_periods = format_periods(periods)
                caveats.append(f"- **Completion issue detected:** Field **'{column_name}'** is 0% during {formatted_periods}.")


    if caveats:
        for caveat in caveats:
            st.markdown(caveat)
    else:
        st.success("No Caveats to create. Everything looks good!")
