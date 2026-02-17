# PhishGuard AI - Real-Time Phishing Detection Dashboard

PhishGuard AI is a comprehensive phishing detection web application built with Streamlit and Python. It leverages machine learning and NLP techniques to identify phishing attempts in both emails and URLs.

## Core Features
- **Email Phishing Detection**: Analyzes email content for urgency, suspicious domains, and spoofing patterns.
- **URL Phishing Detection**: Extracts URL-based features and checks against ML models.
- **AI Explanation Report**: Uses simulated XAI to explain detection factors.
- **Real-Time Threat Monitoring**: Dashboard for tracking recent threats.
- **Admin Analytics**: Visualizations of system performance and detection rates.

## Tech Stack
- **Frontend**: Streamlit
- **Backend**: Python
- **ML/NLP**: Scikit-learn, Joblib, Plotly
- **Database**: SQLite
- **Reporting**: FPDF2

## Installation & Setup

### Prerequisites
- Python 3.9+
- Docker (optional)

### Local Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

### Docker Deployment
1. Build the image:
   ```bash
   docker build -t phishguard-ai .
   ```
2. Run the container:
   ```bash
   docker run -p 8501:8501 phishguard-ai
   ```

## Project Structure
```
phishing_detection_app/
├── app.py              # Main Streamlit application
├── requirements.txt    # Project dependencies
├── Dockerfile          # Containerization config
├── models/             # ML models and training scripts
├── utils/              # Helper modules (detection, database, reporting)
├── data/               # Dataset storage
└── logs/               # Application logs and PDF reports
```

## Dataset Suggestions
- [Kaggle: Phishing Dataset for Machine Learning](https://www.kaggle.com/datasets/shashwat तिवारी/phishing-dataset-for-machine-learning)
- [Kaggle: Email Phishing Dataset](https://www.kaggle.com/datasets/subhajitnayak/country-wise-phishing-dataset)
