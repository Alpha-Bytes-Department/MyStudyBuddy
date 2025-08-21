import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load API Key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Helper Functions ---
def transcribe_video(file) -> str:
    """Transcribe uploaded video/audio into text using Whisper API."""
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=file   # pass file-like object directly
    )
    return transcript.text

def generate_notes(transcript, language="English", num_notes=10, tone="Neutral", difficulty="Medium", mood="Serious"):
    """Generate high-quality, context-faithful study notes from transcript."""
    prompt = f"""
    You are an expert tutor creating study notes STRICTLY based on the transcript below. 
    Do NOT add information that is not in the transcript. 
    Your job is to capture ALL important details accurately and present them in {language}.

    - Cover definitions, examples, algorithm/code explanation, steps, and conclusions.
    - Structure the notes in sections (Concept, Explanation, Steps, Code Walkthrough if present, Applications, Key Takeaways).
    - Make the notes high-quality, easy to follow, and optimized for students.
    - Tone: {tone}
    - Difficulty: {difficulty}
    - Mood: {mood}
    - Number of summarized notes sections: {num_notes}

    Transcript:
    {transcript}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a precise and detail-oriented study assistant. Only use the transcript content, no outside knowledge."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,  # lower temp → more accuracy, less fluff
        max_tokens=1200
    )
    return response.choices[0].message.content



# --- Streamlit UI ---
st.set_page_config(page_title="AI Study Notes Generator", page_icon="📝", layout="centered")
st.title("📝 AI Study Notes Generator")

# Upload video/audio
uploaded_file = st.file_uploader("Upload your lecture video/audio", type=["mp4", "mp3", "wav", "m4a"])

# Customization options
language = st.selectbox("Language", ["English", "Bangla"])
tone = st.selectbox("Tone", ["Neutral", "Friendly", "Formal", "Motivational"])
difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])
mood = st.selectbox("Mood", ["Serious", "Casual", "Encouraging", "Fun"])
num_notes = st.slider("Number of Notes", min_value=3, max_value=15, value=5)

if uploaded_file and st.button("Generate Notes"):
    with st.spinner("⏳ Transcribing your video..."):
        transcript = transcribe_video(uploaded_file)

    with st.expander("📖 Transcript Preview"):
        st.write(transcript[:10000] + "...")  # show first part only

    with st.spinner("✨ Generating AI Notes..."):
        notes = generate_notes(transcript, language, num_notes, tone, difficulty, mood)

    st.success("✅ Notes Generated!")
    st.text_area("Your AI Notes:", notes, height=300)
