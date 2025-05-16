# 🌱 AI-Powered Farming Advisor System

Uses CrewAI multi-agent LLMs for crop-specific analysis:
- Soil & climate assessment
- Pest & disease recommendations
- Cost-benefit evaluation
- Final PDF report

## ✨ Features

- Multi-agent system using CrewAI
- Real-time weather integration via OpenWeatherMap
- Custom recommendations for crop health and farm economics
- Auto-generated farmer-friendly report in PDF format
- Clean, interactive Gradio interface

## 📝 Inputs

- Crop type (e.g., Maize)
- Region (e.g., Axum)
- Soil data (e.g., pH: 6.2, Nitrogen: medium)
- Farm size (e.g., 400 acres)

## 📤 Output

- Detailed advisory report in plain text
- Downloadable PDF version

## 🧰 Technologies Used

- Python
- Gradio (Web UI)
- FPDF (PDF generation)
- OpenWeatherMap API
- CrewAI (LLM agent framework)
- Groq API (LLM backend)


## 📄 Sample Output
[📥 Download PDF Report](examples/wheat-USA-report.pdf)

## 🚀 How to Run
1. Clone the repo:
   ```bash
   git clone https://github.com/yaekobB/farming-advisor-multi-agent-system.git
2. Add `.env` with your API keys
   ```bash
   GROQ_API_KEY=your_groq_api_key
   OPENWEATHER_API_KEY=your_openweather_api_key

3. Install requirements: 
   ```bash
   pip install -r requirements.txt
4. Run: 
   ```bash
   python farming_advisor_agent_code.py

