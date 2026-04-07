import streamlit as st
import api_client as api
import json

def render_model_cards():
    st.markdown('<p class="gradient-text">📄 Model Cards</p>', unsafe_allow_html=True)
    st.markdown("Instantly generate and download compliance-ready PDF reports from completed Audits.")
    st.write("---")

    default_audit = st.session_state.get("latest_audit_id", "")

    st.subheader("Fetch Model Card by Audit ID")
    col1, col2 = st.columns([3, 1])
    audit_id = col1.text_input("Enter Audit ID", value=default_audit)
    fetch_btn = col2.button("Retrieve Model Card", type="primary", use_container_width=True)

    if fetch_btn and audit_id:
        res = api.get_model_card(audit_id)
        if res.status_code == 200:
            card_data = res.json()
            st.success(f"Successfully loaded Model Card for: `{card_data['model_name']}`")
            
            # --- Visual JSON Display ---
            st.markdown(f"### {card_data['model_name']} - Specifications")
            tab_info, tab_metrics = st.tabs(["Documentation", "Metrics & Fairness"])
            
            with tab_info:
                st.write("**Intended Use:**")
                st.info(card_data['intended_use'] or "N/A")
                st.write("**Out of Scope Use:**")
                st.warning(card_data['out_of_scope_use'] or "N/A")
                st.write("**Training Data:**")
                st.write(card_data['training_data_desc'] or "N/A")
                st.write("**Limitations:**")
                st.write(card_data['limitations'] or "N/A")
                st.write("**Recommendations:**")
                st.write(card_data['recommendations'] or "N/A")
                
            with tab_metrics:
                colA, colB = st.columns(2)
                with colA:
                    st.write("**Performance Summary:**")
                    st.json(card_data['performance_summary'] or {})
                with colB:
                    st.write("**Fairness Output (`fairlearn`):**")
                    st.json(card_data['fairness_summary'] or {})
                    
            st.write("---")
            st.subheader("Export to PDF")
            
            # Fetch the actual PDF bytes
            with st.spinner("Preparing PDF Document..."):
                pdf_res = api.get_model_card_pdf(audit_id)
                if pdf_res.status_code == 200:
                    st.download_button(
                        label="📥 Download Official Model Card (PDF)",
                        data=pdf_res.content,
                        file_name=f"Model_Card_{card_data['model_name'].replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        type="primary"
                    )
                else:
                    st.error("The PDF file generation failed or the file is missing from the server.")

        else:
            st.error(f"Cannot find Model Card for Audit ID `{audit_id}`. Make sure the Audit successfully completed.")
