
import streamlit as st
import pandas as pd
import json

# ---------- Page setup ----------
st.set_page_config(page_title="AI Risk & Criticality Screening", layout="wide")
st.markdown("""
<style>
.section-title {font-size:1.4rem; font-weight:700; margin-top:1.2rem; padding-bottom:0.3rem; border-bottom:1px solid #ddd;}
.small-note {font-size:0.9rem; color:#666;}
.risk-high {background:#ffe5e5; padding:0.6rem; border:1px solid #ffaaaa; border-radius:6px;}
.risk-medium {background:#fff5e0; padding:0.6rem; border:1px solid #ffd699; border-radius:6px;}
.risk-low {background:#e9ffe9; padding:0.6rem; border:1px solid #bdf0bd; border-radius:6px;}
</style>
""", unsafe_allow_html=True)

st.title("AI Use Case Risk & Criticality Screening Questionnaire")

# ---------- Helpers ----------
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

def max_source_risk(sources):
    # Internal=2, External=3, Third-party=4 (max of selected)
    mapping = {"Internal": 2, "External": 3, "Third-party": 4}
    if not sources:
        return 3  # neutral if none provided
    return max([mapping.get(s, 3) for s in sources if s in mapping])

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
    return "Review"

def performance_metrics_risk(metrics):
    """
    Heuristic:
    - No metrics -> 4.5 (high risk)
    - Only 'Accuracy' -> 3.5 (moderate-high)
    - Includes Precision/Recall/F1 (any) -> 2 (good)
    - If 'Other' only (without standard metrics) -> 3
    """
    if not metrics:
        return 4.5
    std = {"Accuracy", "Precision", "Recall", "F1 Score"}
    has_std = any(m in std for m in metrics)
    only_accuracy = metrics == ["Accuracy"]
    if only_accuracy:
        return 3.5
    if has_std:
        return 2.0
    return 3.0

def add_risk(risks, category, description, severity, recommendation):
    risks.append({
        "Category": category,
        "Risk": description,
        "Severity": severity,
        "Recommended Control": recommendation
    })

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
model_types_other = st.text_input("If 'Other', specify AI Model Types (comma-separated)") if "Other" in model_types_sel else ""
model_types = enrich_with_other(model_types_sel, model_types_other)

deployment_envs_base = ["On-prem", "Cloud", "Hybrid", "Other"]
deployment_envs_sel = st.multiselect("Deployment Environment (select one or more)", deployment_envs_base)
deployment_envs_other = st.text_input("If 'Other', specify Deployment Environments (comma-separated)") if "Other" in deployment_envs_sel else ""
deployment_envs = enrich_with_other(deployment_envs_sel, deployment_envs_other)

# ---------- Section 2: Data Risk Assessment ----------
st.markdown('<div class="section-title">Section 2: Data Risk Assessment</div>', unsafe_allow_html=True)
data_sources_base = ["Internal", "External", "Third-party", "Other"]
data_sources_sel = st.multiselect("Data Sources (select one or more)", data_sources_base)
data_sources_other = st.text_input("If 'Other', specify Data Sources (comma-separated)") if "Other" in data_sources_sel else ""
data_sources = enrich_with_other(data_sources_sel, data_sources_other)

data_sensitivity = st.radio("Data Sensitivity (PII/PHI/Financial/Confidential) present?", ["Yes", "No"], horizontal=True)
data_bias_checks = st.radio("Bias/Quality checks implemented?", ["Yes", "No"], horizontal=True)
data_encryption = st.radio("Encryption & retention policies applied?", ["Yes", "No"], horizontal=True)

# ---------- Section 3: Model Risk Assessment ----------
st.markdown('<div class="section-title">Section 3: Model Risk Assessment</div>', unsafe_allow_html=True)
model_explainable = st.radio("Model transparency (explainable)?", ["Yes", "No"], horizontal=True)
bias_fairness = st.radio("Bias & fairness checks implemented?", ["Yes", "No"], horizontal=True)

# ✅ PERFORMANCE METRIC: multi-select + Other free-text
perf_options = ["Accuracy", "Precision", "Recall", "F1 Score", "Other"]
performance_metrics_sel = st.multiselect("Performance Metrics (select one or more)", perf_options)
performance_metrics_other = st.text_input("If 'Other', specify Performance Metrics (comma-separated)") if "Other" in performance_metrics_sel else ""
performance_metrics = enrich_with_other(performance_metrics_sel, performance_metrics_other)

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
regs_other = st.text_input("If 'Other', specify applicable regulations (comma-separated)") if "Other" in regs_sel else ""
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
st.markdown('<p class="small-note">Weights are 20% for each dimension (Data, Model, Operational, Regulatory, Security). 1=low risk, 5=high risk.</p>', unsafe_allow_html=True)

