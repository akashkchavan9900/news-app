import google.generativeai as genai
import os
from typing import List, Dict, Any
import json

class GeminiService:
    def __init__(self, api_key: str = None):
        """
        Initialize the Gemini service with API key.
        
        Args:
            api_key: Google API key for Gemini
        """
        if api_key is None:

            api_key = os.getenv("GOOGLE_API_KEY")

            
        if not api_key:
            raise ValueError("Google API key is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    def analyze_news_articles(self, company_name: str, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze news articles for a company using Gemini API.
        
        Args:
            company_name: Name of the company
            articles: List of article dictionaries with title and content
        
        Returns:
            Dictionary with analysis results
        """
        # Create a prompt for Gemini
        prompt = self._create_analysis_prompt(company_name, articles)
        
        # Send the prompt to Gemini
        try:
            response = self.model.generate_content(prompt)
            result = response.text
            
            # Parse the JSON response
            try:
                # Check if the response starts and ends with markdown code block indicators
                if result.startswith("```json") and result.endswith("```"):
                    result = result[7:-3]  # Remove ```json and ``` markers
                
                # Parse the JSON content
                analysis = json.loads(result)
                return analysis
            except json.JSONDecodeError as e:
                print(f"Error parsing Gemini response as JSON: {e}")
                print(f"Raw response: {result}")
                
                # Attempt to fix broken JSON (this is a fallback, not ideal)
                # Create a minimal valid JSON with just the necessary information
                return {
                    "Company": company_name,
                    "Articles": [],
                    "Final Sentiment Analysis": "Error analyzing articles."
                }
        
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return {
                "Company": company_name,
                "Articles": [],
                "Final Sentiment Analysis": "Error analyzing articles."
            }
    
    def _create_analysis_prompt(self, company_name: str, articles: List[Dict[str, Any]]) -> str:
        """
        Create a prompt for the Gemini model to analyze news articles.
        
        Args:
            company_name: Name of the company
            articles: List of article dictionaries
            
        Returns:
            Prompt string for Gemini
        """
        prompt = f"""
        Analyze the following news articles about {company_name}. For each article:
        
        1. Create a concise summary
        2. Determine the sentiment (Positive, Negative, or Neutral)
        3. Extract key topics discussed
        
        Then, perform a comparative analysis across all articles to understand:
        - The distribution of sentiment
        - Key differences in coverage
        - Topic overlap between articles
        
        Finally, provide an overall sentiment analysis for {company_name} based on these articles.
        
        Return your analysis in the following JSON format:
        
        ```json
        {{
            "Company": "{company_name}",
            "Articles": [
                {{
                    "Title": "Article title",
                    "Summary": "Concise summary",
                    "Sentiment": "Positive/Negative/Neutral",
                    "Topics": ["Topic 1", "Topic 2"]
                }}
            ],
            "Comparative Sentiment Score": {{
                "Sentiment Distribution": {{
                    "Positive": count,
                    "Negative": count,
                    "Neutral": count
                }},
                "Coverage Differences": [
                    {{
                        "Comparison": "Description of difference between articles",
                        "Impact": "Impact of this difference"
                    }}
                ],
                "Topic Overlap": {{
                    "Common Topics": ["Topic shared across articles"],
                    "Unique Topics in Article X": ["Topics unique to a specific article"]
                }}
            }},
            "Final Sentiment Analysis": "Overall sentiment conclusion"
        }}
        ```
        
        Here are the articles:
        """
        
        # Add each article to the prompt
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'No title').replace('"', '\\"')
            content = article.get('content', 'No content')
            
            # Truncate very long articles to avoid exceeding token limits
            if len(content) > 5000:
                content = content[:5000] + "..."
            
            prompt += f"\n\nARTICLE {i} - {title}\n{content}"
        
        return prompt
