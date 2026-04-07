import time
import streamlit as st
import api_client as api

def render_audits():
    st.markdown('<p class="gradient-text">📊 Live Audits</p>', unsafe_allow_html=True)
    st.markdown("Trigger full AI governance pipelines using Celery background workers and view real-time execution progress.")
    st.write("---")

    datasets_res = api.fetch_datasets()
    models_res = api.fetch_models()

    if datasets_res.status_code != 200 or models_res.status_code != 200:
        st.error("Failed to fetch assets. Ensure backend is running.")
        return

    datasets = datasets_res.json()
    models = models_res.json()

    if not datasets or not models:
        st.warning("You must have at least 1 Dataset and 1 ML Model registered to run an audit.")
        return

    ds_options = {d["name"]: d["id"] for d in datasets}
    mod_options = {m["name"]: m["id"] for m in models}

    st.subheader("Configure New Audit Run")
    with st.form("trigger_audit_form"):
        col1, col2 = st.columns(2)
        selected_ds_name = col1.selectbox("Select Target Dataset", list(ds_options.keys()))
        selected_mod_name = col2.selectbox("Select ML Model to Evaluate", list(mod_options.keys()))

        submitted = st.form_submit_button("Launch Audit Pipeline 🚀", type="primary")
        
    if submitted:
        ds_id = ds_options[selected_ds_name]
        mod_id = mod_options[selected_mod_name]
        
        # Trigger
        res = api.trigger_audit(ds_id, mod_id)
        if res.status_code != 201:
            st.error(f"Failed to start audit: {res.text}")
            return
            
        audit_id = res.json()["id"]
        st.success(f"Audit `{audit_id}` actively running on Celery workers!")
        
        # Real-time Polling Logic
        progress_bar = st.progress(0, text="Initializing Audit Pipeline...")
        status_placeholder = st.empty()
        metrics_placeholder = st.empty()

        while True:
            time.sleep(2)  # Non-blocking poll every 2 seconds
            poll_res = api.get_audit_status(audit_id)
            if poll_res.status_code == 200:
                data = poll_res.json()
                prog = data.get("progress", 0)
                status = data.get("status", "UNKNOWN")
                
                # Update visual progress
                progress_bar.progress(prog / 100.0, text=f"Processing... {prog}% ({status})")

                if status in ["PASSED", "FLAGGED", "BLOCKED"]:
                    status_color = "green" if status == "PASSED" else "red"
                    status_placeholder.markdown(f"### Final Status: <span style='color:{status_color}'>{status}</span>", unsafe_allow_html=True)
                    
                    # Layout final metrics
                    with metrics_placeholder.container():
                        st.write("---")
                        st.subheader("Audit Results")
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("Demographic Parity", f"{data.get('demographic_parity', 0):.4f}")
                        m2.metric("Disparate Impact", f"{data.get('disparate_impact', 0):.4f}")
                        m3.metric("Eq Odds TPR", f"{data.get('equalized_odds_tpr', 0):.4f}")
                        m4.metric("Accuracy", f"{data.get('overall_accuracy', 0):.4f}")
                        
                        st.info("Check the Model Cards section to download the full PDF report of this audit.")
                        
                    # Also try to auto-generate the Model Card as part of this workflow!
                    # For simplicity, we trigger the endpoint silently.
                    api.requests.post(
                        f"{api.BASE_URL}/api/model_cards", 
                        json={"audit_id": audit_id, "intended_use": "Automated run."},
                        headers=api.get_headers()
                    )
                    
                    st.session_state["latest_audit_id"] = audit_id
                    break