# Scores per dimension
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
    performance_metrics_risk(performance_metrics),
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
reg_base = regulatory_base_risk(regs)
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

# Weighted total (1-5)
weights = { "Data": 0.20, "Model": 0.20, "Operational": 0.20, "Regulatory": 0.20, "Security": 0.20 }
total_weighted = round(
    data_risk_score * weights["Data"]
    + model_risk_score * weights["Model"]
    + operational_risk_score * weights["Operational"]
    + regulatory_risk_score * weights["Regulatory"]
    + security_risk_score * weights["Security"],
    2
)
risk_level = categorize_total_risk(total_weighted)
recommendation = decision_matrix(risk_level, criticality)

# ---------- Identified Risks (rule-based from answers) ----------
identified_risks = []
if data_sensitivity == "Yes":
    add_risk(identified_risks, "Data", "Sensitive data present (PII/PHI/Financial/Confidential).", "High",
             "Apply DLP, minimize data, lawful basis, assess cross-border transfers.")
if "External" in data_sources or "Third-party" in data_sources:
    add_risk(identified_risks, "Data", "External/Third-party data increases contractual/compliance risk.", "Medium",
             "Validate licenses/DPAs, provenance checks, intake approvals.")
if data_bias_checks == "No":
    add_risk(identified_risks, "Data/Model", "Bias & quality checks missing.", "High",
             "Run bias detection, sampling review, fairness metrics and mitigations.")
if data_encryption == "No":
    add_risk(identified_risks, "Security/Privacy", "Encryption/retention controls missing.", "High",
             "Enable encryption at-rest/in-transit, retention policies, key management.")
if model_explainable == "No":
    add_risk(identified_risks, "Model", "Lack of explainability.", "Medium",
             "Adopt XAI techniques, model cards, decision logs.")
if bias_fairness == "No":
    add_risk(identified_risks, "Model", "Fairness checks not implemented.", "High",
             "Define fairness criteria, monitor disparate impact, add governance gates.")
pm_risk = performance_metrics_risk(performance_metrics)
if pm_risk >= 3.0:
    add_risk(identified_risks, "Model", "Insufficient performance metrics (e.g., only Accuracy).", "Medium",
             "Track Precision/Recall/F1; align metrics to use-case harm.")
if model_drift == "No":
    add_risk(identified_risks, "Model/Ops", "No drift monitoring.", "Medium",
             "Add data/model drift alerts, retraining schedule, shadow evaluation.")
if dependency == "Fully Automated" and criticality == "High":
    add_risk(identified_risks, "Operational", "High criticality with fully automated decisions.", "High",
             "Add human-in-the-loop, approvals, rollback plan.")
if fallback == "No":
    add_risk(identified_risks, "Operational", "No fallback/override.", "High",
             "Define manual override, contingency plan, RTO/RPO.")
if consent == "No":
    add_risk(identified_risks, "Compliance", "Consent management missing.", "High",
             "Capture/manage consent, notice/opt-out, DPIA where applicable.")
if auditability == "No":
    add_risk(identified_risks, "Compliance", "Limited auditability/traceability.", "Medium",
             "Implement decision logs, model/version lineage, reproducibility.")
if access_controls == "No":
    add_risk(identified_risks, "Security", "RBAC missing.", "High",
             "Implement least privilege, periodic access reviews.")
if cyber_measures == "No":
    add_risk(identified_risks, "Security", "Cybersecurity measures incomplete.", "High",
             "Apply vulnerability management, monitoring, incident response.")
if privacy_by_design == "No":
    add_risk(identified_risks, "Privacy", "Privacy-by-design not embedded.", "Medium",
             "Data minimization, purpose limitation, privacy impact assessment.")

