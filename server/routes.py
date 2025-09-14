from flask import Blueprint, request, jsonify
from llm import run_llm_conversation
from classifier import classify
from llm import AVAILABLE_FUNCTIONS  # your db functions

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_message = data.get("message", "").strip()
    history = data.get("history", None)

    if not user_message:
        return jsonify({"reply": "Please type something."})

    # Try classifier first with confidence threshold
    intent, confidence = classify(user_message, threshold=0.8)
    print(intent, confidence)
    if intent:
        fn = AVAILABLE_FUNCTIONS.get(intent)
        if fn:
            try:
                # Very basic handling (you can parse better later)
                if intent == "db_get_product_by_id":
                    result = fn(product_id=1)
                elif intent == "db_search_products":
                    result = fn(query=user_message)
                elif intent == "db_get_inventory":
                    result = fn(product_id=1)  # placeholder
                else:
                    result = {"ok": False, "error": "Unhandled tool."}

                return jsonify({
                    "reply": str(result),
                    "source": "classifier",
                    "intent": intent,
                    "confidence": round(confidence, 3),
                })
            except Exception as e:
                pass  # fallback to LLM if tool call fails

    # Fallback: LLM
    reply = run_llm_conversation(user_message, history)
    return jsonify({"reply": reply, "source": "llm"})
