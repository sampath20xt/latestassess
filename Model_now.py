import vertexai
from vertexai.generative_models import HarmCategory, HarmBlockThreshold
from vertexai.preview.generative_models import GenerativeModel
import textwrap
import os
import json


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "email-extraction-381718-3f73208ce3b71.json"
vertexai.init(project="email-extraction-381718", location="us-central1")
generative_multimodal_model = GenerativeModel("gemini-1.5-pro-001")


# Chunking function to handle large inputs
def chunk_text(text, token_limit=8192):
    chunks = textwrap.wrap(text, width=token_limit)
    return chunks

# Function to evaluate the spoken text using Vertex AI and Gemini model
def evaluate_text(choose_topic, spoken_text):
    prompt = f"""
        You are a highly experienced communication and soft skills trainer.
        The user was asked to read the following paragraph:
        "{choose_topic}"
        The user read the following transcribed speech:
        "{spoken_text}"
        evaluate the spoken texts with the original _text based on the following criteria:
        - Clarity of speech,Professionalism,Tone,Grammar,Vocabulary,Fluency,Coherence,Accuracy (matching the original paragraph) don't display this text
        evaluation must be in a line by line not in a table format and in a seperate  line for each criteria
        you have criteria name  in one line and it is explanation in another line and score in another line
        give a short explanation on why they lagging on each and every criteria with the marks for each criteria separately
        Give a score for overall performance out of 10 use the scores of each and every criteria to calculate and give the score  with explanation make it as Overall Performance
        provide detailed feedback on how they can improve their communication, reading accuracy, and English-speaking skills.
        give the feedback in two -three lines without confusion

        Please provide two separate sections in your evaluation:
        Criteria Evaluation: Provide feedback for each criterion separately (Clarity, Professionalism, etc.), with a score out of 10 and a brief explanation.
        Overall Performance: Summarize the user's overall performance, give an overall score, and provide advice on how they can improve.
        """
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.7,
        "top_p": 0.95,
    }
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }

    response = generative_multimodal_model.generate_content(prompt, generation_config=generation_config, safety_settings=safety_settings)
    return response.text


# prompt getting paragraphs for testing communication
def paragraphs(choose_topic):
    prompt = f"""
    you are well trained on different topics in the universe 
    you have to assign the paragraph as per the user choice that means based on "{choose_topic}"
    you have to generate paragraph which useful to the user to read for one minute to evaluate their communication skill
    you have to generate a basic paragraph which is useful to the user to read for 1 minute
    the paragraph is mainly useful to the user to test their communication
    the paragraph is must be different each time when your generating
    you have to give only the paragraph and avoid all  other things
    you have to generate the paragraph based upon the user choice 
    never ever ask a question in the paragraph just generate the paragraph as per the user choice
    for example if the user ask for movies you have to give origin and some related things
    you have to generate the paragraph to the user never ask questions in paragraph
    for example if the user ask for explain about kalki is a telugu movie then you have to explain about the movie story
    in that way you have to classify the topic and generate the paragraph to the user in a clear and confine way
    """
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.7,
        "top_p": 0.95,
    }
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }
    response = generative_multimodal_model.generate_content(prompt, generation_config=generation_config, safety_settings=safety_settings)
    return response.text


# Generate both skills and topics at once
def generate_skills_and_topics(title, job_designation, experience_range):
    prompt = f"""
        You are an expert in designing assessments for technical job roles.
        Suggest relevant skills needed for a {job_designation} with {experience_range} years of experience for a "{title}" assessment.
        For each skill, provide associated topics that can be tested in an assessment.
        The output should be a list of dictionaries where each dictionary contains a 'skill' and its respective 'topics'.
        Ensure that both technical and soft skills are included, and topics should cover both foundational and advanced areas.
        Format as a list of dictionaries, for example:
        [
            {{
                'skill': 'Skill 1',
                'topics': ['Topic 1', 'Topic 2']
            }},
            {{
                'skill': 'Skill 2',
                'topics': ['Topic 3', 'Topic 4']
            }}
        ]
        """
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.3,
        "top_p": 0.5,
    }
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }
    response = generative_multimodal_model.generate_content(prompt, generation_config=generation_config,
                                                            safety_settings=safety_settings)
    # Print the raw response for debugging
    print(f"Model response: {response.text}")
    try:
        cleaned_response = response.text.replace("```python", "").replace("```", "").strip()
        cleaned_response = cleaned_response.replace("'", '"')
        cleaned_response = cleaned_response.replace(",\n}", "\n}").replace(",\n]", "\n]")
        # Now use json.loads to safely parse the response
        skills_and_topics = json.loads(cleaned_response)
        return skills_and_topics
    except (json.JSONDecodeError, SyntaxError, ValueError) as e:
        # Log the error and return an empty list
        print(f"Error parsing model response: {e}")
        return []


