import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__, static_folder="static")
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/recommend", methods=["POST"])
def recommend():
    if not GEMINI_API_KEY:
        return jsonify({"error": "API key not configured on server."}), 500

    data = request.get_json()
    answers = data.get("answers", {})

    priorities = answers.get("priorities", "Not specified")
    if isinstance(priorities, list):
        priorities = ", ".join(priorities)

    prompt = f"""You are InsureWise AI — a warm, knowledgeable assistant that helps Americans navigate public health insurance programs. A user has shared the following about their situation:

- Currently has insurance: {answers.get("coverage", "Unknown")}
- Household size: {answers.get("household", "Unknown")}
- Children under 19 at home: {answers.get("kids", "Unknown")}
- Employment status: {answers.get("employment", "Unknown")}
- Monthly household income (before taxes): {answers.get("income", "Unknown")}
- Age group: {answers.get("age", "Unknown")}
- Military / veteran connection: {answers.get("military", "Unknown")}
- State: {answers.get("location", "Unknown")}
- Coverage priorities: {priorities}

Please respond with three clearly labeled sections using these exact headings:

**Programs You May Qualify For**
List 2–3 real public programs or plan types (e.g. Medicaid, CHIP, ACA Marketplace Silver plan, Medicare, VA Health). For each, write 1–2 sentences explaining in plain language WHY this person likely qualifies, and what it covers. Do not mention fake or made-up plan names.

**Your Action Checklist**
A short numbered list. What documents they need to gather (proof of income, residency, etc.) and exactly where to apply (give the real website or agency name, e.g. healthcare.gov, their state Medicaid agency).

**One Thing Most People Miss**
One sentence about a deadline, program rule, or tip that surprises people in this exact situation — like special enrollment windows, CHIP income thresholds being higher than Medicaid, or income change reporting rules.

Keep the tone friendly and clear. No jargon without explanation. End with: "Remember: this is guidance, not a guarantee — always verify with your state agency or healthcare.gov." """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(
        f"{GEMINI_URL}?key={GEMINI_API_KEY}",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    result = response.json()

    if "error" in result:
        return jsonify({"error": result["error"]["message"]}), 500

    text = result["candidates"][0]["content"]["parts"][0]["text"]
    return jsonify({"text": text})


if __name__ == "__main__":
    app.run(debug=True)
