
import streamlit as st

# Page settings
st.set_page_config(page_title="AI Risk Screening", layout="wide")

st.title("AI Use Case Risk & Criticality Screening Questionnaire")

# --- Section 1: Use Case Overview ---
st.header("Section 1: Use Case Overview")
use_case_name = st.text_input("Use Case Name & Description")
business_objective = st.text_area("Business Objective")
model_type = st.selectbox("AI Model Type", ["Predictive", "Generative", "NLP", "Classification", "Other"])
deployment_env = st.selectbox("Deployment Environment", ["On-prem", "Cloud", "Hybrid"])

# --- Section 2: Data Risk Assessment ---
st.header("Section 2: Data Risk Assessment")
data_source = st.selectbox("Data Source", ["Internal", "External", "Third-party"])
data_sensitivity = st.radio("Data Sensitivity (PII/PHI/Financial/Confidential)", ["Yes", "No"])
data_bias = st.radio("Bias Checks Implemented?", ["Yes", "No"])
data_encryption = st.radio("Encryption Applied?", ["Yes", "No"])

# --- Section 3: Model Risk Assessment ---
st.header("Section 3: Model Risk Assessment")
model_explainable = st.radio("Model Transparency (Explainable)?", ["Yes", "No"])
bias_fairness = st.radio("Bias & Fairness Checks?", ["Yes", "No"])
performance_metric = st.selectbox("Performance Metric", ["Accuracy", "Precision", "Recall", "F1 Score"])
model_drift = st.radio("Model Drift Monitoring?", ["Yes", "No"])

# --- Section 4: Operational Risk ---
st.header("Section 4: Operational Risk")
criticality = st.selectbox("Criticality of Business Process", ["Low", "Medium", "High"])
dependency = st.selectbox("Dependency on AI Output", ["Advisory", "Fully Automated"])
fallback = st.radio("Fallback Mechanism (Human-in-the-loop)?", ["Yes", "No"])

# Submit button
if st.button("Submit"):
    # Simple AI Risk Scoring Logic
    risk_score = 0
    if data_sensitivity == "Yes": risk_score += 2
    if bias_fairness == "No": risk_score += 2
    if criticality == "High": risk_score += 2
    if dependency == "Fully Automated": risk_score += 2

    risk_level = "Low"
    if risk_score >= 6:
        risk_level = "High"
    elif risk_score >= 3:
        risk_level = "Medium"

    st.success(f"✅ Identified Risk Level: {risk_level}")
    st.write("Risk Score:", risk_score)
    st.write("Use Case:", use_case_name)
    st.write("Business Objective:", business_objective)

    st.info("Email notification to Risk & Compliance team simulated (SMTP can be added later).")