# Retrieve topics for selected skills
def get_topics_for_selected_skills(selected_skills, skills_and_topics):
    topics = []
    for skill_dict in skills_and_topics:
        if skill_dict['skill'] in selected_skills:
            topics.extend(skill_dict['topics'])
    return topics


# Generate questions based on user requirements
def generate_questions(topics, question_type, difficulty_level, num_questions, additional_requirements):
    prompt = f"""
            You are an expert in designing assessments for technical job roles and also trained on different set of technical skills set.
            Your task is to generate the questions based on the given inputs like topic, type of the question, difficulty level of the question, number of the question to be generate.
            While generating the questions you should cover all the topics which are given in question.
            While generating the questions, the depth of the question should be based on the given difficulty level.
            Make the questions relevant to real-world challenges the candidate would face in the given role.

            For 'project' type questions, ensure that:
            - Each question should involve writing a program to solve a specific coding problem using the relevant skills.
            - Each question should present a Scenario related to real-world coding challenges that a developer might encounter.(e.g., data processing, optimization, full-stack features).
            - The Task should describe the problem to be solved with specific instructions for the code to be written.Such as algorithms, data structures, or design patterns to use.
            - Provide at least 3 Test Cases that will be used to validate the correctness of the solution. Each test case should include input data, expected output, and edge cases if applicable.
            Example format for project questions:
            - Scenario: A real-world coding problem where the candidate needs to write a full program.
            - Task: Clear and detailed instructions of what needs to be implemented (e.g., functions, classes, algorithms).
            - Test Cases: Provide at least 3 specific Test Cases that will be used to validate the solution. Each test case should include:
                - Input: The input data for the function or program.
                - Expected Output: The expected result from the function or program.
                - Executable Code: Provide Python code using `assert` statements to validate the test cases. Ensure the test cases cover:
                - Normal cases
                - Executable Code
                - Edge cases (e.g., empty input, boundary conditions)
                - Performance cases (e.g., large datasets for complexity evaluation)

            For 'mcq' type questions:
            - Provide a list of options for the question. Make sure not to use quotes (' or ") within the options.
            - Ensure the options cover different aspects of the topic and are diverse.

            For 'pseudo code' type questions:
            - Generate pseudo type of questions mainly focusing on coding and programming related to the topics. 
            - Based on the difficulty level generate the pseudo questions.

            For 'subjective' type questions:
            - Generate Subjective type of questions, A clear and open-ended question related to the topic.

            If the difficulty_level is 'easy', don't be too basic while generating the questions. 
            Ensure that the questions are diverse, testing both theoretical knowledge and practical problem-solving skills.
            While generating the questions, the depth of the question should be based on the given difficulty level.
            Make the questions relevant to real-world challenges the candidate would face in the given role.
            Include a mixture of basic and advanced scenarios, ensuring the difficulty is scaled as per the specified level.
            If the user gives any additional requirements, implement that while generating the questions.
            For 'MCQ' type of questions,The output should be a list of dictionaries which consist of question, options, and correct answer. 
            For 'project' type of questions,The output should be a list of dictionaries which consist of Scenario, Task and Test Cases.
            Make sure that the questions are relevant to the given topics and are programming-related.
            skills: {topics}
            question_type: {question_type}
            difficulty_level: {difficulty_level}
            no_of_question: {num_questions}
            Additional requirements: {additional_requirements}.
        """

    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.3,
        "top_p": 0.6,
    }
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }
    response = generative_multimodal_model.generate_content(prompt, generation_config=generation_config,
                                                            safety_settings=safety_settings)
    print(f"response: {response.text}")
    return response.text.replace("```", "").replace("json", "").replace("python", "")


