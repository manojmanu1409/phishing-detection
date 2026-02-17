import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os

# Get the directory of the current script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')

def train_models():
    print(f"Training models using base directory: {BASE_DIR}")
    
    # 1. URL Model
    url_data_path = os.path.join(DATA_DIR, 'urls.csv')
    if os.path.exists(url_data_path):
        print(f"Loading URL dataset from {url_data_path}...")
        url_data = pd.read_csv(url_data_path)
    else:
        print("URL dataset not found. Training with enhanced simulation data (demo)...")
        # Generate 2000 samples of simulation data
        n_samples = 2000
        url_data = pd.DataFrame({
            'url_length': np.random.randint(10, 200, n_samples),
            'has_ip': np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
            'has_https': np.random.choice([0, 1], n_samples, p=[0.3, 0.7]),
            'dot_count': np.random.randint(1, 5, n_samples),
            'hyphen_count': np.random.randint(0, 4, n_samples),
            'at_count': np.random.choice([0, 1], n_samples, p=[0.95, 0.05]),
            'slash_count': np.random.randint(1, 6, n_samples),
            'digit_ratio': np.random.uniform(0, 0.4, n_samples),
            'is_shortened': np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
            'keyword_count': np.random.randint(0, 3, n_samples),
            'label': np.random.choice([0, 1], n_samples)
        })
        
        # Add some correlations to make the model "learn"
        url_data.loc[url_data['has_ip'] == 1, 'label'] = 1
        url_data.loc[url_data['at_count'] == 1, 'label'] = 1
        url_data.loc[url_data['keyword_count'] > 0, 'label'] = 1
        url_data.loc[url_data['url_length'] > 150, 'label'] = 1
        url_data.loc[(url_data['has_https'] == 0) & (url_data['dot_count'] > 3), 'label'] = 1
        # Neutralize some labels for safe looking URLs
        url_data.loc[(url_data['has_https'] == 1) & (url_data['url_length'] < 50) & (url_data['keyword_count'] == 0), 'label'] = 0
    
    X_url = url_data.drop('label', axis=1)
    y_url = url_data['label']
    
    url_model = RandomForestClassifier(n_estimators=100)
    url_model.fit(X_url, y_url)
    joblib.dump(url_model, os.path.join(MODELS_DIR, 'url_model.pkl'))
    
    # 2. Email Model
    email_data_path = os.path.join(DATA_DIR, 'emails.csv')
    if os.path.exists(email_data_path):
        print(f"Loading Email dataset from {email_data_path}...")
        email_data = pd.read_csv(email_data_path)
        emails = email_data['text'].astype(str).tolist()
        labels = email_data['label'].tolist()
    else:
        print("Email dataset not found. Training with enhanced simulation data (demo)...")
        emails = [
            "Urgent: Verify your account now!", 
            "Your package is ready for pickup.",
            "Security alert: suspicious login detected.",
            "Meeting at 3pm today.",
            "Action Required: Account suspended immediately.",
            "Invoice from Apple Store - Please pay.",
            "Your order #12345 has been shipped.",
            "Claim your $1000 prize now!",
            "Weekly newsletter: Top stories this week.",
            "Warning: Unauthorised access to your bank account.",
            "Hey, are we still meeting for lunch?",
            "Can you send me the report by Friday?",
            "Just checking in on the project status.",
            "Happy birthday! Hope you have a great day.",
            "The weather is nice today."
        ] * 100
        labels = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0] * 100
    
    vectorizer = TfidfVectorizer(max_features=2000, stop_words='english')
    X_email = vectorizer.fit_transform(emails)
    
    email_model = RandomForestClassifier(n_estimators=100)
    email_model.fit(X_email, labels)
    
    joblib.dump(email_model, os.path.join(MODELS_DIR, 'email_model.pkl'))
    joblib.dump(vectorizer, os.path.join(MODELS_DIR, 'email_vectorizer.pkl'))
    
    print("Models trained and saved successfully.")

if __name__ == "__main__":
    train_models()
