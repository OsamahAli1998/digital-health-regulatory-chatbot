# Digital Health Regulatory Chatbot
A conversational AI chatbot that helps SMEs in Sweden identify which EU and Swedish regulations may apply to their digital health products. Built with Streamlit and Google Gemini AI.

## Project Structure

```
├── README.md
├── app.py
├── data
│   ├── questions.json
│   └── regulations.json
├── logic
│   ├── __pycache__
│   │   └── decision_engine.cpython-311.pyc
│   └── decision_engine.py
├── requirements.txt
└── style.css
```

## Installation

1. Clone the repository:
```bash
git clone git@gitlab.lnu.se:oa222sv/digital-health-regulatory-chatbot.git
cd digital-health-regulatory-chatbot
```


2. Install dependencies 

```bash
pip install -r requirements.txt
```

## Environment Variables
Create a .env file in the root directory with the following:

```bash
GOOGLE_API_KEY=your_api_key_here
```


3. Usage

#### Start the application:
```bash
streamlit run app.py
```
- Open your browser and go to:

```bash
http://localhost:8501
```

## Features

- Interactive chat-based questionnaire
- Identifies relevant EU & Swedish digital health regulations
- AI-generated explanations using Google Gemini
- Expandable detailed regulation information

## Regulations Covered

- GDPR, MDR, Patientdatalagen, HSL, Patientsäkerhetslagen, OSL, EU AI Act

### How It Works

1. User starts the assessment
2. Answers a series of Yes/No questions
3. A decision engine determines applicable regulations
4. Google Gemini generates a short explanation
5. User can view detailed regulatory guidance
