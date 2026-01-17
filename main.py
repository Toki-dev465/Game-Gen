from flask import Flask, jsonify
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

app = Flask(__name__)

@app.route("/generate", methods=["GET"])
def generate_game():
    prompt = """
    Create a completely new, fun video game. Include:
    - Game name
    - Genre
    - Platform (Web)
    - Short 2-3 sentence description
    - One cool feature
    """
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        return jsonify({"game": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
