# 💰 AI Finance Agent (Streamlit + OCR + LLM)

AI-powered personal finance dashboard that:
- Reads receipt images with OCR
- Classifies spending by category
- Detects smart **TOTAL** amounts (not subtotals)
- Saves everything to a live dashboard with charts and CSV export
- Includes a separate **Finance Agent** notebook that analyzes a SQLite receipts database with Llama 3 and LangGraph.

## 🔧 Tech Stack

- Streamlit (interactive web UI)
- EasyOCR + Pillow + NumPy (receipt OCR)
- Pandas + Plotly (analytics + charts)
- SQLite (sample receipts database in notebook)
- LangGraph + LangChain + Llama 3 (agentic analysis, in `finance_agent.ipynb`)

## 📂 Repository Structure

- `app.py` – Streamlit app:
  - Upload receipts
  - Smart TOTAL detection
  - Category selection
  - Live dashboard (metrics + pie chart)
  - Editable recent transactions table with delete
  - Clean CSV export

- `finance_agent.ipynb` – Notebook agent:
  - Builds `receipts.db` with Sri Lankan LKR sample data
  - Tools to load expenses and build charts
  - Uses Llama 3 to summarize and give budget tips.[file:57]

## ▶️ How to Run the Streamlit App

```bash
# 1. Clone repo
git clone https://github.com/<your-username>/ai-finance-agent.git
cd ai-finance-agent

# 2. Create env (optional but recommended)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
