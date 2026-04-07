import streamlit as st
import api_client as api
import pandas as pd
import ast

def render_datasets():
    st.markdown('<p class="gradient-text">📁 Datasets</p>', unsafe_allow_html=True)
    st.markdown("Upload and analyze structured CSV datasets for AI training and evaluation.")
    st.write("---")

    tab1, tab2 = st.tabs(["📊 Browse Datasets", "☁️ Upload New Dataset"])

    with tab2:
        st.subheader("Upload Dataset for Auditing")
        with st.form("upload_dataset_form"):
            col1, col2 = st.columns(2)
            dataset_name = col1.text_input("Dataset Name", placeholder="e.g. Adult Census Income")
            domain_choice = col2.selectbox("Domain", ["finance", "healthcare", "industrial", "other"])
            description = st.text_area("Description")
            
            st.markdown("**Sensitive Columns Setup**")
            col3, col4 = st.columns(2)
            sensitive_cols_str = col3.text_input("Sensitive Columns (comma separated)", placeholder="race, sex, age")
            target_col = col4.text_input("Target Column", placeholder="income_pred")
            
            uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
            
            submitted = st.form_submit_button("Upload & Profile", type="primary")
            if submitted:
                if not uploaded_file or not dataset_name or not target_col:
                    st.error("Please fill all required fields and attach a CSV.")
                else:
                    # Clean up inputs
                    sens_list = [x.strip() for x in sensitive_cols_str.split(",") if x.strip()]
                    import json
                    
                    data_payload = {
                        "name": dataset_name,
                        "domain": domain_choice,
                        "description": description,
                        "sensitive_cols": json.dumps(sens_list),
                        "target_col": target_col
                    }
                    
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                    
                    with st.spinner("Uploading and analyzing..."):
                        import requests
                        headers = {}
                        if "access_token" in st.session_state:
                            headers["Authorization"] = f"Bearer {st.session_state['access_token']}"
                        
                        # Use raw request since api_client currently doesn't wrap file uploads easily
                        res = requests.post(f"{api.BASE_URL}/api/datasets/upload", headers=headers, data=data_payload, files=files)
                        
                        if res.status_code == 201:
                            st.success(f"Dataset successfully analyzed! ID: {res.json()['id']}")
                        else:
                            st.error(f"Failed: {res.text}")


    with tab1:
        st.subheader("Available Datasets")
        datasets_res = api.fetch_datasets()
        if datasets_res.status_code == 200:
            datasets = datasets_res.json()
            if not datasets:
                st.info("No datasets found. Upload one to get started.")
            else:
                for ds in datasets:
                    with st.container():
                        st.markdown(f"#### {ds['name']}")
                        st.write(f"**Domain:** {ds['domain'].title()} | **Rows:** {ds.get('num_rows', 'Unknown')} | **Columns:** {ds.get('num_cols', 'Unknown')}")
                        st.write(f"**Target:** `{ds.get('target_col')}` | **Protected Specs:** `{ds.get('sensitive_cols')}`")
                        
                        with st.expander("View Generated AI Profile / Schema"):
                            try:
                                profile = ast.literal_eval(ds.get('profile_summary', '{}'))
                            except:
                                profile = ds.get('profile_summary', {})
                            st.json(profile)
                        st.write("---")
        else:
            st.error("Failed to load datasets from the server.")
