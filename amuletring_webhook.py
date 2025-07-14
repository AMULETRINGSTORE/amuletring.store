from flask import Flask, request, jsonify
import openai
import os
import requests

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "AMULET RING STORE Webhook is running!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        verify_token = "amuletring.store"
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode and token:
            if mode == "subscribe" and token == verify_token:
                return challenge, 200
            else:
                return "Verification token mismatch", 403

    elif request.method == "POST":
        incoming_data = request.get_json()
        print("📥 Received message:", incoming_data)

        try:
            # Extract incoming message details
            message = incoming_data['entry'][0]['changes'][0]['value']['messages'][0]
            user_msg = message['text']['body']
            from_number = message['from']
            phone_number_id = incoming_data['entry'][0]['changes'][0]['value']['metadata']['phone_number_id']

            # Get reply from ChatGPT
            gpt_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_msg}]
            )
            reply_text = gpt_response['choices'][0]['message']['content']

            # Send WhatsApp reply
            url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
                "Content-Type": "application/json"
            }
            payload = {
                "messaging_product": "whatsapp",
                "to": from_number,
                "type": "text",
                "text": {"body": reply_text}
            }
            response = requests.post(url, headers=headers, json=payload)
            print("📤 Sent reply:", response.text)

        except Exception as e:
            print("❌ Error:", str(e))

        return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
