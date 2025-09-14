from flask import Flask
from flask_cors import CORS
from routes import chat_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Register routes
app.register_blueprint(chat_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
