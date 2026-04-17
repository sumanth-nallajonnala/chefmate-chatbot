import requests
import os
import re
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("SPOONACULAR_API_KEY")
BASE_URL = "https://api.spoonacular.com"

def parse_user_message(message):
    """Properly extract ingredients and diet from user message."""
    original = message.lower()

    # Detect diet preference
    diet = None
    diet_keywords = ["vegan", "vegetarian", "gluten-free", "dairy-free"]
    for keyword in diet_keywords:
        if keyword in original:
            diet = keyword
            break

    # Remove diet keywords from message before ingredient extraction
    cleaned = original
    for d in diet_keywords:
        cleaned = cleaned.replace(d, "")

    # Remove filler phrases (whole words/phrases only, NOT substrings)
    filler_phrases = [
        "i have", "i've got", "i got", "using", "can you", "please",
        "make something", "make me", "cook something", "cook me",
        "suggest a recipe", "suggest recipes", "what can i make",
        "with these", "i want", "something", "help me", "recipe with",
        "ingredients are", "ingredients:", "i need", "make", "cook",
        "recipe", "food", "dish", "meal", "prepare", "using these"
    ]
    for phrase in filler_phrases:
        cleaned = re.sub(r'\b' + re.escape(phrase) + r'\b', ' ', cleaned)

    # Remove punctuation except hyphens (for things like "gluten-free")
    cleaned = re.sub(r'[^\w\s-]', ' ', cleaned)

    # Split on spaces, commas, "and", "or"
    tokens = re.split(r'[\s,]+', cleaned)

    # Filter: keep only meaningful words (not stop words, not single chars)
    stop_words = {
        "and", "or", "the", "a", "an", "i", "me", "my", "some",
        "any", "have", "has", "with", "for", "of", "in", "on",
        "it", "is", "are", "be", "to", "do", "can", "get", "want"
    }

    ingredients = []
    for token in tokens:
        token = token.strip("-").strip()
        if token and len(token) > 2 and token not in stop_words:
            ingredients.append(token)

    # Deduplicate while preserving order
    seen = set()
    unique_ingredients = []
    for ing in ingredients:
        if ing not in seen:
            seen.add(ing)
            unique_ingredients.append(ing)

    return unique_ingredients, diet


def search_recipes_by_ingredients(ingredients, diet=None, number=5):
    url = f"{BASE_URL}/recipes/findByIngredients"
    params = {
        "ingredients": ",".join(ingredients),
        "number": number,
        "ranking": 1,
        "ignorePantry": True,
        "apiKey": API_KEY
    }
    response = requests.get(url, params=params)
    print(f"[API] findByIngredients status: {response.status_code}")
    print(f"[API] URL called: {response.url}")

    if response.status_code != 200:
        print(f"[API ERROR] {response.text}")
        return []

    recipes = response.json()
    print(f"[API] Raw recipes found: {len(recipes)}")

    result = []
    for r in recipes:
        details = get_recipe_details(r["id"], diet)
        if details:
            result.append(details)
        if len(result) >= 3:  # limit to 3 to save API calls
            break

    return result


def get_recipe_details(recipe_id, diet=None):
    url = f"{BASE_URL}/recipes/{recipe_id}/information"
    params = {"apiKey": API_KEY, "includeNutrition": True}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"[API ERROR] Recipe detail failed: {response.status_code}")
        return None

    data = response.json()

    # Apply dietary filter
    if diet:
        diet_map = {
            "vegan": data.get("vegan", False),
            "vegetarian": data.get("vegetarian", False),
            "gluten-free": data.get("glutenFree", False),
            "dairy-free": data.get("dairyFree", False),
        }
        if not diet_map.get(diet.lower(), True):
            return None

    return {
        "id": data["id"],
        "title": data["title"],
        "image": data.get("image", ""),
        "readyInMinutes": data.get("readyInMinutes", "N/A"),
        "servings": data.get("servings", "N/A"),
        "sourceUrl": data.get("sourceUrl", "#"),
        "vegan": data.get("vegan", False),
        "vegetarian": data.get("vegetarian", False),
        "glutenFree": data.get("glutenFree", False),
        "dairyFree": data.get("dairyFree", False),
        "nutrition": extract_nutrition(data),
    }


def extract_nutrition(data):
    nutrients = {}
    try:
        for n in data["nutrition"]["nutrients"]:
            if n["name"] in ["Calories", "Protein", "Carbohydrates", "Fat"]:
                nutrients[n["name"]] = f"{round(n['amount'])} {n['unit']}"
    except:
        pass
    return nutrients