import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load API Key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class NotesGenerator:
    def __init__(self, client):
        self.client = client

    def generate_notes(
        self, 
        transcript: str, 
        num_notes: int = 10, 
        additional_instructions: str = ""
    ) -> str:
        """Generate structured study notes from transcript text."""

        # --- Analytical adjustment based on transcript length ---
        word_count = len(transcript.split())
        # Heuristic: ~40 words per note is reasonable
        max_possible_notes = max(1, word_count // 40)

        if num_notes > max_possible_notes:
            num_notes = max_possible_notes

        prompt = f"""
        You are an expert tutor creating **structured study notes** STRICTLY based on the transcript below.
        Do NOT add information outside the transcript.

        FORMAT & STYLE REQUIREMENTS:
        - The final notes must follow this exact visual style:
            Title: <Main Topic>                            

            Note 1 – <Short, Clear Title>
            <Broad, paragraph-style explanation covering this section of the transcript.>
            
            Note 2 – <Short, Clear Title>
            <Broad, paragraph-style explanation covering this section of the transcript.>
            ... (continue as needed)

        - Each note should have a **clear title** and a **coherent, well-written paragraph** explaining that part.
        - Keep the language clear, student-friendly, and accurate.
        - DO NOT use bullet points or numbered lists inside paragraphs.
        - Capture only what is actually present in the transcript — do NOT add outside information.
        - Produce up to {num_notes} notes (adjust if transcript is short).
        - Maintain consistent formatting and spacing similar to a handwritten notebook page.
        Additional Custom Instructions:
        {additional_instructions}

        Transcript:
        {transcript}
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a precise and detail-oriented study assistant. Only use the transcript content, no outside knowledge."
                },
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
transcript = st.text_area(
    "Paste your transcribed paragraph here:", 
    height=250, 
    placeholder="Paste the full transcript here..."
)

# New free-text field for customizations
additional_instructions = st.text_area(
    "Additional Instructions", 
    height=100, 
    placeholder="Add customizations here, such as tone, difficulty level, or emojis..."
)

# Number input instead of slider
num_notes = st.number_input("Number of Notes", min_value=1, max_value=50, value=5)

# Generate Notes
if transcript and st.button("Generate Notes"):
    with st.spinner("✨ Generating AI Notes..."):
        generator = NotesGenerator(client)
        notes = generator.generate_notes(
            transcript, 
            num_notes=num_notes, 
            additional_instructions=additional_instructions
        )

    st.success("✅ Notes Generated!")
    st.text_area("Your AI Notes:", notes, height=400)
