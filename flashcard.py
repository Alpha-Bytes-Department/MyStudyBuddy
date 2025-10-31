import streamlit as st
import json
from typing import List, Dict
import re
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class FlashcardGenerator:
    def __init__(self, client):
        self.client = client
    
    def analyze_text_capacity(self, text: str) -> Dict:
        """Analyze text and determine maximum flashcards that can be generated"""
        
        prompt = f"""Analyze the following text and determine how many quality flashcards can be generated from it.

Text to analyze:
{text}

Consider these factors:
1. Text length and word count
2. Number of distinct concepts, topics, or key ideas present
3. Depth of information provided
4. Variety of information (definitions, facts, processes, examples)
5. Redundancy or repetition in the content

Provide only a single number representing the absolute maximum number of unique, quality flashcards that can be generated from this text.

Rules:
- Be realistic - don't overestimate capacity
- A short paragraph can typically support 2-5 flashcards
- A page of text can typically support 8-15 flashcards
- Each flashcard needs substantial, distinct information

Return only the number, nothing else.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert educational content analyzer. Provide accurate assessments of text capacity for flashcard generation. Return only a single number."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract just the number
            max_flashcards = int(re.search(r'\d+', content).group())
            
            return {
                "max_flashcards": max_flashcards
            }
            
        except Exception as e:
            st.error(f"Error analyzing text: {str(e)}")
            # Fallback to simple word count based estimation
            word_count = len(text.split())
            estimated = max(1, min(20, word_count // 50))
            return {
                "max_flashcards": estimated
            }
    
    def generate_flashcards(self, text: str, flashcard_type: str, num_cards: int, additional_instructions: str = "") -> List[Dict]:
        """Generate flashcards from input text"""
        
        if flashcard_type == "Question and Answer":
            format_instruction = """Generate flashcards in this exact JSON format:
[
    {
        "question": "What is...?",
        "answer": "Short, concise answer"
    }
]"""
        else:  # Terms and Definition
            format_instruction = """Generate flashcards in this exact JSON format:
[
    {
        "term": "Key term",
        "definition": "Clear, concise definition"
    }
]"""
        
        prompt = f"""Based on the following text, create exactly {num_cards} flashcards in {flashcard_type} format.

Text:
{text}

Additional Instructions: {additional_instructions if additional_instructions else "None"}

{format_instruction}

