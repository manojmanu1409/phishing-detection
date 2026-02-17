import streamlit as st
import pandas as pd
import plotly.express as px
from utils.detection import get_url_detector, get_email_detector
from utils.database import init_db, log_detection, get_logs, get_stats
from utils.ai_explanation import get_ai_explanation
from utils.reporting import generate_pdf_report
import os

# Page Config
st.set_page_config(page_title="PhishGuard AI", layout="wide", page_icon="🛡️")

# Initialize DB
init_db()

# Load Detectors
url_detector = get_url_detector()
email_detector = get_email_detector()

# Sidebar
st.sidebar.title("🛡️ PhishGuard AI")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", ["Dashboard", "Email Detection", "URL Detection", "Threat Monitoring", "Admin Analytics"])

# Header
st.title(f"PhishGuard AI - {page}")

if page == "Dashboard":
    st.markdown("### Real-Time Phishing Protection Powered by AI")
    col1, col2, col3 = st.columns(3)
    
    stats = get_stats()
    total_scans = stats['count'].sum() if not stats.empty else 0
    phishing_detected = stats[stats['prediction'] == 'True']['count'].sum() if not stats.empty else 0
    
    col1.metric("Total Scans", total_scans)
    col2.metric("Phishing Detected", phishing_detected)
    col3.metric("System Health", "100%", "Stable")
    
    st.markdown("---")
    st.subheader("Recent Activity")
    logs = get_logs(10)
    if not logs.empty:
        # Style the dataframe: Red for True (Phishing), Green for False (Safe)
        def highlight_prediction(val):
            color = 'red' if val == 'True' else 'green'
            return f'color: {color}; font-weight: bold'
        
        st.dataframe(
            logs[['type', 'prediction', 'confidence', 'timestamp']].style.applymap(
                highlight_prediction, subset=['prediction']
            ),
            use_container_width=True
        )
    else:
        st.info("No scans performed yet.")

elif page == "Email Detection":
    st.markdown("### Analyze Email Content for Phishing")
    email_content = st.text_area("Paste Email Content Here", height=200)
    uploaded_file = st.file_uploader("Or Upload .eml / .txt file", type=['eml', 'txt'])
    
    if uploaded_file:
        email_content = uploaded_file.read().decode("utf-8")
        st.text_area("Uploaded Content", email_content, height=150)

    if st.button("Scan Email"):
        if email_content:
            with st.spinner("Analyzing email content..."):
                is_phishing, score, phrases = email_detector.predict(email_content)
                log_detection("Email", email_content[:100], is_phishing, score)
                
                if is_phishing:
                    st.error(f"🚨 WARNING: PHISHING Detected! (Confidence: {score*100:.1f}%)")
                else:
                    st.success(f"✅ SAFE Email (Confidence: {score*100:.1f}%)")
                
                explanation = get_ai_explanation("Email", email_content, is_phishing, score)
                
                with st.expander("AI Explanation & Indicators"):
                    st.write(explanation['summary'])
                    st.markdown("**Key Indicators:**")
                    for factor in explanation['key_factors']:
                        st.write(f"- {factor}")
                    
                    if phrases:
                        st.markdown("**Suspicious Phrases Highlighted:**")
                        for p in phrases:
                            st.markdown(f"- :red[{p}]")
                
                with st.expander("Security Recommendations"):
                    for rec in explanation['recommendations']:
                        st.write(f"- {rec}")
                
                # Report Generation
                report_path = generate_pdf_report("Email", email_content, is_phishing, score, explanation)
                with open(report_path, "rb") as f:
                    st.download_button("Download Analysis Report (PDF)", f, file_name="phishing_report.pdf")
        else:
            st.warning("Please enter email content or upload a file.")

elif page == "URL Detection":
    st.markdown("### Scan URLs for Malicious Patterns")
    url_input = st.text_input("Enter URL to scan (e.g., http://suspicious-site.com)")
    
    if st.button("Scan URL"):
        if url_input:
            with st.spinner("Scanning URL..."):
                is_phishing, score = url_detector.predict(url_input)
                log_detection("URL", url_input, is_phishing, score)
                
                if is_phishing:
                    st.error(f"🚨 DANGER: PHISHING URL Detected! (Confidence: {score*100:.1f}%)")
                else:
                    st.success(f"✅ SAFE URL (Confidence: {score*100:.1f}%)")
                
                explanation = get_ai_explanation("URL", url_input, is_phishing, score)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("AI Analysis")
                    st.write(explanation['summary'])
                    for factor in explanation['key_factors']:
                        st.write(f"- {factor}")
                
                with col2:
                    st.subheader("Recommendations")
                    for rec in explanation['recommendations']:
                        st.write(f"- {rec}")
                
                report_path = generate_pdf_report("URL", url_input, is_phishing, score, explanation)
                with open(report_path, "rb") as f:
                    st.download_button("Download URL Analysis Report (PDF)", f, file_name="url_report.pdf")
        else:
            st.warning("Please enter a URL.")

elif page == "Threat Monitoring":
    st.markdown("### Real-Time Threat Intelligence")
    st.info("Live feed of global phishing attempts and local system detections.")
    
    logs = get_logs(50)
    if not logs.empty:
        fig = px.line(logs, x='timestamp', y='confidence', color='prediction', 
                     color_discrete_map={'True': 'red', 'False': 'green'},
                     title="Detection Confidence Over Time")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Live Detection Log")
        st.dataframe(logs)
    else:
        st.write("No data available for monitoring.")

elif page == "Admin Analytics":
    st.markdown("### System Performance & Analytics")
    stats = get_stats()
    
    if not stats.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig_pie = px.pie(stats, values='count', names='prediction', 
                            color='prediction',
                            color_discrete_map={'True': 'red', 'False': 'green'},
                            title="Phishing vs Safe Ratio")
            st.plotly_chart(fig_pie)
        
        with col2:
            fig_bar = px.bar(stats, x='type', y='count', color='prediction', barmode='group', 
                            color_discrete_map={'True': 'red', 'False': 'green'},
                            title="Detection by Type")
            st.plotly_chart(fig_bar)
            
        st.subheader("Continuous Learning - User Feedback")
        st.write("Review false positives reported by users to retrain models.")
    else:
        st.info("Perform some scans to see analytics.")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("PhishGuard AI v1.0\nCreated for Real-World Security")
