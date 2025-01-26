import streamlit as st

def render_header():
    # Ajouter une image
    st.image("front/app-logo.png", width=80)

    st.markdown(
        f"<h1>Register Caveat Helper",
        unsafe_allow_html=True,
    )
    st.write(
        """Welcome! 👋 This app aims at simplifying and accelerating the caveat part during the new merchants creation process.✨."""
    )

