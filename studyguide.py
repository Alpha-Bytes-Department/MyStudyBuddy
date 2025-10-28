import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import json

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Study Guide Generator", layout="wide")

def generate_study_guide(text):
    """Generate a comprehensive study guide from input text"""
    
    prompt = f"""Analyze the following text and create a comprehensive study guide. 

Text to analyze:
{text}

IMPORTANT: You must respond ONLY with valid JSON. Do not include any text before or after the JSON.

Generate a JSON response with this exact structure:
{{
    "main_title": "Main topic title",
    "sections": [
        {{
            "section_title": "Section name",
            "summary": "A comprehensive paragraph with 5-8 sentences covering all key points of this section in detail",
            "bullet_takeaways": [
                "Bullet Takeaway 1",
                "Bullet Takeaway 2",
                "Bullet Takeaway 3",
                "... as many as needed to cover the section"
            ],
            "key_terms": [
                "Term 1",
                "Term 2",
                "Term 3",
                "... just the key words/phrases, no definitions"
            ],
            "quick_facts": [
                {{"term": "Concept name", "definition": "Brief explanation or definition"}},
                {{"term": "Another concept", "definition": "Its explanation"}},
                "... as many term-definition pairs as relevant"
            ],
            "needs_diagram": true,
            "diagram_description": "Description of what diagram should illustrate (only if needs_diagram is true)"
        }}
    ]
}}

Rules:
1. Create multiple sections that logically divide the content
2. Each section should cover a distinct portion of the text
3. Ensure ALL content from the original text is covered across sections
4. **SUMMARY**: Write a FULL PARAGRAPH with 5-8 detailed sentences (or more if needed) that thoroughly explains all key concepts, processes, and important details in this section
5. **BULLET TAKEAWAYS**: Include ALL important takeaways from the section - as many as needed to fully cover the section content
6. **KEY TERMS**: List ONLY the key words or phrases as simple strings (like "Mitosis", "Cell cycle", "DNA replication") - NO definitions, just the terms themselves
7. **QUICK FACTS**: Provide term-definition pairs as objects with "term" and "definition" fields - include ALL important concepts that need explanation
8. Set needs_diagram to true only when a visual representation would significantly aid understanding (processes, cycles, structures, relationships)
9. Use true or false (not "true" or "false" as strings) for needs_diagram
10. Be comprehensive and detailed - summaries should be thorough paragraphs, not brief overviews
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert educator who creates comprehensive study guides. You MUST respond with ONLY valid JSON, nothing else. No explanations, no markdown code blocks, just pure JSON. Be thorough and comprehensive - include all relevant information from each section. Write detailed, multi-sentence summaries."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.7
    )
    
    content = response.choices[0].message.content.strip()
    
    # Remove markdown code blocks if present
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()
    
    return json.loads(content)

def generate_diagram(description):
    """Generate a diagram using DALL-E based on description"""
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Create a clear, educational diagram showing: {description}. Style: clean, simple, educational illustration with labels and arrows where appropriate. Use a white or light background.",
            size="1024x1024",
            quality="standard",
            n=1
        )
        return response.data[0].url
    except Exception as e:
        return None

def main():
    """Main function to run the Streamlit app"""
    # Streamlit UI
    st.title("📚 AI Study Guide Generator")
    st.markdown("Generate comprehensive study guides with summaries, key terms, and AI-generated diagrams")

    # Input text
    input_text = st.text_area(
        "Paste your study material here:",
        height=300,
        placeholder="Paste the text you want to convert into a study guide..."
    )

    if st.button("Generate Study Guide", type="primary"):
        if not input_text.strip():
            st.error("Please enter some text to generate a study guide.")
        else:
            with st.spinner("Analyzing content and generating study guide..."):
                try:
                    study_guide = generate_study_guide(input_text)
                    
                    # Display main title
                    st.markdown(f"# {study_guide['main_title']}")
                    st.markdown("---")
                    
                    # Display each section
                    for section in study_guide['sections']:
                        st.markdown(f"## {section['section_title']}")
                        
                        # Summary
                        with st.expander("📖 Summary", expanded=True):
                            st.write(section['summary'])
                        
                        # Bullet Takeaways
                        with st.expander("💡 Bullet Takeaways", expanded=True):
                            for takeaway in section['bullet_takeaways']:
                                st.markdown(f"• {takeaway}")
                        
                        # Key Terms - Display as chips/badges
                        with st.expander("🔑 Key Terms", expanded=True):
                            # Display as chips/badges
                            terms_html = " ".join([
                                f'<span style="display: inline-block; background-color: #e0e7ff; color: #4338ca; padding: 4px 12px; margin: 4px; border-radius: 12px; font-size: 14px;">{term}</span>' 
                                for term in section['key_terms']
                            ])
                            st.markdown(terms_html, unsafe_allow_html=True)
                        
                        # Quick Facts - Display as term: definition pairs
                        with st.expander("⚡ Quick Facts", expanded=True):
                            for fact_obj in section['quick_facts']:
                                st.markdown(f"**{fact_obj['term']}**: {fact_obj['definition']}")
                        
                        # Diagrams (if needed)
                        if section.get('needs_diagram', False):
                            with st.expander("📊 Diagram", expanded=True):
                                with st.spinner("Generating diagram..."):
                                    diagram_url = generate_diagram(section['diagram_description'])
                                    if diagram_url:
                                        st.image(diagram_url, caption=section['diagram_description'])
                                    else:
                                        st.warning("Could not generate diagram for this section.")
                        
                        st.markdown("---")
                    
                    st.success("✅ Study guide generated successfully!")
                    
                except json.JSONDecodeError:
                    st.error("Error parsing the study guide. Please try again.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()