# ---------- Submit & Results ----------
if st.button("Submit & Analyze"):
    # Scoring table
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
    st.subheader("Identified Risks")
    if identified_risks:
        # Display risks with color by severity
        for r in identified_risks:
            css_class = "risk-high" if r["Severity"] == "High" else "risk-medium" if r["Severity"] == "Medium" else "risk-low"
            st.markdown(
                f'<div class="{css_class}"><b>{r["Category"]}</b>: {r["Risk"]} '
                f'<br/><i>Severity:</i> {r["Severity"]} '
                f'<br/><i>Recommendation:</i> {r["Recommended Control"]}</div>',
                unsafe_allow_html=True
            )
    else:
        st.success("No major risks identified by current heuristics.")

    st.divider()
    st.subheader("Submission Summary")
    st.write("**Use Case Name:**", use_case_name or "-")
    st.write("**Description:**", use_case_desc or "-")
    st.write("**Business Objective:**", business_objective or "-")
    st.write("**AI Model Types:**", ", ".join(model_types) if model_types else "-")
    st.write("**Deployment Environments:**", ", ".join(deployment_envs) if deployment_envs else "-")
    st.write("**Data Sources:**", ", ".join(data_sources) if data_sources else "-")
    st.write("**Performance Metrics:**", ", ".join(performance_metrics) if performance_metrics else "-")
    st.write("**Applicable Regulations:**", ", ".join(regs) if regs else "-")

    # ---------- Routing (Power Automate webhook or SMTP via Secrets) ----------
    payload = {
        "use_case_name": use_case_name,
        "use_case_desc": use_case_desc,
        "business_objective": business_objective,
        "model_types": model_types,
        "deployment_envs": deployment_envs,
        "data_sources": data_sources,
        "data_sensitivity": data_sensitivity,
        "data_bias_checks": data_bias_checks,
        "data_encryption": data_encryption,
        "model_explainable": model_explainable,
        "bias_fairness": bias_fairness,
        "performance_metrics": performance_metrics,
        "model_drift": model_drift,
        "criticality": criticality,
        "dependency": dependency,
        "fallback": fallback,
        "regs": regs,
        "consent": consent,
        "auditability": auditability,
        "access_controls": access_controls,
        "cyber_measures": cyber_measures,
        "privacy_by_design": privacy_by_design,
        "scores": {
            "data_risk": data_risk_score,
            "model_risk": model_risk_score,
            "operational_risk": operational_risk_score,
            "regulatory_risk": regulatory_risk_score,
            "security_risk": security_risk_score,
            "total_weighted": total_weighted,
            "risk_level": risk_level,
            "recommendation": recommendation
        },
        "identified_risks": identified_risks
    }

    routed = False
    # Preferred: Power Automate webhook
    if "WEBHOOK_URL" in st.secrets:
        try:
            import requests
            resp = requests.post(st.secrets["WEBHOOK_URL"], json=payload, timeout=10)
            if 200 <= resp.status_code < 300:
                st.info("Sent to Risk & Compliance workflow via Power Automate webhook.")
                routed = True
            else:
                st.warning(f"Webhook responded with status {resp.status_code}.")
        except Exception as e:
            st.warning(f"Webhook error: {e}")

    # Fallback: SMTP (requires M365 SMTP + credentials in secrets)
    if not routed and "EMAIL" in st.secrets:
        try:
            import smtplib, ssl
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            email_cfg = st.secrets["EMAIL"]
            smtp_server = email_cfg.get("SMTP_SERVER", "smtp.office365.com")
            smtp_port = int(email_cfg.get("SMTP_PORT", 587))
            username = email_cfg["USERNAME"]
            password = email_cfg["PASSWORD"]
            to_list = email_cfg.get("TO", [])

            html_body = f"""
            <h3>AI Risk Screening Submission</h3>
            <p><b>Use Case:</b> {use_case_name}</p>
            <p><b>Risk Level:</b> {risk_level} | <b>Total Weighted:</b> {total_weighted}</p>
            <p><b>Recommendation:</b> {recommendation}</p>
            <h4>Identified Risks</h4>
            <ul>
            {''.join([f"<li><b>{r['Category']}</b> – {r['Risk']} (Severity: {r['Severity']}). <i>Control:</i> {r['Recommended Control']}</li>" for r in identified_risks])}
            </ul>
            <h4>Scores</h4>
            <ul>
                <li>Data: {data_risk_score}</li>
                <li>Model: {model_risk_score}</li>
                <li>Operational: {operational_risk_score}</li>
                <li>Regulatory: {regulatory_risk_score}</li>
                <li>Security: {security_risk_score}</li>
            </ul>
            """

            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"AI Risk Screening: {use_case_name} | {risk_level}"
            msg["From"] = username
            msg["To"] = ", ".join(to_list)
            msg.attach(MIMEText(html_body, "html"))

            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls(context=context)
                server.login(username, password)
                server.sendmail(username, to_list, msg.as_string())
            st.info("Email sent to Risk & Compliance / Legal / AI Committee.")
            routed = True
        except Exception as e:
            st.warning(f"SMTP error: {e}")

    if not routed:
        st.info("Routing simulated. Configure WEBHOOK_URL (Power Automate) or EMAIL secrets to enable live routing.")
