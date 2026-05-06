import os
import logging
from flask import Flask, render_template, request, jsonify, session
from openai import OpenAI
from dotenv import load_dotenv

# --- CONFIGURATION INITIALE ---

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

app = Flask(__name__)
# Clé secrète indispensable pour utiliser les sessions (stockage de l'historique)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "une_cle_tres_secrete_123")

# Initialisation du client OpenAI
# La clé doit être dans ton fichier .env sous le nom OPENAI_API_KEY
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configuration des logs (pour voir les erreurs dans la console)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- LOGIQUE MÉTIER (LE CERVEAU DU CHEF) ---

def get_chef_ai_response(user_input: str, history: list) -> str:
    """
    Interagit avec l'API OpenAI pour générer une réponse de Chef Cuisinier.
    Inclut la gestion du personnage (System Prompt) et de la mémoire.
    """
    
    # Définition précise du rôle (Prompt Engineering)
    SYSTEM_INSTRUCTIONS = {
        "role": "system",
        "content": (
            "Tu es un Chef cuisinier étoilé, expert en gastronomie française et internationale. "
            "Tes règles de conduite : "
            "1. Réponds toujours avec enthousiasme et professionnalisme. "
            "2. Utilise des termes techniques (ex: 'brunoise', 'réduction', 'mijoter'). "
            "3. Structure tes recettes avec : Ingrédients (en liste) puis Étapes (numérotées). "
            "4. Utilise des émojis culinaires pour rendre la lecture agréable. "
            "5. Si l'utilisateur pose une question hors sujet, réponds poliment que tu ne peux "
            "parler que de cuisine et de saveurs."
        )
    }

    try:
        # Construction de la liste des messages (Système + Historique + Nouveau message)
        messages = [SYSTEM_INSTRUCTIONS]
        
        # On ajoute les 6 derniers messages de l'historique pour garder le contexte
        messages.extend(history[-6:])
        
        # On ajoute la nouvelle question de l'utilisateur
        messages.append({"role": "user", "content": user_input})

        # Appel à l'API avec le modèle performant gpt-4o-mini
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7, # Équilibre entre précision et créativité
            max_tokens=800   # Évite les réponses trop longues qui coupent
        )
        
        return completion.choices[0].message.content

    except Exception as e:
        logger.error(f"Erreur lors de l'appel OpenAI: {e}")
        return "Désolé, mes fourneaux sont en panne (erreur technique). Réessayez dans un instant ! 🍳"

# --- ROUTES FLASK ---

@app.route('/')
def index():
    """Affiche la page d'accueil et réinitialise la session de chat."""
    session['chat_history'] = []
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Route principale pour traiter les messages du chatbot."""
    
    # 1. Récupération et validation des données reçues
    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({"error": "Le message est vide"}), 400

    # 2. Initialisation de l'historique dans la session si vide
    if 'chat_history' not in session:
        session['chat_history'] = []

    # 3. Appel de la logique IA
    chef_response = get_chef_ai_response(user_message, session['chat_history'])

    # 4. Mise à jour de l'historique pour la mémoire du bot
    session['chat_history'].append({"role": "user", "content": user_message})
    session['chat_history'].append({"role": "assistant", "content": chef_response})
    
    # On limite la taille de la session pour ne pas ralentir le navigateur
    session['chat_history'] = session['chat_history'][-10:]
    session.modified = True # Force Flask à sauvegarder les changements

    # 5. Réponse envoyée au JavaScript du front-end
    return jsonify({
        "response": chef_response,
        "status": "success"
    })

# --- LANCEMENT DE L'APPLICATION ---

if __name__ == '__main__':
    # Le mode debug=True permet de voir les modifications sans relancer le serveur
    app.run(debug=True, port=5000)