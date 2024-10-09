from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import csv
import json

app = Flask(__name__)
CORS(app)  # This will allow requests from any origin by default

# Define the directory where the uploaded video will be saved
UPLOAD_FOLDER = 'user_videos'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Define allowed video file extensions
ALLOWED_EXTENSIONS = {'webm'}

# Check if the uploaded file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Save responses to a CSV file
def save_responses(user_id, answers):
    answers_list = json.loads(answers)  # Parse JSON string into a Python list
    file_exists = os.path.isfile("responses.csv")
    with open("responses.csv", mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["User ID", "Answers"])
        writer.writerow([user_id, answers_list])

@app.route('/submission', methods=['POST'])
def handle_submission():
    try:
        # Get the answers and user ID from the form
        user_id = request.form.get('user_id')
        answers = request.form.get('answers')
        if not answers or not user_id:
            return jsonify({"error": "No answers or user ID provided"}), 400

        # Get the uploaded video file
        if 'video' not in request.files:
            return jsonify({"error": "No video file provided"}), 400

        video = request.files['video']

        # Check if the file is valid and allowed
        if video and allowed_file(video.filename):
            video_filename = os.path.join(UPLOAD_FOLDER, f"{user_id}_video.webm")
            video.save(video_filename)  # Save the video to the uploads folder
        else:
            return jsonify({"error": "Invalid video file"}), 400

        # Save the responses with the user ID
        save_responses(user_id, answers)

        # Respond with success message
        return jsonify({
            "message": "Submission received successfully",
            "answers": answers,
            "video_path": video_filename
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
