
import streamlit as st
import pandas as pd

# ---------- Page setup ----------
st.set_page_config(page_title="AI Risk & Criticality Screening", layout="wide")
st.markdown("""
<style>
.section-title {font-size:1.4rem; font-weight:700; margin-top:1.2rem; padding-bottom:0.3rem; border-bottom:1px solid #ddd;}
.small-note {font-size:0.9rem; color:#666;}
.help {color:#555; font-style:italic;}
</style>
""", unsafe_allow_html=True)

st.title("AI Use Case Risk & Criticality Screening Questionnaire")

# ---------- Helper ----------
def enrich_with_other(selected_list, other_text):
    """
    If 'Other' is selected and user provided comma-separated values in other_text,
    replace 'Other' with those values.
    """
    if "Other" in selected_list:
        selected_list = [s for s in selected_list if s != "Other"]
        if other_text and other_text.strip():
            extras = [x.strip() for x in other_text.split(",") if x.strip()]
            selected_list.extend(extras)
    return selected_list

def score_mapping_yes_no(yes_value: str, score_if_yes=2, score_if_no=4):
    return score_if_yes if yes_value == "Yes" else score_if_no

def max_source_risk(sources):
    # Internal=2, External=3, Third-party=4 (max of selected)
    mapping = {"Internal": 2, "External": 3, "Third-party": 4}
    if not sources:
        return 3  # neutral if none provided
    return max([mapping.get(s, 3) for s in sources])

def regulatory_base_risk(regs):
    # Regulated (GDPR, HIPAA, RBI) -> 4; Only Other -> 3; None -> 2
    regulated = {"GDPR", "HIPAA", "RBI"}
    if any(r in regulated for r in regs):
        return 4
    if len(regs) > 0:
        return 3
    return 2

def categorize_total_risk(total):
    # 1–5 scale
    if total >= 3.5:
        return "High"
    elif total >= 2.5:
        return "Medium"
    else:
        return "Low"

def decision_matrix(risk_level, criticality):
    # From your document’s matrix
    if risk_level == "Low" and criticality in ["Low", "Medium", "High"]:
        return "Approve"
    if risk_level == "Medium" and criticality in ["Low", "Medium"]:
        return "Approve"
    if risk_level == "Medium" and criticality == "High":
        return "Approve with conditions"
    if risk_level == "High" and criticality == "High":
        return "Escalate for detailed review"
    if risk_level == "High" and criticality in ["Low", "Medium"]:
        return "Reject or redesign"
    # Fallback
    return "Review"

