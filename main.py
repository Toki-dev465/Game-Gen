from flask import Flask, jsonify, request
from google import genai
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
from PIL import Image

load_dotenv()

app = Flask(__name__)
CORS(app)

client = genai.Client()

food_inventory = []

# --- MANUAL ADD ---
@app.route("/add", methods=["POST"])
def add_food():
    data = request.json
    item = data.get("item", "").strip()
    expiry = data.get("expiry")  # optional
    if item:
        food_inventory.append({"name": item, "expiry": expiry})
    return jsonify({"inventory": food_inventory})

# --- CLEAR INVENTORY ---
@app.route("/clear", methods=["POST"])
def clear_inventory():
    food_inventory.clear()
    return jsonify({"inventory": food_inventory})

# --- GEMINI SCAN IMAGE ---
@app.route("/scan", methods=["POST"])
def scan_food():
    try:
        file = request.files['image']
        img = Image.open(file)

        prompt = """
        Analyze this image of a food product.
        Extract the product name and expiry date.
        Return ONLY a JSON object like:
        {"name": "Product Name", "expiry": "YYYY-MM-DD"}
        If you can't find a date, return null for expiry.
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([prompt, img])
        
        cleaned_text = response.text.replace("```json","").replace("```","")
        data = json.loads(cleaned_text)
        
        food_inventory.append(data)
        return jsonify({"item": data, "inventory": food_inventory})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- GEMINI MEAL SUGGESTION ---
@app.route("/suggest", methods=["GET"])
def suggest_meals():
    if not food_inventory:
        return jsonify({"suggestion": "Your fridge is empty!"})
    
    ingredients = [f"{i['name']}" for i in food_inventory]
    prompt = f"""
    I have these ingredients: {', '.join(ingredients)}.
    Suggest 3 simple meals I can cook.
    Keep it short and simple.
    Return plain text.
    """
    try:
        response = client.models.generate_content(
            model="gemini-3-flash",
            contents=prompt
        )
        return jsonify({"suggestion": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
