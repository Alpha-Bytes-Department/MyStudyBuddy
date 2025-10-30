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

    def generate_comprehensive_note(
        self, 
        transcript: str, 
        additional_instructions: str = ""
    ) -> str:
        """Generate a single comprehensive study note from the entire transcript."""

        prompt = f"""
        You are an expert tutor creating a **comprehensive, student-friendly study note** that covers ALL content from the transcript below.
        

        
        CRITICAL REQUIREMENTS:
        - Create ONE complete note that summarizes the ENTIRE transcript
        - Extract and organize ALL key topics, subtopics, and important details
        - Use clear headings and subheadings to organize the content
        - Write in a student-friendly, easy-to-understand style
        - Include examples, definitions, and explanations as mentioned in the transcript
        - DO NOT add information outside the transcript
        - Structure the note logically from introduction to conclusion

        FORMAT STRUCTURE:
        
        📚 [Main Topic Title]
        ═══════════════════════════════════════
        
        📖 Overview
        [Brief introduction covering what this note is about]
        
        📝 Summary
        [Concise wrap-up of the entire content in a detailed big big big paragraph]
        

        ═══════════════════════════════════════

        STYLE GUIDELINES:
        - Use clear, conversational language
        - Break complex ideas into digestible explanations
        - Write in complete paragraphs, not bullet lists
        - Ensure the note flows logically from one section to the next
        - Make it comprehensive yet concise
        
        Additional Custom Instructions:
        {additional_instructions if additional_instructions else "None"}

        Transcript:
        {transcript}
        
        Generate a complete, well-organized study note covering ALL the content above.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert educational content creator. Create comprehensive, student-friendly notes that cover all material thoroughly while remaining clear and concise. Only use content from the provided transcript."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=3000
        )
        return response.choices[0].message.content


# --- Streamlit UI ---
st.set_page_config(page_title="AI Comprehensive Note Generator", page_icon="📝", layout="centered")

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .stTextArea textarea {
        font-size: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📝 AI Comprehensive Note Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Transform any text into a complete, student-friendly study note</div>', unsafe_allow_html=True)

# User Inputs
st.markdown("### 📄 Input Your Study Material")
transcript = st.text_area(
    "Paste your text here (lecture notes, article, textbook chapter, etc.):", 
    height=250, 
    placeholder="Paste the full text here... The AI will create one comprehensive note covering everything.",
    label_visibility="collapsed"
)

# Additional instructions
with st.expander("⚙️ Customize Your Note (Optional)"):
    additional_instructions = st.text_area(
        "Additional Instructions:", 
        height=100, 
        placeholder="Example: Focus on medical terminology, use simple language for beginners, include more examples, add mnemonics, etc.",
        help="Provide specific instructions to customize how the note should be generated"
    )

# Generate Notes
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_button = st.button("✨ Generate Comprehensive Note", type="primary", use_container_width=True)

if transcript and generate_button:
    if len(transcript.strip()) < 50:
        st.warning("⚠️ Please provide more text (at least 50 characters) to generate a meaningful note.")
    else:
        with st.spinner("✨ Creating your comprehensive study note..."):
            generator = NotesGenerator(client)
            notes = generator.generate_comprehensive_note(
                transcript, 
                additional_instructions=additional_instructions if 'additional_instructions' in locals() else ""
            )

        st.success("✅ Your comprehensive note is ready!")
        
        # Display the generated note
        st.markdown("---")
        st.markdown("### 📚 Your Study Note")
        
        # Create a nice container for the notes
        st.markdown(f"""
        <div style="
            background-color: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            border-left: 5px solid #2E86AB;
            font-family: 'Georgia', serif;
            line-height: 1.8;
            color: #333;
        ">
        {notes.replace(chr(10), "<br>")}
        </div>
        """, unsafe_allow_html=True)
        
        # Download button
        st.markdown("---")
        st.download_button(
            label="📥 Download Note as TXT",
            data=notes,
            file_name="comprehensive_study_note.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Characters", f"{len(notes):,}")
        with col2:
            st.metric("📖 Words", f"{len(notes.split()):,}")
        with col3:
            st.metric("📄 Lines", f"{len(notes.split(chr(10))):,}")

elif not transcript and generate_button:
    st.error("⚠️ Please paste some text to generate a note!")

# Help section
with st.expander("ℹ️ How to Use"):
    st.markdown("""
    **Steps:**
    1. **Paste your text** - Copy any study material (lecture notes, articles, textbook chapters, etc.)
    2. **Add custom instructions** (optional) - Specify how you want the note formatted
    3. **Click Generate** - The AI will create one comprehensive note covering everything
    4. **Download** - Save your note as a text file
    
    **Tips:**
    - Longer texts will generate more detailed notes
    - Use custom instructions to focus on specific aspects
    - The note will be organized with clear sections and subheadings
    - Perfect for exam preparation and quick revision
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'>Made with ❤️ for students | Powered by OpenAI</div>", 
    unsafe_allow_html=True
)