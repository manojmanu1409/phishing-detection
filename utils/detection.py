import re
import pandas as pd
import numpy as np
import joblib
import tldextract
import os

# Get the directory of the current script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

class URLDetector:
    def __init__(self):
        model_path = os.path.join(MODELS_DIR, 'url_model.pkl')
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
        else:
            self.model = None
        
    def extract_features(self, url):
        features = {}
        url_lower = url.lower()
        features['url_length'] = len(url)
        features['has_ip'] = 1 if re.search(r'\d+\.\d+\.\d+\.\d+', url) else 0
        features['has_https'] = 1 if url.startswith('https') else 0
        features['dot_count'] = url.count('.')
        features['hyphen_count'] = url.count('-')
        features['at_count'] = url.count('@')
        features['slash_count'] = url.count('/')
        features['digit_ratio'] = sum(c.isdigit() for c in url) / len(url) if len(url) > 0 else 0
        features['is_shortened'] = 1 if any(short in url_lower for short in ['bit.ly', 'goo.gl', 't.co', 'tinyurl']) else 0
        
        # Keyword features in URL
        suspicious_keywords = ['login', 'verify', 'account', 'bank', 'secure', 'update', 'signin', 'wp-', 'admin']
        features['keyword_count'] = sum(1 for kw in suspicious_keywords if kw in url_lower)
        return features

    def predict(self, url):
        features = self.extract_features(url)
        url_lower = url.lower()
        
        # 1. White-list common safe domains to reduce false positives
        safe_domains = ['google.com', 'facebook.com', 'apple.com', 'microsoft.com', 'amazon.com', 'github.com']
        if any(domain in url_lower for domain in safe_domains) and features['has_https']:
            return False, 0.05

        if self.model:
            try:
                X = pd.DataFrame([features])
                prob = self.model.predict_proba(X)[0][1]
                # If model is uncertain, let heuristics weigh in
                if 0.3 < prob < 0.7:
                    pass # Continue to heuristics to refine
                else:
                    return prob > 0.5, prob
            except Exception:
                pass
        
        # Enhanced Heuristic logic
        score = 0.05
        if features['url_length'] > 50: score += 0.1
        if features['url_length'] > 100: score += 0.15
        if features['has_ip']: score += 0.5
        if not features['has_https']: score += 0.2
        if features['dot_count'] > 3: score += 0.15
        if features['hyphen_count'] > 2: score += 0.15
        if features['at_count'] > 0: score += 0.4
        if features['digit_ratio'] > 0.25: score += 0.2
        if features['is_shortened']: score += 0.25
        if features['keyword_count'] > 0: score += 0.2 * features['keyword_count']
        
        score = min(score, 1.0)
        return score > 0.5, score

class EmailDetector:
    def __init__(self):
        model_path = os.path.join(MODELS_DIR, 'email_model.pkl')
        vec_path = os.path.join(MODELS_DIR, 'email_vectorizer.pkl')
        if os.path.exists(model_path) and os.path.exists(vec_path):
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vec_path)
        else:
            self.model = None
            self.vectorizer = None
        self.urgency_words = [
            'verify', 'immediately', 'urgent', 'action required', 'account suspended', 
            'password', 'security', 'login', 'confirm', 'unusual activity', 'frozen',
            'locked', 'limited', 'unauthorized', 'click here', 'billing', 'update',
            'invoice', 'winner', 'prize', 'gift card', 'bonus', 'free', 'reward'
        ]
        
    def predict(self, content):
        content_lower = content.lower()
        if self.model and self.vectorizer:
            X = self.vectorizer.transform([content])
            prob = self.model.predict_proba(X)[0][1]
            # Combine model with keyword check for better reliability
            keyword_match = any(word in content_lower for word in self.urgency_words)
            if keyword_match:
                prob = max(prob, 0.6)
            is_phishing = prob > 0.5
        else:
            # Enhanced Fallback
            matches = [word for word in self.urgency_words if word in content_lower]
            match_count = len(matches)
            if match_count >= 3:
                prob = 0.9
            elif match_count >= 1:
                prob = 0.7
            else:
                prob = 0.1
            is_phishing = prob > 0.5
            
        suspicious_phrases = [word for word in self.urgency_words if word in content_lower]
        return is_phishing, prob, suspicious_phrases

def get_url_detector():
    return URLDetector()

def get_email_detector():
    return EmailDetector()