# ---------- Section 1: Use Case Overview ----------
st.markdown('<div class="section-title">Section 1: Use Case Overview</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    use_case_name = st.text_input("Use Case Name")
with c2:
    use_case_desc = st.text_area("Use Case Description")

business_objective = st.text_area("Business Objective")

# Multi-select with 'Other' + free-text
model_types_base = ["Predictive", "Generative", "NLP", "Classification", "Other"]
model_types_sel = st.multiselect("AI Model Types (select one or more)", model_types_base)
model_types_other = ""
if "Other" in model_types_sel:
    model_types_other = st.text_input("Specify other AI Model Types (comma-separated)")
model_types = enrich_with_other(model_types_sel, model_types_other)

deployment_envs_base = ["On-prem", "Cloud", "Hybrid", "Other"]
deployment_envs_sel = st.multiselect("Deployment Environment (select one or more)", deployment_envs_base)
deployment_envs_other = ""
if "Other" in deployment_envs_sel:
    deployment_envs_other = st.text_input("Specify other Deployment Environments (comma-separated)")
deployment_envs = enrich_with_other(deployment_envs_sel, deployment_envs_other)

# ---------- Section 2: Data Risk Assessment ----------
st.markdown('<div class="section-title">Section 2: Data Risk Assessment</div>', unsafe_allow_html=True)
data_sources_base = ["Internal", "External", "Third-party", "Other"]
data_sources_sel = st.multiselect("Data Sources (select one or more)", data_sources_base)
data_sources_other = ""
if "Other" in data_sources_sel:
    data_sources_other = st.text_input("Specify other Data Sources (comma-separated)")
data_sources = enrich_with_other(data_sources_sel, data_sources_other)

data_sensitivity = st.radio("Data Sensitivity (PII/PHI/Financial/Confidential) present?", ["Yes", "No"], horizontal=True)
data_bias_checks = st.radio("Bias/Quality checks implemented?", ["Yes", "No"], horizontal=True)
data_encryption = st.radio("Encryption & retention policies applied?", ["Yes", "No"], horizontal=True)

# ---------- Section 3: Model Risk Assessment ----------
st.markdown('<div class="section-title">Section 3: Model Risk Assessment</div>', unsafe_allow_html=True)
model_explainable = st.radio("Model transparency (explainable)?", ["Yes", "No"], horizontal=True)
bias_fairness = st.radio("Bias & fairness checks implemented?", ["Yes", "No"], horizontal=True)
performance_metric = st.selectbox("Primary performance metric tracked", ["Accuracy", "Precision", "Recall", "F1 Score"])
model_drift = st.radio("Model drift monitoring in place?", ["Yes", "No"], horizontal=True)

# ---------- Section 4: Operational Risk ----------
st.markdown('<div class="section-title">Section 4: Operational Risk</div>', unsafe_allow_html=True)
criticality = st.selectbox("Criticality of impacted business process", ["Low", "Medium", "High"])
dependency = st.selectbox("Dependency on AI output", ["Advisory", "Fully Automated"])
fallback = st.radio("Fallback mechanism / human-in-the-loop available?", ["Yes", "No"], horizontal=True)

# ---------- Section 5: Compliance & Regulatory ----------
st.markdown('<div class="section-title">Section 5: Compliance & Regulatory</div>', unsafe_allow_html=True)
regs_base = ["GDPR", "HIPAA", "RBI", "Other"]
regs_sel = st.multiselect("Applicable regulations (select one or more)", regs_base)
regs_other = ""
if "Other" in regs_sel:
    regs_other = st.text_input("Specify other applicable regulations (comma-separated)")
regs = enrich_with_other(regs_sel, regs_other)

consent = st.radio("Consent management present?", ["Yes", "No"], horizontal=True)
auditability = st.radio("Decisions traceable/auditable?", ["Yes", "No"], horizontal=True)

# ---------- Section 6: Security & Privacy ----------
st.markdown('<div class="section-title">Section 6: Security & Privacy</div>', unsafe_allow_html=True)
access_controls = st.radio("Role-based access controls?", ["Yes", "No"], horizontal=True)
cyber_measures = st.radio("Cybersecurity measures implemented?", ["Yes", "No"], horizontal=True)
privacy_by_design = st.radio("Privacy-by-design embedded?", ["Yes", "No"], horizontal=True)

# ---------- Section 7: Risk & Criticality Scoring ----------
st.markdown('<div class="section-title">Section 7: Risk & Criticality Scoring</div>', unsafe_allow_html=True)
st.markdown('<p class="small-note">Weights are 20% for each dimension (Data, Model, Operational, Regulatory, Security).</p>', unsafe_allow_html=True)

# Compute dimension scores (1=best/lowest risk, 5=worst/highest risk) using simple heuristics aligned with your questionnaire
# Data Risk
data_risk_components = [
    5 if data_sensitivity == "Yes" else 2,
    4 if data_bias_checks == "No" else 2,
    4 if data_encryption == "No" else 2,
    max_source_risk([s for s in data_sources if s in ["Internal", "External", "Third-party"]])
]
data_risk_score = round(sum(data_risk_components) / len(data_risk_components), 2)

# Model Risk
model_risk_components = [
    4 if model_explainable == "No" else 2,
    4 if bias_fairness == "No" else 2,
    4 if model_drift == "No" else 2
]
model_risk_score = round(sum(model_risk_components) / len(model_risk_components), 2)

# Operational Risk
crit_map = {"Low": 2, "Medium": 3, "High": 4}
dep_map = {"Advisory": 2, "Fully Automated": 4}
operational_risk_components = [
    crit_map.get(criticality, 3),
    dep_map.get(dependency, 3),
    4 if fallback == "No" else 2
]
operational_risk_score = round(sum(operational_risk_components) / len(operational_risk_components), 2)

# Regulatory Risk
reg_base = regulatory_base_risk([r for r in regs if r in ["GDPR", "HIPAA", "RBI"] or r not in ["GDPR", "HIPAA", "RBI"]])
regulatory_risk_components = [
    reg_base,
    4 if consent == "No" else 2,
    4 if auditability == "No" else 2
]
regulatory_risk_score = round(sum(regulatory_risk_components) / len(regulatory_risk_components), 2)

# Security Risk
security_risk_components = [
    4 if access_controls == "No" else 2,
    4 if cyber_measures == "No" else 2,
    4 if privacy_by_design == "No" else 2
]
security_risk_score = round(sum(security_risk_components) / len(security_risk_components), 2)

# Weighted total
weights = {
    "Data Risk": 0.20,
    "Model Risk": 0.20,
    "Operational Risk": 0.20,
    "Regulatory Risk": 0.20,
    "Security Risk": 0.20
}
total_weighted = round(
    data_risk_score * weights["Data Risk"]
    + model_risk_score * weights["Model Risk"]
    + operational_risk_score * weights["Operational Risk"]
    + regulatory_risk_score * weights["Regulatory Risk"]
    + security_risk_score * weights["Security Risk"],
    2
)
risk_level = categorize_total_risk(total_weighted)
recommendation = decision_matrix(risk_level, criticality)

# ---------- Submit & Results ----------
if st.button("Submit & Analyze"):
    summary_rows = [
        {"Dimension": "Data Risk", "Weight": "20%", "Score (1-5)": data_risk_score},
        {"Dimension": "Model Risk", "Weight": "20%", "Score (1-5)": model_risk_score},
        {"Dimension": "Operational Risk", "Weight": "20%", "Score (1-5)": operational_risk_score},
        {"Dimension": "Regulatory Risk", "Weight": "20%", "Score (1-5)": regulatory_risk_score},
        {"Dimension": "Security Risk", "Weight": "20%", "Score (1-5)": security_risk_score},
    ]
    st.subheader("Risk Scoring Breakdown")
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.metric("Total Weighted Risk (1–5)", total_weighted)
        st.metric("Identified Risk Level", risk_level)
    with c4:
        st.metric("Process Criticality", criticality)
        st.metric("Recommended Decision", recommendation)

    st.divider()
    st.subheader("Submission Summary")
    st.write("**Use Case Name:**", use_case_name or "-")
    st.write("**Description:**", use_case_desc or "-")
    st.write("**Business Objective:**", business_objective or "-")
    st.write("**AI Model Types:**", ", ".join(model_types) if model_types else "-")
    st.write("**Deployment Environments:**", ", ".join(deployment_envs) if deployment_envs else "-")
    st.write("**Data Sources:**", ", ".join(data_sources) if data_sources else "-")
    st.write("**Applicable Regulations:**", ", ".join(regs) if regs else "-")

    st.info("For demo, email/workflow routing is not enabled here. You can add Power Automate or SMTP later.")

# ---------- Optional: Helper sidebar ----------
with st.sidebar:
    st.caption("Tips")
    st.markdown("""
- If you select **Other**, please type one or more values (comma-separated).
- Scores are heuristic and for demonstration. Replace with your organization's policy when ready.
- Use the **Submit & Analyze** button to compute risk and see the decision recommendation.
    """)

