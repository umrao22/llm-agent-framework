import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL
from db import db_get_product_by_id, db_search_products, db_get_inventory
import json
from datetime import date, datetime
from decimal import Decimal

client = Groq(api_key=GROQ_API_KEY)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "db_get_product_by_id",
            "description": "Fetch a single product by numeric ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer"}
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "db_search_products",
            "description": "Search products by name or description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "db_get_inventory",
            "description": "Check inventory (stock) for a product by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer"}
                },
                "required": ["product_id"]
            }
        }
    },
]

AVAILABLE_FUNCTIONS = {
    "db_get_product_by_id": db_get_product_by_id,
    "db_search_products": db_search_products,
    "db_get_inventory": db_get_inventory,
}

SYSTEM_PROMPT = (
    "You are a helpful retail assistant. "
    "When users ask about products, pricing, or stock, call the appropriate tools. "
    "Be concise, cite product names and prices from tool results, and avoid guessing. "
    "If a product is not found, say so. "
    "Never expose raw SQL or internal errors."
)

def safe_json_dumps(data):
    def default(o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, Decimal):
            return float(o)
        return str(o)  # fallback
    return json.dumps(data, ensure_ascii=False, default=default)

def log_training_example(query, tool_name):
    with open("training_data.csv", "a", encoding="utf-8") as f:
        f.write(f"{query}\t{tool_name}\n")

def run_llm_conversation(user_text: str, history: list[dict] | None = None) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_text})

    for _ in range(2):  # up to 2 tool-use rounds
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_completion_tokens=800,
            temperature=0.2,
        )
        msg = resp.choices[0].message
        tool_calls = getattr(msg, "tool_calls", None)

        if not tool_calls:
            return msg.content

        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [tc.model_dump() for tc in tool_calls],
        })

        for tc in tool_calls:
            fn_name = tc.function.name
            fn_args = json.loads(tc.function.arguments or "{}")
            fn = AVAILABLE_FUNCTIONS.get(fn_name)

            if not fn:
                tool_result = {"ok": False, "error": f"Unknown tool: {fn_name}"}
            else:
                try:
                    log_training_example(user_text, fn_name)
                    tool_result = fn(**fn_args)
                except Exception as e:
                    tool_result = {"ok": False, "error": f"Error: {str(e)}"}

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": fn_name,
                "content": safe_json_dumps(tool_result),
            })

    return "I couldn't complete that request with the available tools."
