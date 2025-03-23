import streamlit as st
import pandas as pd
import os
import requests
import json
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API URL (change this if your API is hosted elsewhere)
API_URL = "http://localhost:8000"  # Default FastAPI URL

# Set page configuration
st.set_page_config(
    page_title="News Sentiment Analysis",
    page_icon="📰",
    layout="wide"
)

# Function to get audio data
def get_audio_content(company_name):
    """Get audio content for a company from the API"""
    try:
        response = requests.get(f"{API_URL}/tts/{company_name}")
        response.raise_for_status()
        
        # Get the audio file path from the response
        audio_path = response.json().get("audio_path")
        
        if audio_path and os.path.exists(audio_path):
            with open(audio_path, "rb") as audio_file:
                return audio_file.read()
        return None
    except Exception as e:
        st.error(f"Error fetching audio: {e}")
        return None

# Function to get list of companies
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_companies():
    """Get list of available companies from the API"""
    try:
        response = requests.get(f"{API_URL}/companies")
        response.raise_for_status()
        return response.json().get("companies", [])
    except Exception as e:
        st.error(f"Error fetching companies: {e}")
        return []

# Function to get company data
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_company_data(company_name):
    """Get sentiment analysis data for a company from the API"""
    try:
        response = requests.get(f"{API_URL}/company/{company_name}")
        response.raise_for_status()
        return response.json().get("data", {})
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return {}

# App title and description
st.title("📰 News Sentiment Analysis")
st.markdown("""
This application analyzes news articles about companies, performs sentiment analysis, 
and generates text-to-speech output in Hindi.
""")

# Sidebar for company selection
st.sidebar.header("Select a Company")
companies = get_companies()

if not companies:
    st.sidebar.warning("No company data available. Please run the cron job first.")
else:
    selected_company = st.sidebar.selectbox("Choose a company:", companies)
    
    if selected_company:
        # Get data for the selected company
        company_data = get_company_data(selected_company)
        
        if company_data:
            # Display company information
            st.header(f"News Analysis for {selected_company}")
            
            # Display overall sentiment
            final_sentiment = company_data.get("Final Sentiment Analysis", "No sentiment analysis available")
            st.subheader("Overall Sentiment")
            st.info(final_sentiment)
            
            # Display Hindi TTS
            st.subheader("Hindi Text-to-Speech")
            audio_content = get_audio_content(selected_company)
            
            if audio_content:
                # Create a base64 encoded string for the audio
                b64 = base64.b64encode(audio_content).decode()
                audio_html = f"""
                <audio controls>
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    Your browser does not support the audio element.
                </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)
            else:
                st.warning("Audio not available. Please check the API.")
            
            # Display sentiment distribution
            st.subheader("Sentiment Distribution")
            if "Comparative Sentiment Score" in company_data and "Sentiment Distribution" in company_data["Comparative Sentiment Score"]:
                sentiment_dist = company_data["Comparative Sentiment Score"]["Sentiment Distribution"]
                
                # Create a DataFrame for the sentiment distribution
                sentiment_df = pd.DataFrame({
                    "Sentiment": list(sentiment_dist.keys()),
                    "Count": list(sentiment_dist.values())
                })
                
                # Display as a bar chart
                st.bar_chart(sentiment_df.set_index("Sentiment"))
            else:
                st.warning("Sentiment distribution not available.")
            
            # Display articles
            st.subheader("Articles")
            if "Articles" in company_data and company_data["Articles"]:
                for i, article in enumerate(company_data["Articles"], 1):
                    title = article.get("Title", "No title")
                    summary = article.get("Summary", "No summary")
                    sentiment = article.get("Sentiment", "Unknown")
                    topics = article.get("Topics", [])
                    
                    with st.expander(f"Article {i}: {title}"):
                        st.markdown(f"**Summary:** {summary}")
                        
                        # Show sentiment with appropriate color
                        if sentiment.lower() == "positive":
                            st.markdown(f"**Sentiment:** 🟢 {sentiment}")
                        elif sentiment.lower() == "negative":
                            st.markdown(f"**Sentiment:** 🔴 {sentiment}")
                        else:
                            st.markdown(f"**Sentiment:** 🟡 {sentiment}")
                        
                        st.markdown(f"**Topics:** {', '.join(topics)}")
            else:
                st.warning("No articles available for this company.")
            
            # Display comparative analysis
            st.subheader("Comparative Analysis")
            if "Comparative Sentiment Score" in company_data and "Coverage Differences" in company_data["Comparative Sentiment Score"]:
                differences = company_data["Comparative Sentiment Score"]["Coverage Differences"]
                
                for i, diff in enumerate(differences, 1):
                    comparison = diff.get("Comparison", "")
                    impact = diff.get("Impact", "")
                    
                    with st.expander(f"Comparison {i}"):
                        st.markdown(f"**Observation:** {comparison}")
                        st.markdown(f"**Impact:** {impact}")
            else:
                st.warning("Comparative analysis not available.")
            
            # Display topic overlap
            st.subheader("Topic Analysis")
            if "Comparative Sentiment Score" in company_data and "Topic Overlap" in company_data["Comparative Sentiment Score"]:
                topic_overlap = company_data["Comparative Sentiment Score"]["Topic Overlap"]
                
                # Common topics
                common_topics = topic_overlap.get("Common Topics", [])
                st.markdown("**Common Topics Across Articles:**")
                if common_topics:
                    st.write(", ".join(common_topics))
                else:
                    st.write("No common topics found.")
                
                # Display unique topics for each article
                st.markdown("**Unique Topics by Article:**")
                
                unique_topics = {k: v for k, v in topic_overlap.items() if k.startswith("Unique Topics in")}
                for article, topics in unique_topics.items():
                    st.markdown(f"*{article}:* {', '.join(topics)}")
            else:
                st.warning("Topic analysis not available.")
        else:
            st.error("Failed to load data for the selected company.")

# Footer
st.markdown("---")
st.markdown("### How to Use This Application")
st.markdown("""
1. Select a company from the dropdown menu on the left
2. View the overall sentiment analysis and listen to the Hindi TTS audio
3. Explore detailed article summaries and sentiment distributions
4. Review comparative analysis and topic overlaps across articles
""")