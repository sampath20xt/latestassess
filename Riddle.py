import streamlit as st
import vertexai
from vertexai.generative_models import HarmCategory, HarmBlockThreshold
from vertexai.preview.generative_models import GenerativeModel
import os
import json
import regex as re
from streamlit_extras.let_it_rain import rain

# Initialize Vertex AI
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "email-extraction-381718-3f73208ce3b71.json"
vertexai.init(project="email-extraction-381718", location="us-central1")
generative_multimodal_model = GenerativeModel("gemini-1.5-pro-001")

# Streamlit interface
st.title("Programming Riddle Game")

# Input from the user
Topic = st.text_input("Enter a programming-related Topic:")

# Function to generate 10 riddles with answers in JSON format
def generate_riddles(Topic):
    prompt = f"""
    You are an Expert that can determine whether a given topic is programming-related or not. 
    Check if the following topic is related to programming: "{Topic}". 
    If it is programming-related, generate 10 funny riddles along with their answers in JSON format. 
    The riddles should be engaging and appropriate for an audience familiar with programming concepts. 
    Provide the output in the following JSON structure:

    [
      {{
        "riddle": "Riddle 1",
        "answer": "Answer 1"
      }},
      {{
        "riddle": "Riddle 2",
        "answer": "Answer 2"
      }},
      ...
      {{
        "riddle": "Riddle 10",
        "answer": "Answer 10"
      }}
    ]

    If the topic is not programming-related, respond with "Please select programming-related topics."
    """

    # Generation configuration and safety settings
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.6,
        "top_p": 0.5,
    }

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }

    response = generative_multimodal_model.generate_content(
        prompt,
        generation_config=generation_config,
        safety_settings=safety_settings
    )

    print(response.text)  # Debugging: Print the raw AI response

    # Extract the JSON part from the response
    json_string = re.search(r"\[.*\]", response.text, re.DOTALL)

    if json_string:
        try:
            return json.loads(json_string.group(0))  # Safely load JSON data
        except json.JSONDecodeError as e:
            st.error("Error decoding JSON: " + str(e))
            return None
    else:
        st.error("No valid JSON found in the response.")
        return None


# Store riddles and progress in session state
if Topic and st.button("Generate Riddles"):
    riddle_data = generate_riddles(Topic)
    if riddle_data:
        st.session_state.riddles = riddle_data
        st.session_state.current_riddle = 0
        st.session_state.user_attempts = 0
        st.session_state.show_next_button = False
        st.session_state.answer_input = ""  # Initialize answer input for the first riddle

# Function to get the next riddle
def get_next_riddle():
    current = st.session_state.current_riddle
    if current < len(st.session_state.riddles):
        return st.session_state.riddles[current]["riddle"]
    else:
        return None


# Check if riddles have been generated
if "riddles" in st.session_state:
    # Display the current riddle
    current_riddle = get_next_riddle()

    if current_riddle:
        st.write(f"Riddle: {current_riddle}")

        # Initialize the input field value based on session state
        user_answer = st.text_input("What's your answer?", value=st.session_state.answer_input, key="answer_input")

        # Submit button for user's answer
        if st.button("Submit Answer"):
            correct_answer = st.session_state.riddles[st.session_state.current_riddle]["answer"]

            # Check the user's answer
            if user_answer.lower() == correct_answer.lower():
                st.success("Correct Answer!")
                rain(emoji="❄️", font_size=54, falling_speed=5, animation_length="infinite")
                st.session_state.show_next_button = True
            else:
                st.error("Wrong Answer! Try again.")
                rain(emoji="🔥", font_size=54, falling_speed=5, animation_length="infinite")

        # Show "Go to Next Question" button if the answer was correct
        if st.session_state.show_next_button:
            if st.button("Go to Next Question"):
                st.session_state.current_riddle += 1
                st.session_state.show_next_button = False
                st.session_state.answer_input = ""  # Clear input for the next riddle

        # Show "Try Again" button if the answer was wrong
        if st.button("Try Again"):
            st.session_state.answer_input = user_answer  # Retain the last answer input
            st.session_state.user_attempts += 1  # Increment attempts

    else:
        st.write("🎉 You've answered all riddles!")
        st.balloons()
