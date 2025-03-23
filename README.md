# News Sentiment Analysis Application

This application extracts news articles about a company, performs sentiment analysis, conducts a comparative analysis across articles, and generates a text-to-speech (TTS) output in Hindi. It provides a web-based interface for users to input a company name and receive a structured sentiment report with audio output.

## Features

- **News Extraction**: Extracts title and content from news articles related to a given company using BeautifulSoup
- **Sentiment Analysis**: Determines the sentiment (positive, negative, neutral) of each article using Google's Gemini API
- **Comparative Analysis**: Compares sentiment and topics across multiple articles
- **Text-to-Speech**: Converts the summarized content into Hindi speech
- **User Interface**: Simple Streamlit web interface