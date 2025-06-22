from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

@app.route('/submit-jobs', methods=['POST'])
def submit_jobs():
    job_data = request.get_json()
    print("Received job data:", job_data)
    return jsonify({"status": "success", "received": job_data})

if __name__ == '__main__':
    app.run(debug=True)
