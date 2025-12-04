
import streamlit as st
import pandas as pd
import json

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
    if "Other" in selected_list:
        selected_list = [s for s in selected_list if s != "Other"]
        if other_text and other_text.strip():
            extras = [x.strip() for x in other_text.split(",") if x.strip()]
            selected_list.extend(extras)
    return selected_list

def max_source_risk(sources):
    mapping = {"Internal": 2, "External": 3, "Third-party": 4}
    if not sources:
        return 3
    return max([mapping.get(s, 3) for s in sources if s in mapping])

def regulatory_base_risk(regs):
    regulated = {"GDPR", "HIPAA", "RBI"}
    if any(r in regulated for r in regs): return 4
    if len(regs) > 0: return 3
    return 2

def categorize_total_risk(total):
    if total >= 3.5: return "High"
    elif total >= 2.5: return "Medium"
    else: return "Low"

def decision_matrix(risk_level, criticality):
    if risk_level == "Low": return "Approve"
    if risk_level == "Medium" and criticality == "High": return "Approve with conditions"
    if risk_level == "Medium": return "Approve"
    if risk_level == "High" and criticality == "High": return "Escalate for detailed review"
    if risk_level == "High": return "Reject or redesign"
    return "Review"

def performance_metrics_risk(metrics):
    if not metrics: return 4.5
    std = {"Accuracy", "Precision", "Recall", "F1 Score"}
    only_accuracy = (metrics == ["Accuracy"])
    has_std = any(m in std for m in metrics)
    if only_accuracy: return 3.5
    if has_std: return 2.0
    return 3.0

def add_risk(risks, category, description, severity, recommendation):
    risks.append({"Category": category, "Risk": description, "Severity": severity, "Recommended Control": recommendation})

