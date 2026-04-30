import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

# Chargement des variables d'environnement (.env)
load_dotenv()

app = Flask(__name__)

# Initialisation de l'API OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def index():
    # Afficher la page HTML principale
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message")
    
    if not user_input:
        return jsonify({"error": "Message vide"}), 400

    try:
        # Appel à l'API OpenAI (GPT-3.5 ou GPT-4)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un assistant utile et poli."},
                {"role": "user", "content": user_input}
            ]
        )
        # Récupération de la réponse
        bot_response = response.choices[0].message.content
        return jsonify({"response": bot_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)