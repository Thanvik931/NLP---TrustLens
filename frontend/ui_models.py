import streamlit as st
import api_client as api

def render_models():
    st.markdown('<p class="gradient-text">🤖 AI Models</p>', unsafe_allow_html=True)
    st.markdown("Register and manage your models connected to the TrustLens governance platform.")
    st.write("---")

    tab1, tab2 = st.tabs(["📋 Registered Models", "➕ Register New Model"])

    with tab2:
        st.subheader("Register a Remote or Local Model")
        with st.form("register_model_form"):
            model_name = st.text_input("Model Name", placeholder="e.g. Credit Risk Predictor")
            framework = st.selectbox("Framework", ["scikit-learn", "xgboost", "tensorflow", "pytorch"])
            domain_choice = st.selectbox("Domain", ["finance", "healthcare", "industrial", "other"])
            description = st.text_area("Description")
            
            submitted = st.form_submit_button("Register Model", type="primary")
            if submitted:
                if not model_name:
                    st.error("Model Name is required.")
                else:
                    payload = {
                        "name": model_name,
                        "framework": framework,
                        "domain": domain_choice,
                        "description": description
                    }
                    with st.spinner("Registering..."):
                        res = api.create_model(payload)
                        if res.status_code == 201:
                            st.success(f"Model successfully registered! ID: {res.json()['id']}")
                        else:
                            st.error(f"Failed: {res.text}")


    with tab1:
        st.subheader("Model Inventory")
        models_res = api.fetch_models()
        if models_res.status_code == 200:
            models = models_res.json()
            if not models:
                st.info("No models registered yet.")
            else:
                for mod in models:
                    with st.container():
                        colA, colB = st.columns([3, 1])
                        with colA:
                            st.markdown(f"#### {mod['name']}")
                            st.write(f"**Framework:** `{mod['framework']}` | **Domain:** {mod['domain'].title()}")
                            st.caption(f"{mod.get('description', 'No description provided.')}")
                        with colB:
                            st.button("View Rules", key=f"btn_{mod['id']}")
                        st.write("---")
        else:
            st.error("Failed to load models from the server.")
