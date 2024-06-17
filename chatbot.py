import openai
import os
from flask import Flask, request, jsonify
from flask_ngrok import run_with_ngrok
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv('ENTER_YOUR_OPENAI_API_KEY')

# Knowledge base
knowledge_base = {
    "FAQs": [
        {
            "question": "What are your business hours?",
            "answer": "Our business hours are from 9 AM to 6 PM, Monday to Friday."
        },
        {
            "question": "How can I contact customer support?",
            "answer": "You can contact customer support via email at support@example.com or call us at 123-456-7890."
        }
    ],
    "Products": [
        {
            "name": "Product A",
            "description": "Product A is a high-quality item that offers great value.",
            "price": "$19.99"
        },
        {
            "name": "Product B",
            "description": "Product B is known for its excellent performance and durability.",
            "price": "$29.99"
        }
    ]
}

app = Flask(__name__)
run_with_ngrok(app) 

def search_knowledge_base(query):
    for category, items in knowledge_base.items():
        for item in items:
            if query.lower() in item.get('question', '').lower():
                return item['answer']
            if query.lower() in item.get('name', '').lower():
                return f"{item['description']} Price: {item['price']}"
    return None

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    response = search_knowledge_base(user_message)

    if not response:
        try:
            openai_response = openai.Completion.create(
                engine="text-davinci-003",  
                prompt=user_message,
                max_tokens=150
            )
            response = openai_response.choices[0].text.strip()
        except Exception as e:
            response = "I'm sorry, but I'm unable to assist with that query at the moment."

    return jsonify({"response": response})

@app.route('/')
def index():
    return """
<html>
<head>
    <title>Chatbot</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
        }
    </style>
    <script>
        async function sendMessage() {
            let userMessage = document.getElementById("userMessage").value;
            let response = await fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({message: userMessage})
            });
            let data = await response.json();
            document.getElementById("chatResponse").innerText = data.response;
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>Chatbot</h1>
        <input type="text" id="userMessage" placeholder="Type your message here">
        <button onclick="sendMessage()">Send</button>
        <p id="chatResponse"></p>
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    app.run()