Requirements:
- Create exactly {num_cards} flashcards
- Keep answers/definitions concise (1-3 sentences)
- Focus on key concepts from the text
- Return ONLY valid JSON array, no other text
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a precise flashcard creator. Return only valid JSON arrays. Extract information only from the provided text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from markdown code blocks if present
            json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            
            flashcards = json.loads(content)
            return flashcards
            
        except json.JSONDecodeError as e:
            st.error(f"Error parsing flashcards: {str(e)}")
            return []
        except AttributeError as e:
            st.error(f"API Error: Please check your OpenAI API key is valid")
            return []
        except Exception as e:
            st.error(f"Error generating flashcards: {str(e)}")
            return []
    
    def check_answer(self, correct_answer: str, user_answer: str) -> Dict:
        """Check if user's answer is correct using AI"""
        
        prompt = f"""Compare the user's answer with the correct answer and evaluate if it's correct.

Correct Answer: {correct_answer}
User's Answer: {user_answer}

Respond in this exact JSON format:
{{
    "is_correct": true/false,
    "feedback": "Brief feedback explaining why it's correct or what's missing"
}}

IMPORTANT EVALUATION CRITERIA:
- Mark as CORRECT if the user's answer conveys the SAME MAIN IDEA or CONCEPT as the correct answer
- Ignore differences in wording, phrasing, or sentence structure
- Accept synonyms, paraphrases, and alternative explanations
- Focus on SEMANTIC MEANING, not exact word matching
- Be lenient - if the core concept is present, mark it correct
- Only mark incorrect if the answer is factually wrong or missing key concepts
- Minor omissions of details are acceptable if the main point is captured

Examples of what should be marked CORRECT:
- Correct: "The heart pumps blood" | User: "The heart circulates blood through the body" ✓
- Correct: "Mitochondria produce energy" | User: "Mitochondria generate ATP for cells" ✓
- Correct: "Photosynthesis converts light to energy" | User: "Plants use sunlight to make food" ✓
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an educational evaluator. Be fair but thorough. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from markdown code blocks if present
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            
            result = json.loads(content)
            return result
            
        except Exception as e:
            st.error(f"Error checking answer: {str(e)}")
            return {"is_correct": False, "feedback": "Error evaluating answer"}


def main():
    st.set_page_config(page_title="AI Flashcard Generator", page_icon="🎴", layout="wide")
    
    # Custom CSS
    st.markdown("""
        <style>
        .flashcard {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .correct {
            background-color: #d4edda;
            border-left: 5px solid #28a745;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .incorrect {
            background-color: #f8d7da;
            border-left: 5px solid #dc3545;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .analysis-box {
            background-color: #e7f3ff;
            border-left: 5px solid #2196F3;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🎴 AI Flashcard Generator")
    st.markdown("Generate and study flashcards with AI-powered feedback")
    
    # Initialize session state
    if 'flashcards' not in st.session_state:
        st.session_state.flashcards = []
    if 'current_card' not in st.session_state:
        st.session_state.current_card = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = {}
    if 'text_analysis' not in st.session_state:
        st.session_state.text_analysis = None
    
    # Main content area
    tab1, tab2 = st.tabs(["📝 Generate Flashcards", "📚 Study Mode"])
    
    with tab1:
        st.header("Create Your Flashcards")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            input_text = st.text_area(
                "Enter your study material:",
                height=200,
                placeholder="Paste your text here... (lecture notes, textbook content, etc.)"
            )
            
            # Feature 1: Analyze Text Button
            if st.button("🔍 Analyze Text Capacity", use_container_width=True):
                if not input_text or len(input_text.strip()) < 20:
                    st.warning("⚠️ Please enter at least 20 characters of text to analyze")
                else:
                    with st.spinner("🔄 Analyzing your text..."):
                        generator = FlashcardGenerator(client)
                        analysis = generator.analyze_text_capacity(input_text)
                        st.session_state.text_analysis = analysis
                        st.rerun()
            
            # Feature 2: Display Analysis Results
            if st.session_state.text_analysis:
                analysis = st.session_state.text_analysis
                
                st.markdown(f"""
                <div class="analysis-box">
                    <h4>📊 Text Analysis Results</h4>
                    <p><strong>Maximum Flashcards Possible:</strong> {analysis['max_flashcards']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            flashcard_type = st.selectbox(
                "Flashcard Type:",
                ["Question and Answer", "Terms and Definition"]
            )
            
            # Feature 3: Dynamic Number Input with Validation
            if st.session_state.text_analysis:
                max_allowed = st.session_state.text_analysis['max_flashcards']
                
                num_cards = st.number_input(
                    "Number of Flashcards:",
                    min_value=1,
                    max_value=max_allowed,
                    value=min(5, max_allowed),
                    help=f"Based on your text, maximum {max_allowed} flashcards can be generated"
                )
                
                # Show info if user reaches maximum
                if num_cards == max_allowed:
                    st.info(f"ℹ️ You've reached the maximum of {max_allowed} flashcards for this text.")
                    
            else:
                num_cards = st.number_input(
                    "Number of Flashcards:",
                    min_value=1,
                    max_value=20,
                    value=5,
                    help="Analyze your text first to see recommended numbers"
                )
                st.info("💡 Click 'Analyze Text Capacity' to see how many flashcards can be generated from your text")
            
            additional_instructions = st.text_area(
                "Additional Instructions:",
                height=100,
                placeholder="e.g., Focus on key dates, Include examples, etc."
            )
        
        if st.button("🎯 Generate Flashcards", type="primary", use_container_width=True):
            if not input_text:
                st.error("⚠️ Please enter some text to generate flashcards")
            elif len(input_text.strip()) < 20:
                st.error("⚠️ Text is too short. Please provide at least 20 characters.")
            else:
                # ALWAYS analyze first if not already done
                if not st.session_state.text_analysis:
                    with st.spinner("🔄 Analyzing text capacity..."):
                        generator = FlashcardGenerator(client)
                        analysis = generator.analyze_text_capacity(input_text)
                        st.session_state.text_analysis = analysis
                
                # Now validate against analysis
                max_allowed = st.session_state.text_analysis['max_flashcards']
                if num_cards > max_allowed:
                    st.error(f"❌ Cannot generate {num_cards} flashcards. Maximum possible for this text is {max_allowed}. Please reduce the number or add more content.")
                else:
                    with st.spinner("🔄 Generating flashcards..."):
                        generator = FlashcardGenerator(client)
                        flashcards = generator.generate_flashcards(
                            input_text,
                            flashcard_type,
                            num_cards,
                            additional_instructions
                        )
                        
                        if flashcards:
                            st.session_state.flashcards = flashcards
                            st.session_state.flashcard_type = flashcard_type
                            st.session_state.current_card = 0
                            st.session_state.user_answers = {}
                            st.session_state.show_answer = {}
                            st.success(f"✅ Generated {len(flashcards)} flashcards!")
                            st.info("👉 Go to 'Study Mode' tab to practice")
        
        # Preview generated flashcards
        if st.session_state.flashcards:
            st.markdown("---")
            st.subheader("📋 Generated Flashcards Preview")
            
            # Generate JSON response for backend
            json_response = {
                "status": "success",
                "data": {
                    "flashcards": st.session_state.flashcards,
                    "flashcard_type": st.session_state.flashcard_type,
                    "total_count": len(st.session_state.flashcards),
                    "text_analysis": st.session_state.text_analysis if st.session_state.text_analysis else None,
                    "metadata": {
                        "generated_at": None,  # Can add timestamp if needed
                        "input_text_length": len(input_text) if input_text else 0,
                        "custom_instructions": additional_instructions if additional_instructions else None
                    }
                }
            }
            
            # Display JSON response
            st.markdown("### 🔗 JSON Response for Backend")
            st.json(json_response)
            
            # Download JSON button
            json_string = json.dumps(json_response, indent=2, ensure_ascii=False)
            st.download_button(
                label="📋 Download JSON Response",
                data=json_string,
                file_name="flashcards_response.json",
                mime="application/json",
                use_container_width=True
            )
            
            st.markdown("---")
            
            for idx, card in enumerate(st.session_state.flashcards):
                with st.expander(f"Flashcard"):
                    if st.session_state.flashcard_type == "Question and Answer":
                        st.markdown(f"**Q:** {card.get('question', 'N/A')}")
                        st.markdown(f"**A:** {card.get('answer', 'N/A')}")
                    else:
                        st.markdown(f"**Term:** {card.get('term', 'N/A')}")
                        st.markdown(f"**Definition:** {card.get('definition', 'N/A')}")
    
    with tab2:
        st.header("Study Your Flashcards")
        
        if not st.session_state.flashcards:
            st.info("📭 No flashcards generated yet. Go to 'Generate Flashcards' tab to create some!")
        else:
            # Progress bar
            progress = (st.session_state.current_card + 1) / len(st.session_state.flashcards)
            st.progress(progress)
            st.markdown(f"**Card {st.session_state.current_card + 1} of {len(st.session_state.flashcards)}**")
            
            # Navigation
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                if st.button("⬅️ Previous", disabled=st.session_state.current_card == 0):
                    st.session_state.current_card -= 1
                    st.rerun()
            
            with col3:
                if st.button("Next ➡️", disabled=st.session_state.current_card >= len(st.session_state.flashcards) - 1):
                    st.session_state.current_card += 1
                    st.rerun()
            
            # Current flashcard
            current_idx = st.session_state.current_card
            card = st.session_state.flashcards[current_idx]
            
            st.markdown("---")
            
            # Display question/term
            if st.session_state.flashcard_type == "Question and Answer":
                st.markdown(f"### ❓ {card.get('question', 'N/A')}")
                correct_answer = card.get('answer', '')
            else:
                st.markdown(f"### 📌 {card.get('term', 'N/A')}")
                correct_answer = card.get('definition', '')
            
            # User answer input
            user_answer = st.text_area(
                "Your answer:",
                height=100,
                key=f"answer_{current_idx}",
                value=st.session_state.user_answers.get(current_idx, "")
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Check Answer", type="primary", use_container_width=True):
                    if not user_answer.strip():
                        st.warning("⚠️ Please write an answer first")
                    else:
                        st.session_state.user_answers[current_idx] = user_answer
                        
                        with st.spinner("🔄 Checking your answer..."):
                            generator = FlashcardGenerator(client)
                            result = generator.check_answer(correct_answer, user_answer)
                            st.session_state.show_answer[current_idx] = result
                        st.rerun()
            
            with col2:
                if st.button("👁️ Show Answer", use_container_width=True):
                    st.session_state.show_answer[current_idx] = {
                        "is_correct": None,
                        "feedback": "Answer revealed",
                        "show_only": True
                    }
                    st.rerun()
            
            # Show feedback
            if current_idx in st.session_state.show_answer:
                result = st.session_state.show_answer[current_idx]
                
                st.markdown("---")
                
                if result.get("show_only"):
                    st.info(f"**Correct Answer:** {correct_answer}")
                elif result.get("is_correct"):
                    st.markdown(f'<div class="correct">✅ <strong>Correct!</strong><br>{result.get("feedback", "")}</div>', unsafe_allow_html=True)
                    st.success(f"**Correct Answer:** {correct_answer}")
                else:
                    st.markdown(f'<div class="incorrect">❌ <strong>Not quite right</strong><br>{result.get("feedback", "")}</div>', unsafe_allow_html=True)
                    st.error(f"**Correct Answer:** {correct_answer}")
            
            # Statistics
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            answered = len([k for k, v in st.session_state.show_answer.items() if v.get("is_correct") is not None])
            correct = len([k for k, v in st.session_state.show_answer.items() if v.get("is_correct") == True])
            
            with col1:
                st.metric("📊 Answered", f"{answered}/{len(st.session_state.flashcards)}")
            with col2:
                st.metric("✅ Correct", correct)
            with col3:
                accuracy = (correct / answered * 100) if answered > 0 else 0
                st.metric("🎯 Accuracy", f"{accuracy:.1f}%")


if __name__ == "__main__":
    main()