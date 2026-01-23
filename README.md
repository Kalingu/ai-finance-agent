# AI Finance Agent – OCR & LLM-Driven Personal Finance Insights

This project implements a **full-stack AI-driven personal finance tool** that combines **receipt OCR**, **visual analytics**, and a **language model agent** to analyze and provide insights from expense data. Users can upload receipts, automatically extract totals, categorize expenses, visualize spending trends, and interact with a LLM agent for contextual financial queries.

*Role:* Contributor – implemented receipt OCR, Streamlit dashboard, and integrated LangGraph + LLaMA agent for expense analysis.

---

## Problem Statement

Managing personal expenses manually is tedious and error-prone. This project automates the workflow:

- Scan receipts using OCR
- Automatically detect totals and categorize expenses
- Visualize spending in charts and tables
- Use an LLM agent to analyze historical data and answer questions in natural language

It bridges **computer vision**, **data analytics**, and **applied AI/ML** in one real-world project.

---

## Tech Stack

- **Web UI:** Streamlit  
- **OCR:** EasyOCR + Pillow  
- **Data processing:** pandas, SQLite  
- **Visualization:** Plotly  
- **LLM/Agent:** LangGraph + LLaMA 3  
- **Notebook prototyping:** Jupyter Notebook  
- **Vector search & embeddings:** LangChain + FAISS

---

## Key Features

- Automatic extraction of receipt totals using OCR  
- Expense categorization & trend visualization  
- Natural language financial insights via LLM agent  
- CSV export for record keeping  
- Interactive Streamlit dashboard for real-time analysis

---

## Installation & Quick Start

Step 1: Clone the repository
```bash
git clone https://github.com/Kalingu/ai-finance-agent.git
cd ai-finance-agent
```
Step 2: Install dependencies
```bash
pip install -r requirements.txt
```
Step 3: Pull the local LLM using Ollama
```bash
ollama pull llama3.2:3b
```
Step 4: Run the Streamlit dashboard
```bash
streamlit run app.py
```
Step 5: Open the agent notebook for advanced analysis
```bash
jupyter notebook finance_agent.ipynb
```
