# flashcard_ai.py
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize client
client = OpenAI(api_key=api_key)

st.set_page_config(page_title="AI Flashcards", page_icon="🧠", layout="centered")
st.title("🧠 AI Flashcards Helper")

# Flashcard question input
question = st.text_input("Enter your flashcard question:", "")

if st.button("Get Answer") and question.strip():
    with st.spinner("Thinking..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Or gpt-4o / gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "You are a helpful tutor answering flashcard questions clearly and concisely."},
                {"role": "user", "content": question}
            ],
            max_tokens=200,
            temperature=0.4
        )
        answer = response.choices[0].message.content
        st.success("Answer:")
        st.write(answer)