# ---------- Section 1 ----------
st.markdown('<div class="section-title">Section 1: Use Case Overview</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    use_case_name = st.text_input("Use Case Name")
with c2:
    use_case_desc = st.text_area("Use Case Description")
business_objective = st.text_area("Business Objective")

model_types_base = ["Predictive", "Generative", "NLP", "Classification", "Other"]
model_types_sel = st.multiselect("AI Model Types (select one or more)", model_types_base)
model_types_other = st.text_input("If 'Other', specify AI Model Types (comma-separated)") if "Other" in model_types_sel else ""
model_types = enrich_with_other(model_types_sel, model_types_other)

deployment_envs_base = ["On-prem", "Cloud", "Hybrid", "Other"]
deployment_envs_sel = st.multiselect("Deployment Environment (select one or more)", deployment_envs_base)
deployment_envs_other = st.text_input("If 'Other', specify Deployment Environments (comma-separated)") if "Other" in deployment_envs_sel else ""
deployment_envs = enrich_with_other(deployment_envs_sel, deployment_envs_other)

# ---------- Section 2 ----------
st.markdown('<div class="section-title">Section 2: Data Risk Assessment</div>', unsafe_allow_html=True)
data_sources_base = ["Internal", "External", "Third-party", "Other"]
data_sources_sel = st.multiselect("Data Sources (select one or more)", data_sources_base)
data_sources_other = st.text_input("If 'Other', specify Data Sources (comma-separated)") if "Other" in data_sources_sel else ""
data_sources = enrich_with_other(data_sources_sel, data_sources_other)

data_sensitivity = st.radio("Data Sensitivity (PII/PHI/Financial/Confidential) present?", ["Yes", "No"], horizontal=True)
data_bias_checks = st.radio("Bias/Quality checks implemented?", ["Yes", "No"], horizontal=True)
data_encryption = st.radio("Encryption & retention policies applied?", ["Yes", "No"], horizontal=True)

# ---------- Section 3 ----------
st.markdown('<div class="section-title">Section 3: Model Risk Assessment</div>', unsafe_allow_html=True)
model_explainable = st.radio("Model transparency (explainable)?", ["Yes", "No"], horizontal=True)
bias_fairness = st.radio("Bias & fairness checks implemented?", ["Yes", "No"], horizontal=True)

perf_options = ["Accuracy", "Precision", "Recall", "F1 Score", "Other"]
performance_metrics_sel = st.multiselect("Performance Metrics (select one or more)", perf_options)
performance_metrics_other = st.text_input("If 'Other', specify Performance Metrics (comma-separated)") if "Other" in performance_metrics_sel else ""
performance_metrics = enrich_with_other(performance_metrics_sel, performance_metrics_other)

model_drift = st.radio("Model drift monitoring in place?", ["Yes", "No"], horizontal=True)

# ---------- Section 4 ----------
st.markdown('<div class="section-title">Section 4: Operational Risk</div>', unsafe_allow_html=True)
criticality = st.selectbox("Criticality of impacted business process", ["Low", "Medium", "High"])
dependency = st.selectbox("Dependency on AI output", ["Advisory", "Fully Automated"])
fallback = st.radio("Fallback mechanism / human-in-the-loop available?", ["Yes", "No"], horizontal=True)

# ---------- Section 5 ----------
st.markdown('<div class="section-title">Section 5: Compliance & Regulatory</div>', unsafe_allow_html=True)
regs_base = ["GDPR", "HIPAA", "RBI", "Other"]
regs_sel = st.multiselect("Applicable regulations (select one or more)", regs_base)
regs_other = st.text_input("If 'Other', specify applicable regulations (comma-separated)") if "Other" in regs_sel else ""
regs = enrich_with_other(regs_sel, regs_other)

consent = st.radio("Consent management present?", ["Yes", "No"], horizontal=True)
auditability = st.radio("Decisions traceable/auditable?", ["Yes", "No"], horizontal=True)

# ---------- Section 6 ----------
st.markdown('<div class="section-title">Section 6: Security & Privacy</div>', unsafe_allow_html=True)
access_controls = st.radio("Role-based access controls?", ["Yes", "No"], horizontal=True)
cyber_measures = st.radio("Cybersecurity measures implemented?", ["Yes", "No"], horizontal=True)
privacy_by_design = st.radio("Privacy-by-design embedded?", ["Yes", "No"], horizontal=True)

# ---------- Section 7 ----------
st.markdown('<div class="section-title">Section 7: Risk & Criticality Scoring</div>', unsafe_allow_html=True)
st.markdown('<p class="small-note">Weights are 20% for Data, Model, Operational, Regulatory, Security. 1=low risk, 5=high risk.</p>', unsafe_allow_html=True)

# Scores per dimension
data_risk_components = [
    5 if data_sensitivity == "Yes" else 2,
    4 if data_bias_checks == "No" else 2,
    4 if data_encryption == "No" else 2,
    max_source_risk([s for s in data_sources if s in ["Internal", "External", "Third-party"]])
]
data_risk_score = round(sum(data_risk_components) / len(data_risk_components), 2)

model_risk_components = [
    4 if model_explainable == "No" else 2,
    4 if bias_fairness == "No" else 2,
    performance_metrics_risk(performance_metrics),
    4 if model_drift == "No" else 2
]
model_risk_score = round(sum(model_risk_components) / len(model_risk_components), 2)

crit_map = {"Low": 2, "Medium": 3, "High": 4}
dep_map = {"Advisory": 2, "Fully Automated": 4}
operational_risk_components = [
    crit_map.get(criticality, 3),
    dep_map.get(dependency, 3),
    4 if fallback == "No" else 2
]
operational_risk_score = round(sum(operational_risk_components) / len(operational_risk_components), 2)

reg_base = regulatory_base_risk(regs)
regulatory_risk_components = [
    reg_base,
    4 if consent == "No" else 2,
    4 if auditability == "No" else 2
]
regulatory_risk_score = round(sum(regulatory_risk_components) / len(regulatory_risk_components), 2)

security_risk_components = [
    4 if access_controls == "No" else 2,
    4 if cyber_measures == "No" else 2,
    4 if privacy_by_design == "No" else 2
]
security_risk_score = round(sum(security_risk_components) / len(security_risk_components), 2)

weights = { "Data": 0.20, "Model": 0.20, "Operational": 0.20, "Regulatory": 0.20, "Security": 0.20 }
total_weighted = round(
    data_risk_score * weights["Data"] +
    model_risk_score * weights["Model"] +
    operational_risk_score * weights["Operational"] +
    regulatory_risk_score * weights["Regulatory"] +
    security_risk_score * weights["Security"], 2
)
risk_level = categorize_total_risk(total_weighted)
recommendation = decision_matrix(risk_level, criticality)

# ---------- Heuristic risks (fallback) ----------
heuristic_risks = []
if data_sensitivity == "Yes":
    add_risk(heuristic_risks, "Data", "Sensitive data present (PII/PHI/Financial/Confidential).", "High",
             "DLP, minimization, lawful basis, cross-border review.")
if "External" in data_sources or "Third-party" in data_sources:
    add_risk(heuristic_risks, "Data", "External/Third-party data increases contractual/compliance risk.", "Medium",
             "Validate licenses/DPAs, provenance checks.")
if data_bias_checks == "No":
    add_risk(heuristic_risks, "Data/Model", "Bias & quality checks missing.", "High",
             "Run bias detection, fairness metrics & mitigation.")
if data_encryption == "No":
    add_risk(heuristic_risks, "Security/Privacy", "Encryption/retention controls missing.", "High",
             "Enable at-rest/in-transit encryption, retention policy.")
if model_explainable == "No":
    add_risk(heuristic_risks, "Model", "Lack of explainability.", "Medium",
             "XAI techniques, model cards, decision logs.")
if bias_fairness == "No":
    add_risk(heuristic_risks, "Model", "Fairness checks not implemented.", "High",
             "Define fairness criteria, monitor disparate impact.")
if performance_metrics_risk(performance_metrics) >= 3.0:
    add_risk(heuristic_risks, "Model", "Insufficient performance metrics (e.g., only Accuracy).", "Medium",
             "Track Precision/Recall/F1; align to harm.")
if model_drift == "No":
    add_risk(heuristic_risks, "Model/Ops", "No drift monitoring.", "Medium",
             "Drift alerts, retraining schedule, shadow eval.")
if dependency == "Fully Automated" and criticality == "High":
    add_risk(heuristic_risks, "Operational", "High criticality with fully automated decisions.", "High",
             "Add human-in-the-loop, approvals, rollback.")
if fallback == "No":
    add_risk(heuristic_risks, "Operational", "No fallback/override.", "High",
             "Manual override, contingency plan.")
if consent == "No":
    add_risk(heuristic_risks, "Compliance", "Consent management missing.", "High",
             "Capture/manage consent, notice/opt-out, DPIA.")
if auditability == "No":
    add_risk(heuristic_risks, "Compliance", "Limited auditability/traceability.", "Medium",
             "Decision logs, model lineage, reproducibility.")
if access_controls == "No":
    add_risk(heuristic_risks, "Security", "RBAC missing.", "High",
             "Least privilege, periodic access reviews.")
if cyber_measures == "No":
    add_risk(heuristic_risks, "Security", "Cybersecurity measures incomplete.", "High",
             "Vuln mgmt, monitoring, incident response.")
if privacy_by_design == "No":
    add_risk(heuristic_risks, "Privacy", "Privacy-by-design not embedded.", "Medium",
             "Data minimization, purpose limitation, PIA.")

# ---------- AI risk generation (primary) ----------
def generate_ai_risks(payload):
    """
    Uses Azure OpenAI (preferred) or OpenAI to return a JSON list of risks.
    If neither secret is set, returns [].
    """
    prompt = f"""
You are an AI GRC analyst. Based on the questionnaire answers below, produce a JSON array named "risks"
with items: {{
  "Category": one of ["Data","Model","Operational","Compliance","Security","Privacy"],
  "Risk": short description,
  "Severity": one of ["Low","Medium","High"],
  "Recommended Control": actionable mitigation
}}.
Reference concepts: data sensitivity, bias/fairness, explainability, drift, automation dependency, fallback,
consent, auditability, RBAC, cybersecurity, privacy-by-design, applicable regulations.
Answers:
{json.dumps(payload, indent=2)}
Return ONLY valid JSON: {{ "risks": [ ... ] }}.
"""
    try:
        # Azure OpenAI first
        if "AZURE_OPENAI" in st.secrets:
            import requests
            ao = st.secrets["AZURE_OPENAI"]
            url = f"{ao['ENDPOINT']}/openai/deployments/{ao['DEPLOYMENT']}/chat/completions?api-version={ao['API_VERSION']}"
            headers = {"Content-Type": "application/json", "api-key": ao["API_KEY"]}
            body = {
                "messages": [
                    {"role": "system", "content": "You are a careful AI GRC analyst. Output strictly valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1
            }
            resp = requests.post(url, headers=headers, json=body, timeout=30)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            return parsed.get("risks", [])
        # OpenAI fallback
        if "OPENAI_API_KEY" in st.secrets:
            import requests
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}"
            }
            body = {
                "model": "gpt-4o-mini",  # or gpt-4o
                "messages": [
                    {"role": "system", "content": "You are a careful AI GRC analyst. Output strictly valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1
            }
            resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body, timeout=30)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            return parsed.get("risks", [])
    except Exception as e:
        st.warning(f"AI risk generation error: {e}")
    return []

# ---------- Submit & Results ----------
if st.button("Submit & Analyze"):
    # Build payload to send & to AI
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
        }
    }

    # 1) Show scoring
    st.subheader("Risk Scoring Breakdown")
    summary_rows = [
        {"Dimension": "Data Risk", "Weight": "20%", "Score (1-5)": data_risk_score},
        {"Dimension": "Model Risk", "Weight": "20%", "Score (1-5)": model_risk_score},
        {"Dimension": "Operational Risk", "Weight": "20%", "Score (1-5)": operational_risk_score},
        {"Dimension": "Regulatory Risk", "Weight": "20%", "Score (1-5)": regulatory_risk_score},
        {"Dimension": "Security Risk", "Weight": "20%", "Score (1-5)": security_risk_score},
    ]
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)
    c3, c4 = st.columns(2)
    with c3:
        st.metric("Total Weighted Risk (1–5)", total_weighted)
        st.metric("Identified Risk Level", risk_level)
    with c4:
        st.metric("Process Criticality", criticality)
        st.metric("Recommended Decision", recommendation)

    # 2) AI Risks (primary)
    ai_risks = generate_ai_risks(payload)
    st.divider()
    st.subheader("Identified Risks (AI)")
    if ai_risks:
        for r in ai_risks:
            sev = r.get("Severity","Medium")
            css = "risk-high" if sev == "High" else "risk-medium" if sev == "Medium" else "risk-low"
            st.markdown(
                f'<div class="{css}"><b>{r.get("Category","-")}</b>: {r.get("Risk","-")} '
                f'<br/><i>Severity:</i> {sev} '
                f'<br/><i>Recommendation:</i> {r.get("Recommended Control","-")}</div>',
                unsafe_allow_html=True
            )
    else:
        st.info("AI risks not available (no API key or error). Showing heuristic risks below.")
        for r in heuristic_risks:
            css_class = "risk-high" if r["Severity"] == "High" else "risk-medium" if r["Severity"] == "Medium" else "risk-low"
            st.markdown(
                f'<div class="{css_class}"><b>{r["Category"]}</b>: {r["Risk"]} '
                f'<br/><i>Severity:</i> {r["Severity"]} '
                f'<br/><i>Recommendation:</i> {r["Recommended Control"]}</div>',
                unsafe_allow_html=True
            )
    final_risks = ai_risks if ai_risks else heuristic_risks
    payload["identified_risks"] = final_risks

    # 3) Submission summary
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

    # 4) Routing: Power Automate webhook (preferred) or SMTP
    routed = False
    if "WEBHOOK_URL" in st.secrets:
        try:
            import requests
            resp = requests.post(st.secrets["WEBHOOK_URL"], json=payload, timeout=20)
            if 200 <= resp.status_code < 300:
                st.info("✅ Sent to Risk & Compliance workflow via Power Automate.")
                routed = True
            else:
                st.warning(f"Webhook status {resp.status_code} — check your flow.")
        except Exception as e:
            st.warning(f"Webhook error: {e}")

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

            html_risks = ''.join([f"<li><b>{r['Category']}</b> – {r['Risk']} (Severity: {r['Severity']}). <i>Control:</i> {r['Recommended Control']}</li>" for r in final_risks])
            html_body = f"""
            <h3>AI Risk Screening Submission</h3>
            <p><b>Use Case:</b> {use_case_name}</p>
            <p><b>Risk Level:</b> {risk_level} | <b>Total Weighted:</b> {total_weighted}</p>
            <p><b>Decision:</b> {recommendation}</p>
            <h4>Identified Risks (AI)</h4>
            <ul>{html_risks}</ul>
            <h4>Scores</h4>
            <ul>
                <li>Data: {data_risk_score}</li>
                <li>Model: {model_risk_score}</li>
                <li>Operational: {operational_risk_score}</li>
                <li>Regulatory: {regulatory_risk_score}</li>
                <li>Security: {security_risk_score}</li>
            </ul>
            <h4>Summary</h4>
            <p><b>Model Types:</b> {", ".join(model_types) if model_types else "-"}</p>
            <p><b>Deployment:</b> {", ".join(deployment_envs) if deployment_envs else "-"}</p>
            <p><b>Data Sources:</b> {", ".join(data_sources) if data_sources else "-"}</p>
            <p><b>Performance Metrics:</b> {", ".join(performance_metrics) if performance_metrics else "-"}</p>
            <p><b>Regulations:</b> {", ".join(regs) if regs else "-"}</p>
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

            st.info("✅ Email sent to Risk & Compliance / Legal / AI Committee.")
            routed = True
        except Exception as e:
            st.warning(f"SMTP error: {e}")

    if not routed:
        st.info("Routing simulated. Add WEBHOOK_URL (Power Automate) or EMAIL secrets to send automatically.")
