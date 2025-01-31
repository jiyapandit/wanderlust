# app.py
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
import os
import json
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# Chat history storage (for persistence)
CHAT_HISTORY_FILE = "chat_history.json"

def get_gemini_response(user_input):
    prompt = f"""Act as an expert travel planner. For: {user_input}
    
    Provide structured response with:
    - Itinerary with time slots
    - Places with entry fees & duration
    - Budget breakdown
    - Travel tips
    - Total cost & time
    
    Use Markdown formatting with clear sections."""

    try:
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text'):
            return response.text
        else:
            return "⚠️ Error: No response generated from Gemini API."
    except Exception as e:
        print(f"Error in get_gemini_response: {e}")  # Debugging output
        return f"⚠️ Error: {str(e)}"

# def get_gemini_response(user_input):
#     prompt = f"""Act as an expert travel planner. For: {user_input}
    
#     Provide structured response with:
#     - Itinerary with time slots
#     - Places with entry fees & duration
#     - Budget breakdown
#     - Travel tips
#     - Total cost & time
    
#     Use Markdown formatting with clear sections."""
    
#     try:
#         response = model.generate_content(prompt)
#         return response.text
#     except Exception as e:
#         return f"Error: {str(e)}"

def save_chat_history(user_id, data):
    try:
        history = load_chat_history()
        history[user_id] = data
        with open(CHAT_HISTORY_FILE, 'w') as f:
            json.dump(history, f)
    except Exception as e:
        print(f"Error saving history: {str(e)}")

def load_chat_history():
    try:
        with open(CHAT_HISTORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data['message']
        user_id = data.get('user_id', 'default')
        
        # Get response
        bot_response = get_gemini_response(user_message)
        
        # Save to history
        history = load_chat_history()
        user_history = history.get(user_id, [])
        user_history.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_message,
            'bot': bot_response
        })
        save_chat_history(user_id, user_history)
        
        return jsonify({'response': bot_response})
    
    except Exception as e:
        return jsonify({'response': f"Error: {str(e)}"})

@app.route('/history/<user_id>', methods=['GET'])
def get_history(user_id):
    try:
        history = load_chat_history()
        return jsonify(history.get(user_id, []))
    except:
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)