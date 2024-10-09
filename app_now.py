import ast
import csv
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

from Model_now import generate_skills_and_topics, get_topics_for_selected_skills, evaluate_answers, generate_questions, validate_testCases

if "questions" not in st.session_state:
    st.session_state['questions'] = []

if "topics" not in st.session_state:
    st.session_state['topics'] = []

def save_test_cases_to_csv(test_cases, file_name='testcases.csv'):
    df = pd.DataFrame(test_cases)
    df.to_csv(file_name, index=False)
    print(f"Test cases saved to {file_name}")

def create_html_form(questions):

    html_form = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Online Assessment</title>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
            <style>
                body {
                    background-color: #f4f4f9;
                }
                .container {
                    margin-top: 150px;
                    padding: 20px;
                    background: white;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }
                h1 {
                    text-align: center;
                    margin-bottom: 20px;
                }
                .question {
                    margin-bottom: 60px;
                }
                .btn-submit {
                    width: 100%;
                    margin-top: 20px;
                }
                .scenario, .task {
                    font-style: italic; /* Make the scenario and task distinct */
                }
            </style>
        </head>
        <body>

        <div class="container">
            <h1>Online Assessment</h1>
            <form id="quiz-form">
    """

    # Add user ID field
    html_form += f"<div class='form-group'><label for='user_id'>User ID:</label>\n"
    html_form += f"<input type='text' class='form-control' id='user_id' name='user_id' required><br>\n</div>"

    # Loop through the questions and infer the type if missing
    for i, question in enumerate(questions):
        question_type = question.get('type')

        # Attempt to infer type based on the structure if 'type' is missing
        if not question_type:
            if 'options' in question:
                question_type = 'mcq'
            elif 'Scenario' in question and 'Task' in question:
                question_type = 'project'  # Has scenario/task fields, so it's a project type
            else:
                question_type = 'subjective'  # Default to subjective

        # Generate HTML form elements based on inferred or actual type
        if question_type == 'mcq' and 'options' in question:
            question_text = question.get('question', f"Question {i + 1} not provided")
            # Generate MCQ
            html_form += f"<div class='question'><label>Q{i + 1}: {question_text}</label><br>"
            for option in question['options']:
                html_form += f"<div class='form-check'><input type='radio' class='form-check-input' name='Q{i + 1}' value='{option}' required> <label class='form-check-label'>{option}</label></div>\n"
            html_form += "</div>"

        elif question_type == 'project':
            print("Project")
            scenario = question.get('Scenario', 'Scenario not provided')
            task = question.get('Task', 'Task not provided')
            # html_form += f"<div class='question'><label><strong>Q{i + 1}: {question_text}</strong></label><br>
            html_form += f"<div class='scenario'><label>Question</strong>{i + 1}: Scenario: {scenario} <br>"
            html_form += f"<div class='task'><label>Task:</strong>{task}<br>"
            html_form += f"<textarea class='form-control' name='Q{i + 1}' rows='4' placeholder='Your response...' required></textarea><br></div></div>"

        elif question_type in ['subjective', 'pseudo_code']:
            # Generate a text area for subjective or code questions
            html_form += f"<div class='question'><label>Q{i + 1}: {question_text}</label><br>"
            html_form += f"<textarea class='form-control' name='Q{i + 1}' rows='4' placeholder='Your response...' required></textarea><br></div>"

        else:
            # Fallback case for unknown types
            html_form += f"<div class='question'><label>Q{i + 1}: {question_text}</label><br>"
            html_form += f"<textarea class='form-control' name='Q{i + 1}' rows='4' required></textarea><br></div>"

    # Add proctoring video and timer controls
    html_form += """    
        <div class="form-group">
            <label>Proctoring Video Stream:</label>
            <video id="camera-stream" width="320" height="240" autoplay muted></video>
            <p id="microphone-status" class="text-success">Microphone: Active</p>
        </div>

        <button type="submit" class="btn btn-primary btn-submit" id="submit-button">Submit</button>
        <p id="timer" class="text-danger">Time left: <span id="time">60</span> seconds</p>
    </form>

        <div id="success-message" style="display: none;">
            <h3 class="text-success">You have successfully finished the test, now you can close the window.</h3>
        </div>
    </div>

    <script>
        // JavaScript code for proctoring and auto-submit functionality
        let mediaRecorder;
        let recordedChunks = [];
        let videoStream;
        let audioStream;

        let timeLeft = 300; // Timer set
        const timerDisplay = document.getElementById("time");
        const timerInterval = setInterval(() => {
            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                stopRecording();
                document.getElementById('quiz-form').submit(); // Auto-submit when time is up
            } else {
                timerDisplay.textContent = timeLeft;
                timeLeft--;
            }
        }, 1000);

        function startCamera() {
            const video = document.getElementById('camera-stream');
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                navigator.mediaDevices.getUserMedia({ video: true, audio: true })
                    .then(function(stream) {
                        videoStream = stream;
                        video.srcObject = stream;
                        mediaRecorder = new MediaRecorder(stream);
                        mediaRecorder.ondataavailable = function(event) {
                            if (event.data.size > 0) {
                                recordedChunks.push(event.data);
                            }
                        };
                        mediaRecorder.start();
                    })
                    .catch(function(error) {
                        alert("Camera or Microphone access denied.");
                    });
            }
        }

        function startMicrophone() {
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(function(stream) {
                    audioStream = stream;
                    document.getElementById('microphone-status').textContent = "Microphone: Active";
                })
                .catch(function(error) {
                    alert("Microphone access denied.");
                });
        }

        function stopMediaStreams() {
            if (videoStream) {
                videoStream.getTracks().forEach(track => track.stop());
            }
            if (audioStream) {
                audioStream.getTracks().forEach(track => track.stop());
            }
        }

        function stopRecording() {
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
            }
        }

        function handleSubmit(event) {
            event.preventDefault();
            stopRecording();
            stopMediaStreams();

            const formData = new FormData();
            const answers = [];

            const questions = document.querySelectorAll('.question');
            questions.forEach((question, index) => {
                const selectedAnswer = question.querySelector('input[type="radio"]:checked, textarea');
                if (selectedAnswer) {
                    answers.push(selectedAnswer.value);
                }
            });

            const userId = document.getElementById('user_id').value;
            formData.append('user_id', userId);
            formData.append('answers', JSON.stringify(answers));

            setTimeout(() => {
                if (recordedChunks.length > 0) {
                    const recordedBlob = new Blob(recordedChunks, { type: 'video/webm' });
                    formData.append('video', recordedBlob, 'proctoring_video.webm');

                    fetch('http://127.0.0.1:8000/submission', {
                        method: 'POST',
                        body: formData,
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.message === "Submission received successfully") {
                            document.getElementById('quiz-form').style.display = 'none';
                            document.getElementById('camera-stream').style.display = 'none';
                            document.getElementById('success-message').style.display = 'block';
                        } else {
                            alert("Submission failed. Please try again.");
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
                } else {
                    console.error('Error: No recorded chunks found.');
                    alert('Submission failed. Please try again.');
                }
            }, 1000);
        }

        window.onload = function() {
            startCamera();
            startMicrophone();
        };

        document.getElementById('quiz-form').addEventListener('submit', handleSubmit);
    </script>

    </body>
    </html>"""

    return html_form


def details():
    title = st.text_input("Title of Assessment", "")
    job_designation = st.text_input("Job Designation", "")
    experience_range = st.number_input("Experience Range (in years)", min_value=0, step=1)

    if st.button("Generate Skills"):
        if title and job_designation and experience_range:
            skills_suggestion = generate_skills_and_topics(title, job_designation, experience_range)
            # st.write(skills_suggestion)
            st.session_state['skills_topics'] = skills_suggestion  # Store suggested skills in session state
            st.success("Generated skills")
        else:
            st.warning("Please fill out all fields before proceeding.")


def assessment():
    if 'skills_topics' in st.session_state:
        skills = [skill['skill'] for skill in st.session_state['skills_topics']]
        selected_skills = st.multiselect("Select skills you want", skills)
        if selected_skills:
            st.write(f"Selected Skills: {', '.join(selected_skills)}")
        else:
            st.warning("Please select at least one skill.")
    else:
        st.warning("Please go to the previous step and generate skills first.")

    if st.button("Recommended Topic"):
        if selected_skills:
            topic_distribution = get_topics_for_selected_skills(selected_skills, st.session_state['skills_topics'])
            st.session_state['topics'] = topic_distribution
            st.write(topic_distribution)
            st.success("Generated Topics")
        else:
            st.warning("Please select skills you want")

    else:
        topic_distribution = get_topics_for_selected_skills(selected_skills, st.session_state['skills_topics'])
        st.session_state['topics'] = topic_distribution

    question_type = st.selectbox("Question Type", ["Subjective", "Pseudo code", "MCQ","Project"])
    difficulty_level = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"])
    num_questions = st.number_input("Number of Questions", min_value=1, step=1)
    additional_requirements = st.text_area("Additional Requirements (optional)", "")
    topics = st.session_state['topics']

    if st.button("Generate Assessment Questions"):
        if num_questions > 0 and selected_skills:
            questions = generate_questions(topics, question_type, difficulty_level, num_questions,
                                           additional_requirements)
            questions = ast.literal_eval(questions)
            save_test_cases_to_csv(questions,'testcases.csv')
            st.session_state['questions'] = questions  # Store questions in session state
            st.success("Questions generated successfully!")


def html_form():
    if 'questions' in st.session_state:
        questions = st.session_state['questions']
        html_form = create_html_form(questions)
        st.download_button(label="Download HTML Form", data=html_form, file_name="assessment_form.html",
                           mime="text/html")
    else:
        st.warning("Please generate the assessment first.")


def evaluation():
    st.header("Evaluation")

    if 'questions' in st.session_state:
        question = st.session_state['questions']

    user_id = st.text_input("Enter User ID")  # User ID input for evaluation
    found = False

    if st.button("Evaluate"):
        if user_id:
            with st.spinner("Processing responses..."):
                st.write("### Responses")

                with open('responses.csv', 'r') as csvfile:
                    reader = csv.reader(csvfile)
                    data = list(reader)

                # Search for responses with matching user_id
                for row in data:
                    if row[0] == str(user_id):
                        opt = ast.literal_eval(row[1])
                        while len(opt) < len(question):
                            opt.append('')  # Ensure all questions are covered
                        found = True
                        break

                if found:
                    # Display each question with the corresponding user answer
                    for i, value in enumerate(opt):
                        question[i]['user_answer'] = value
                    print(question)
                    if question[0]['options']:  # For multiple-choice questions
                        for i, ques in enumerate(question):
                            st.write(f"**Question {i + 1}:** {ques['question']}")
                            st.write(f"**User Answer:** {ques['user_answer']}")
                            st.write(f"**Correct Answer:** {ques['correct_answer']}")
                            st.write("---")
                        myscore = sum([1 for x in question if x['user_answer'] == x['correct_answer']])
                        st.write(f"Your score: {myscore} out of {len(question)}")

                    elif question[0]['Scenario']:
                        questions = [q['question'] for q in question]
                        print(questions)
                        answers = [q['user_answer'] for q in question]
                        print(answers)
                        test_cases = [q['Test Cases'] for q in question]
                        print(test_cases)
                        if answers:
                            validation = validate_testCases(questions,answers,test_cases)
                            response = ast.literal_eval(validation)

                            for i,ques in enumerate(response):
                                st.write(f"**Question {i + 1}:** {ques['questions']}")
                                st.write(f"**User Answer:** {ques['user_answers']}")
                                st.write(f"**Test Cases:** {ques['test_cases']}")
                                st.write(f"**Answer:** {ques['answer']}")
                                st.write("---")
                            myscore = sum([5 for x in response if x['answer'] == "Passed"])
                            st.write(f"Your score: {myscore} out of {len(response) * 5}")
                        else:
                            st.warning("Please answer all questions before submitting.")

                    else:  # For subjective or pseudo code questions
                        questions = [q['question'] for q in question]
                        print(questions)
                        answers = [q['user_answer'] for q in question]
                        print(answers)

                        if answers:
                            evaluation = evaluate_answers(questions, answers)
                            st.write("Evaluation Results:")
                            response = ast.literal_eval(evaluation)
                            print(response)

                            for i, ques in enumerate(response):
                                st.write(f"**Question {i + 1}:** {ques['questions']}")
                                st.write(f"**User Answer:** {ques['user_answers']}")
                                st.write(f"**Correct Answer:** {ques['correct_answer']}")
                                st.write(f"**Evaluation:** {ques['evaluation']}")
                                st.write("---")

                            myscore = sum([5 for x in response if x['evaluation'] == "Correct Answer"])
                            st.write(f"Your score: {myscore} out of {len(response) * 5}")
                        else:
                            st.warning("Please answer all questions before submitting.")
                else:
                    st.warning(f"No responses found for User ID: {user_id}")

            video_file = open(f"user_videos/{user_id}_video.webm", "rb")
            video_bytes = video_file.read()

            DEFAULT_WIDTH = 40

            width = max(DEFAULT_WIDTH, 0.01)
            side = max((100 - width) / 2, 0.01)

            _, container, _ = st.columns([side, width, side])
            container.video(data=video_bytes)

        else:
            st.warning("Please enter a valid User ID.")


def main():
    st.set_page_config(
        page_title="Assessment Generator",
        page_icon=":page_with_curl:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    choice = option_menu(None, ["Assessment Details & Skills", "Generate Assessment", "Export HTML Form", "Evaluation",
                                "Speech Evaluation"],
                         icons=["briefcase", "pencil", "download", "clipboard", "mic"],
                         menu_icon="cast", default_index=0, orientation="horizontal",
                         styles={
                             "container": {"background-color": "#bedff9", "border-radius": "10px,"},
                             "icon": {"color": "black"},
                             "nav-link": {"color": "black", "--hover-color": "#7ebbfb", "border-radius": "5px"},
                             "nav-link-selected": {"background-color": "#68a8ec", "border-radius": "px"},
                         })

    if choice == "Assessment Details & Skills":
        details()
    elif choice == "Generate Assessment":
        assessment()
    elif choice == "Export HTML Form":
        html_form()
    elif choice == "Evaluation":
        evaluation()


if __name__ == "__main__":
    main()