import numpy as np
import pandas as pd

def get_ai_explanation(detection_type, input_data, prediction, score):
    """
    Simulates AI explanation logic using heuristics for demo purposes.
    In a real app, this would use SHAP or LIME values from the model.
    """
    explanation = {
        "summary": f"The {detection_type} was classified as {'PHISHING' if prediction else 'LEGITIMATE'} with {score*100:.1f}% confidence.",
        "key_factors": [],
        "recommendations": []
    }
    
    if detection_type == "URL":
        if len(input_data) > 50:
            explanation["key_factors"].append("Unusually long URL length.")
        if "@" in input_data:
            explanation["key_factors"].append("Presence of '@' symbol used for obfuscation.")
        if "https" not in input_data:
            explanation["key_factors"].append("Lack of HTTPS encryption.")
    else:
        # Email factors
        content_lower = input_data.lower()
        urgency_words = ['verify', 'immediately', 'urgent', 'account suspended']
        for word in urgency_words:
            if word in content_lower:
                explanation["key_factors"].append(f"Urgency keyword detected: '{word}'")
    
    # Recommendations
    if prediction:
        explanation["recommendations"] = [
            "Do not click on any links or download attachments.",
            "Report this to your IT security department.",
            "Delete the email or close the browser tab immediately.",
            "If you entered credentials, change your password immediately."
        ]
    else:
        explanation["recommendations"] = [
            "This appears to be safe, but always remain cautious.",
            "Verify the sender's identity through another channel if unsure.",
            "Check for subtle typos in the domain name."
        ]
        
    return explanation
