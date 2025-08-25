import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load API Key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Helper Class ---
class FlashcardGenerator:
    def __init__(self, client):
        self.client = client

    def generate_flashcards(self, transcript: str, flashcard_type: str = "Question and Answer", num_flashcards: int = 10, 
                            tone: str = "Neutral", difficulty: str = "Medium", mood: str = "Serious") -> str:
        """Generate structured flashcards based on the transcript text."""
        if flashcard_type == "Question and Answer":
            prompt = f"""
            You are a precise and detail-oriented study assistant. Generate {num_flashcards} flashcards based strictly on the transcript.
            Do NOT add information outside the transcript.

            Requirements:
            - Each flashcard should have a **Question** and a **Short Answer**.
            - The question should be clear and focus on key details from the transcript.
            - The answer should be concise and focus on important details.
            - Tone: {tone}
            - Difficulty: {difficulty}
            - Mood: {mood}
            - Structure the flashcards with questions and concise answers.

            Transcript:
            {transcript}
            """
        elif flashcard_type == "Term and Definition":
            prompt = f"""
            You are an expert assistant creating flashcards with a **Term** and its **Definition** based on the transcript.
            Generate {num_flashcards} flashcards based strictly on the transcript.
            Do NOT add information outside the transcript.

            Requirements:
            - Each flashcard should have a **Term** and a **Definition**.
            - Define each key term mentioned in the transcript.
            - Tone: {tone}
            - Difficulty: {difficulty}
            - Mood: {mood}
            - Provide concise definitions based on the transcript.

            Transcript:
            {transcript}
            """
        elif flashcard_type == "Vocabulary":
            prompt = f"""
            You are a vocabulary expert creating flashcards for key vocabulary in the transcript.
            Generate {num_flashcards} flashcards based strictly on the transcript.
            Do NOT add information outside the transcript.

            Requirements:
            - Each flashcard should include a **Vocabulary Word** and its **Definition**.
            - Focus on words that are critical for understanding the transcript.
            - Tone: {tone}
            - Difficulty: {difficulty}
            - Mood: {mood}
            - Define the vocabulary words clearly based on the transcript.

            Transcript:
            {transcript}
            """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise and detail-oriented assistant. Only use the transcript content, no outside knowledge."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=1500
        )
        return response.choices[0].message.content


# --- Streamlit UI ---
st.set_page_config(page_title="AI Flashcard Generator", page_icon="📝", layout="centered")
st.title("📝 AI Flashcard Generator")

# User Inputs
transcript = st.text_area("Paste your transcribed paragraph here:", height=250, placeholder="Paste the full transcript here...")

flashcard_type = st.selectbox("Flashcard Type", ["Question and Answer", "Term and Definition", "Vocabulary"])
tone = st.selectbox("Tone", ["Neutral", "Friendly", "Formal", "Motivational"])
difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])
mood = st.selectbox("Mood", ["Serious", "Casual", "Encouraging", "Fun"])
num_flashcards = st.slider("Number of Flashcards", min_value=3, max_value=15, value=5)

# Generate Flashcards
if transcript and st.button("Generate Flashcards"):
    with st.spinner("✨ Generating AI Flashcards..."):
        generator = FlashcardGenerator(client)
        flashcards = generator.generate_flashcards(transcript, flashcard_type, num_flashcards, tone, difficulty, mood)

    st.success("✅ Flashcards Generated!")
    st.text_area("Your AI Flashcards:", flashcards, height=400)
