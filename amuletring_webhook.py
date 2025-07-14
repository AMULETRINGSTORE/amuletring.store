from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "AMULET RING STORE Webhook is running!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        verify_token = "amuletring_token"  # ✅ ঠিক টোকেন এখানে দিন
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        print(f"GET Verification Attempt: mode={mode}, token={token}, expected={verify_token}")

        if mode and token:
            if mode == "subscribe" and token == verify_token:
                return challenge, 200
            else:
                return "Verification token mismatch", 403
    elif request.method == "POST":
        incoming_data = request.get_json()
        print("✅ Received message:", incoming_data)
        return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
