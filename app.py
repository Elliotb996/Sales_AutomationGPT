# Broker Buddy Demo App - Streamlit Skeleton (initial setup)
# Allows transcript paste OR file upload, collects email, generates CRM-style notes + red flag review

import streamlit as st
import pandas as pd
from openai import OpenAI
import tempfile
import os


st.set_page_config(page_title="Broker Buddy Demo", layout="centered")
st.title("📞 Broker Buddy - Sales Call Analyzer (Demo)")

st.markdown("Upload a call audio file **or** paste a transcript below. We'll review the call and generate a CRM-style summary, highlight any red flags, and send a sample report to your email.")

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

email = st.text_input("📧 Your Email Address (to receive demo report)")

option = st.radio("Choose input method:", ["Upload Audio File (MP3/MP4)", "Paste Transcript"])
transcript = ""

if option == "Upload Audio File (MP3/MP4)":
    uploaded_file = st.file_uploader("Upload Call Recording", type=["mp3", "mp4"])
    if uploaded_file and api_key:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        client = OpenAI(api_key=api_key)
        transcript_response = client.audio.transcriptions.create(model="whisper-1", file=open(tmp_path, "rb"))
        transcript = transcript_response.text
        st.success("Transcript created from audio.")

elif option == "Paste Transcript":
    transcript = st.text_area("Paste Transcript Here", height=300)

if st.button("Run Analysis") and transcript and email and api_key:
    with st.spinner("Analyzing call and generating CRM summary..."):
        client = OpenAI(api_key=api_key)
        crm_prompt = f"""
        You are a sales support assistant. Read the following sales call transcript and generate a CRM call note.
        Focus on customer details: deposit, budget, term, mileage, product type, objections, and decision.
        Format it like a call note typed by the salesperson.

        Transcript:
        {transcript}
        """
        crm_summary = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": crm_prompt}],
            max_tokens=400
        ).choices[0].message.content

        flag_prompt = f"""
        You are a UK compliance analyst. Read this sales transcript and identify any red flags:
        - FCA breaches
        - incorrect product explanations
        - vulnerability issues
        - signs of fraud or complaint

        Return a short summary of issues.

        Transcript:
        {transcript}
        """
        red_flags = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": flag_prompt}],
            max_tokens=300
        ).choices[0].message.content

        st.subheader("📝 CRM Summary")
        st.success(crm_summary)

        st.subheader("🚩 Red Flags / Compliance Review")
        st.warning(red_flags)

        # (Optional) Simulate sending email with summary content
        st.markdown(f"📧 *Demo email would be sent to:* `{email}`")
        st.markdown("🧪 *This is a demo. Email delivery not implemented in this preview.*")
