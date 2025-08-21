import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from the .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the Mindset Chatbot class
class MindsetChatbot:
    def __init__(self):
        # Define the system prompt for the chatbot
        self.system_prompt = """
        You are a mindset coach chatbot designed to help users reflect on their mindset using the 'Mindset Mantra Framework'. 
        Your goal is to guide users through steps that help them build resilience, positivity, and a personal mantra.
        
        The chatbot will ask reflective questions and provide personalized feedback based on their responses.
        The process follows these steps:
        
        1. Acceptance of Circumstances
        2. Finding Positivity
        3. Evaluating Past Ineffective Mindsets
        4. Creating a Mindset Mantra
        5. Daily Implementation
        
        Use a supportive tone and encourage self-reflection.
        """

    def get_chatbot_response(self, user_input, previous_responses=None):
        """
        Method to send the user input to OpenAI and get the chatbot's response.
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"User Input: {user_input}\nPrevious Responses: {previous_responses or 'No previous responses.'}"}
        ]

        # Request a chat completion from OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # use GPT-4o-mini (fast + cheap) or gpt-4.1 for better depth
            messages=messages,
            temperature=0.3,
            max_tokens=300
        )

        return response.choices[0].message.content.strip()


# Initialize the chatbot
chatbot = MindsetChatbot()

# Streamlit User Interface
st.title("Mindset Mantra Chatbot")
st.write("""
    Welcome to the Mindset Mantra Chatbot! This chatbot will guide you through the steps of developing a resilient, growth-focused mindset. 
    You'll reflect on your circumstances, find positivity in challenges, and create a personal mantra to help you navigate tough times.
""")

# Create a text input for the user to type their responses
user_input = st.text_input("What's the challenge you're currently facing?", "")

# Store previous responses in the session state to maintain context
if 'previous_responses' not in st.session_state:
    st.session_state.previous_responses = []

# When the user submits their response, process it
if st.button("Submit") and user_input:
    # Get the chatbot's response
    response = chatbot.get_chatbot_response(user_input, st.session_state.previous_responses)
    
    # Update session state with the new response
    st.session_state.previous_responses.append(user_input)
    
    # Display the chatbot's response
    st.write(f"**Chatbot Response**: {response}")
