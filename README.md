# 🧠 AI Retail Agent  

An AI-powered retail assistant that answers product-related queries by calling database functions (tools) and returning clear, human-friendly answers.  
It combines:  

- **LLM agent (Groq API)** for natural language understanding and tool orchestration  
- **Custom tools** for product lookup, search, and inventory checking  
- **Classifier (TF-IDF + Logistic Regression)** for predicting the best tool upfront, improving efficiency  

---

## ✨ Features  
- 🔌 Connects to your product database  
- 🛠️ Tools for:  
  - Get product by ID  
  - Search products by name/description  
  - Check product inventory  
- 🧠 Smart tool calling via LLM with Groq API  
- 📚 Classifier to pre-route queries with confidence thresholds  
- 🗂️ Logs training data for continuous improvement  
- 🛡️ Safe JSON serialization (handles dates, decimals, etc.)  

---
