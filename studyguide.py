# study_guide_app.py

import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="AI Study Guide Generator", layout="wide")

# --- Sidebar ---
st.sidebar.header("Upload or Paste Extracted Text")
extracted_text = st.sidebar.text_area("Paste extracted text from audio/video here:")

st.sidebar.write("Or upload a text file:")
uploaded_file = st.sidebar.file_uploader("Upload text file", type=["txt"])
if uploaded_file:
    extracted_text = uploaded_file.read().decode("utf-8")

# --- Additional Instructions ---
st.sidebar.header("Additional Instructions")
user_instructions = st.sidebar.text_area("Optional instructions for formatting...")

# History (to keep previous guides)
if "history" not in st.session_state:
    st.session_state["history"] = []

# --- Generate Study Guide Function ---
def generate_study_guide(text, extra_instructions=""):
    """
    Calls OpenAI API to generate study guide with structured sections
    and also creates diagram prompts for image generation.
    """
    prompt = f"""
    You are an AI that creates structured STUDY GUIDES.

    Text to analyze:
    {text}

    Additional instructions from user:
    {extra_instructions}

    Create a study guide broken into SEGMENTS if necessary.
    Each segment should include:
    - Summary
    - Bullet Takeaways
    - Key Terms without definitions
    - Quick Facts key header and 1 fact
    - Diagram (describe what should be drawn)

    Be concise, structured, and educational.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # can replace with gpt-4.1 if you want best results
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    study_guide_text = response.choices[0].message.content

    # Generate diagram image (extract first diagram request)
    diagram_prompt = f"Create an educational diagram related to: {text[:200]}"
    image_resp = client.images.generate(
        model="dall-e-3",
        prompt=diagram_prompt,
        size="1024x1024"
    )
    diagram_url = image_resp.data[0].url

    return study_guide_text, diagram_url

# --- Main UI ---
st.title(" AI Study Guide Generator")

if extracted_text:
    if st.button("Generate Study Guide"):
        with st.spinner("Generating study guide..."):
            guide, diagram = generate_study_guide(extracted_text, user_instructions)
            st.session_state.history.append({"guide": guide, "diagram": diagram})

# --- Display Study Guides (All Versions) ---
for idx, item in enumerate(st.session_state.history[::-1], 1):
    st.subheader(f"Study Guide Version {len(st.session_state.history) - idx + 1}")
    st.markdown(item["guide"])
    st.image(item["diagram"], caption="AI Generated Diagram")
    st.divider()


