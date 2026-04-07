import streamlit as st
import api_client as api

def render_governance():
    st.markdown('<p class="gradient-text">⚖️ Governance Rules</p>', unsafe_allow_html=True)
    st.markdown("Bind regulatory and fairness thresholds directly to your AI Models. Audits will automatically fail if these rules are breached.")
    st.write("---")

    models_res = api.fetch_models()
    if models_res.status_code != 200:
        st.error("Failed to load models. Ensure backend is running.")
        return

    models = models_res.json()
    if not models:
        st.info("No models available. Please register a model first.")
        return

    # Select a Model
    model_options = {m["name"]: m["id"] for m in models}
    selected_model_name = st.selectbox("Select Model to Manage Rules", list(model_options.keys()))
    selected_model_id = model_options[selected_model_name]

    st.write("---")
    
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"Active Rules for {selected_model_name}")
        rules_res = api.fetch_rules(selected_model_id)
        if rules_res.status_code == 200:
            rules = rules_res.json()
            if not rules:
                st.info("No rules applied yet.")
            else:
                for rule in rules:
                    with st.container():
                        st.markdown(f"**{rule['name']}** (`{rule['metric']}` > {rule['threshold']})")
                        st.caption(rule['description'])
                        st.write("---")

    with col2:
        st.subheader("Add New Rule")
        with st.form("add_rule_form"):
            rule_name = st.text_input("Rule Name", placeholder="e.g. Strict Demographic Parity")
            metric = st.selectbox("Metric to Monitor", [
                "demographic_parity", 
                "disparate_impact", 
                "equalized_odds_tpr", 
                "equalized_odds_fpr"
            ])
            threshold = st.number_input("Threshold Value", value=0.8, min_value=0.0, max_value=1.0, step=0.05)
            category = st.selectbox("Category", ["fairness", "performance", "explainability", "security"])
            description = st.text_area("Description")

            if st.form_submit_button("Bind Rule", use_container_width=True, type="primary"):
                payload = {
                    "model_id": selected_model_id,
                    "name": rule_name,
                    "metric": metric,
                    "threshold": threshold,
                    "category": category,
                    "description": description
                }
                res = api.create_rule(payload)
                if res.status_code == 201:
                    st.success("Rule added!")
                    st.rerun()
                else:
                    st.error(f"Failed: {res.text}")
