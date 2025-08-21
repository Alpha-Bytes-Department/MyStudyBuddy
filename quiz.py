import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load API Key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Helper Class ---
class NotesGenerator:
    def __init__(self, client):
        self.client = client

    def generate_notes(self, transcript: str, num_notes: int = 10, tone: str = "Neutral", 
                       difficulty: str = "Medium", mood: str = "Serious") -> str:
        """Generate structured study notes from transcript text."""
        prompt = f"""
        You are an expert tutor creating structured study notes STRICTLY based on the transcript below.
        Do NOT add information outside the transcript.

        Requirements:
        - Create {num_notes} sections of notes.
        - Each section should have a clear **title** and a **description**.
        - Capture ALL important details accurately.
        - Cover definitions, examples, algorithm/code explanation, steps, and conclusions.
        - Structure the notes in sections (Concept, Explanation, Steps, Code Walkthrough if present, Applications, Key Takeaways).
        - Cover definitions, examples, explanations, steps, code walkthroughs (if present), and conclusions.
        - Tone: {tone}
        - Difficulty: {difficulty}
        - Mood: {mood}
        - Make the notes high-quality, easy to follow, and optimized for students.

        Transcript:
        {transcript}
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise and detail-oriented study assistant. Only use the transcript content, no outside knowledge."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        return response.choices[0].message.content


# --- Streamlit UI ---
st.set_page_config(page_title="AI Study Notes Generator", page_icon="📝", layout="centered")
st.title("📝 AI Study Notes Generator")

# User Inputs
transcript = st.text_area("Paste your transcribed paragraph here:", height=250, placeholder="Paste the full transcript here...")

tone = st.selectbox("Tone", ["Neutral", "Friendly", "Formal", "Motivational"])
difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])
mood = st.selectbox("Mood", ["Serious", "Casual", "Encouraging", "Fun"])
num_notes = st.slider("Number of Notes", min_value=3, max_value=15, value=5)

# Generate Notes
if transcript and st.button("Generate Notes"):
    with st.spinner("✨ Generating AI Notes..."):
        generator = NotesGenerator(client)
        notes = generator.generate_notes(transcript, num_notes, tone, difficulty, mood)

    st.success("✅ Notes Generated!")
    st.text_area("Your AI Notes:", notes, height=400)
