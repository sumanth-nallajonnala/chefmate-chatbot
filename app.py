from flask import Flask, render_template, request, jsonify
from chatbot import search_recipes_by_ingredients, parse_user_message

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please tell me what ingredients you have!"})

    ingredients, diet = parse_user_message(user_message)
    print(f"[PARSED] Ingredients: {ingredients} | Diet: {diet}")  # ← debug line

    if not ingredients:
        return jsonify({
            "reply": "I couldn't detect any ingredients. Try: 'I have chicken, garlic and tomatoes'"
        })

    recipes = search_recipes_by_ingredients(ingredients, diet=diet)

    if not recipes:
        return jsonify({
            "reply": f"No recipes found for: {', '.join(ingredients)}. The API may have no matches — try simpler ingredients like 'chicken, rice'."
        })

    return jsonify({
        "reply": f"Found {len(recipes)} recipe(s) using: {', '.join(ingredients)}!",
        "recipes": recipes,
        "diet": diet
    })

if __name__ == "__main__":
    app.run(debug=True)