def evaluate_answers(questions, answers):
    prompt = f"""
        You are an expert assessment evaluator. You need to evaluate the following answers for respective questions.
        The evaluation should be fair and consistent across all types of questions, including Subjective, MCQs, coding, or pseudo code-based ones.
        Just the output should be whether the answer is correct or not.
        If the answer is correct for the question, the output should be 'Correct Answer'. Otherwise, the output should be 'Incorrect Answer'.
        If the question type is pseudo code or subjective, focus on the logic of the answer:
         - Mark the answer as 'Correct Answer' if the logical structure and problem-solving approach are correct, even if there are differences in the function names, variable names, or the specific way the code is written.
         - Differences in the names of functions, variables, or even minor syntactical elements such as the placement of brackets, spacing, or indentation should not influence the evaluation.
         - Ensure that variations in programming style, structure, or presentation do not result in incorrect marking, as long as the logical flow and reasoning remain sound.
         - If the logic is only partially correct, mark it as 'Partial Correct Answer' and provide a clear explanation detailing what aspect of the logic is correct and what part is missing or incorrect. 
         - For pseudo code or coding questions, assess the use of algorithms, control structures, and overall problem-solving efficiency, while ignoring syntactical variations that do not impact the core logic.
         - For pseudo code,If the user answer is incorrect, Give the correct answer for the user question along with explanation
         - Be lenient with small syntactical errors or deviations in programming style that do not impact the understanding or correctness of the solution.
         - Focus on whether the user has demonstrated an understanding of the underlying problem, algorithms, and data structures needed to solve the question.

        The output should be a list of dictionaries for each question, with the following fields:
        questions: {questions}
        user_answers: {answers}
        correct_answer:
        evaluation: 
        The output should be a list of dictionaries with questions, user_answers, correct_answer, and evaluation. Don't wrap any text to the output.
        """
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.3,
        "top_p": 0.6,
    }
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }

    prompt_length = len(prompt)
    if prompt_length > 8192:
        chunks = chunk_text(prompt, token_limit=8192)
        evaluations = []
        for chunk in chunks:
            response = generative_multimodal_model.generate_content(chunk)
            evaluations.append(response.text.strip())
        return "\n".join(evaluations)
    else:
        response = generative_multimodal_model.generate_content(prompt, generation_config=generation_config,
                                                                safety_settings=safety_settings)
        return response.text.strip()

def validate_testCases(questions, answers, test_cases):
    prompt = f"""
    you are expert Evaluation Specialist who are evaluating the effectiveness of assessments and exams.
    And you are trained on Quality Assurance (QA) Engineer who are responsible for testing the various test cases and scenarios.
    your task is to evaluate the every given answer with question and test the given answer with given test cases.
    You have to test and evaluate the given answer with given various test cases and scenarios.
    If the answer passed in given test cases then the answer will be 'Passed'.
    If the answer failed in given any test cases then the answer will be 'Failed'.
    The output should be a list of dictionaries for rach question, with the following fields:
        questions: {questions}
        user_answers: {answers}
        test_cases:{test_cases}
        answer: 
    The output should be a list of dictionaries with questions, user_answers, test_cases, and answer. Don't wrap any text to the output.
    """
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.3,
        "top_p": 0.6,
    }
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }

    prompt_length = len(prompt)
    if prompt_length > 8192:
        chunks = chunk_text(prompt, token_limit=8192)
        evaluations = []
        for chunk in chunks:
            response = generative_multimodal_model.generate_content(chunk)
            evaluations.append(response.text.strip())
        return "\n".join(evaluations)
    else:
        response = generative_multimodal_model.generate_content(prompt, generation_config=generation_config,
                                                                safety_settings=safety_settings)
        return response.text.strip()