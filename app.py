import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

# Chargement des variables d'environnement (.env)
load_dotenv()

app = Flask(__name__)

# Initialisation du client OpenAI (Version moderne)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message")
    
    if not user_input:
        return jsonify({"error": "Message vide"}), 400

    # Définition du rôle de ton Chef
    instructions = """
    Tu es un Chef cuisinier professionnel et passionné. 
    Ton rôle est d'aider les utilisateurs à cuisiner des plats délicieux.
    - Réponds toujours de manière polie et encourageante en français.
    - Donne des ingrédients précis et les étapes de préparation.
    - Utilise des émojis (👨‍🍳, 🍳, 🥗).
    - Si la question n'est pas culinaire, ramène gentiment l'utilisateur à la cuisine.
    """

    try:
        # Appel à l'API avec la syntaxe correcte pour la version actuelle
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": user_input}
            ]
        )
        
        bot_response = response.choices[0].message.content
        return jsonify({"response": bot_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)