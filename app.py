
import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime
from openai import OpenAI

# ---- CONFIG ----
st.set_page_config(page_title="Broker Buddy", layout="wide")

# ---- HEADER ----
st.title("Broker Buddy - AI Compliance & Sales Assistant")
st.write("Paste your call transcript below and click **Run Analysis** to generate compliance checks, sales coaching, CRM data extraction, and lender recommendations.")

# ---- API KEY INPUT ----
api_key = st.text_input("Enter your OpenAI API Key:", type="password")

# Initialize OpenAI client if API key is entered
if api_key:
    client = OpenAI(api_key=api_key)

# ---- TRANSCRIPT INPUT ----
transcript = st.text_area("Paste Call Transcript Here:", height=300)

# ---- AI PROCESSING FUNCTIONS ----

def run_compliance_check(transcript, mileage_flagged):
    prompt = f"""
    You are a UK financial compliance officer. Review this transcript for:
    1. FCA Consumer Duty adherence.
    2. Vulnerability checks.
    3. Correct product explanation (PCP, HP, etc).
    4. Fraud red flags.
    5. Mileage suitability – was customer's declared annual mileage reflected in product offer?

    Return each item rated as Green, Amber, or Red. Include specific examples and flag if the product doesn't match the stated use.

    Transcript:
    {transcript}

    Note: Mileage mismatch was {'detected' if mileage_flagged else 'not detected'}.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=500
    )
    return response.choices[0].message.content

def run_sales_coaching(transcript):
    prompt = f"""
    You are a UK motor finance sales coach. Review this transcript and provide:
    - Feedback on rapport, structure, opportunity awareness.
    - 2 practical improvement tips.

    Transcript:
    {transcript}
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=300
    )
    return response.choices[0].message.content

def extract_crm_data(transcript):
    # Very basic logic to simulate transcript parsing for mileage
    declared_mileage = "12,000"
    selected_product_mileage = "10,000"
    mileage_flagged = declared_mileage != selected_product_mileage

    return {
        "Deposit": "£3,500",
        "Term": "48 months",
        "Annual Mileage (Stated)": declared_mileage,
        "Annual Mileage (Product)": selected_product_mileage,
        "Budget": "£300/month",
        "Mileage Mismatch": "❌ Mismatch detected" if mileage_flagged else "✅ Match"
    }, mileage_flagged

def recommend_lender(transcript):
    if "business owner" in transcript.lower() or "limited company" in transcript.lower():
        return "Suggested Lender: Aldermore - Meets business lending criteria."
    else:
        return "Suggested Lender: Alphera - Suitable for standard regulated customer."

# ---- RUN ANALYSIS ----
if st.button("Run Analysis"):
    if not transcript or not api_key:
        st.error("Please provide both your OpenAI API Key and a transcript.")
    else:
        with st.spinner("Analyzing call..."):
            crm_data, mileage_flagged = extract_crm_data(transcript)
            st.session_state['crm_data'] = crm_data
            st.session_state['mileage_flagged'] = mileage_flagged
            st.session_state['compliance_result'] = run_compliance_check(transcript, mileage_flagged)
            st.session_state['sales_result'] = run_sales_coaching(transcript)
            st.session_state['lender_recommendation'] = recommend_lender(transcript)

# ---- DISPLAY RESULTS ----
if 'compliance_result' in st.session_state:
    st.subheader("Compliance Review")
    if st.session_state['mileage_flagged']:
        st.error("❗ Mileage mismatch detected between customer need and product offer.")
    st.info(st.session_state['compliance_result'])

    st.subheader("Sales Coaching")
    st.success(st.session_state['sales_result'])

    st.subheader("CRM Data Extracted")
    st.write(pd.DataFrame([st.session_state['crm_data']]))

    st.subheader("Lender Recommendation")
    st.warning(st.session_state['lender_recommendation'])

    if st.button("Download PDF Report"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Broker Buddy - Call Report", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
        pdf.ln(10)
        report_text = (
            f"Compliance Review:\n{st.session_state['compliance_result']}\n\n"
            f"Sales Coaching:\n{st.session_state['sales_result']}\n\n"
            f"Lender Recommendation:\n{st.session_state['lender_recommendation']}\n\n"
            f"CRM: {st.session_state['crm_data']}"
        )
        pdf.multi_cell(0, 10, report_text)
        pdf.output("Broker_Buddy_Report.pdf")
        st.success("PDF Report Generated! Check your app folder.")
