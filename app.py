import openai
import os
from flask import Flask, request, jsonify
from docx import Document
import PyPDF2

app = Flask(__name__)
openai.api_key = "YOUR_OPENAI_API_KEY"

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def analyze_resume(text, job_description):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI that analyzes resumes for job compatibility."},
            {"role": "user", "content": f"Job Description: {job_description}\nResume: {text}\nRate compatibility (0-100%) and provide feedback."}
        ]
    )
    return response["choices"][0]["message"]["content"]

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["resume"]
    job_description = request.form["job_description"]
    
    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(file)
    elif file.filename.endswith(".docx"):
        text = extract_text_from_docx(file)
    else:
        return jsonify({"error": "Unsupported file format"}), 400
    
    result = analyze_resume(text, job_description)
    return jsonify({"analysis": result})

if __name__ == "__main__":
    app.run(debug=True)
