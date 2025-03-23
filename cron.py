import os
import pickle
import pandas as pd
from utils.news_scraper import NewsScraper
from utils.gemini_service import GeminiService
from typing import List, Dict, Any
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cron.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def process_company(company_name: str) -> Dict[str, Any]:
    """
    Process a single company.
    
    Args:
        company_name: Name of the company to process
        
    Returns:
        Dictionary with analysis results
    """
    logger.info(f"Processing company: {company_name}")
    
    # Initialize services
    news_scraper = NewsScraper()
    gemini_service = GeminiService()
    
    # Step 1: Fetch article URLs
    article_urls = news_scraper.search_google_news(company_name)
    logger.info(f"Found {len(article_urls)} articles for {company_name}")
    
    # Step 2: Extract content from each article
    articles = []
    for url in article_urls:
        logger.info(f"Extracting content from: {url}")
        article = news_scraper.extract_article_content(url)
        if article['title'] and article['content']:
            articles.append(article)
    
    logger.info(f"Successfully extracted content from {len(articles)} articles")
    
    # Step 3: Analyze articles with Gemini
    if articles:
        logger.info("Sending articles to Gemini for analysis")
        analysis = gemini_service.analyze_news_articles(company_name, articles)
        return analysis
    else:
        logger.warning(f"No valid articles found for {company_name}")
        return {
            "Company": company_name,
            "Articles": [],
            "Final Sentiment Analysis": "No articles found for analysis."
        }

def main():
    """Main function to process all companies in the CSV file"""
    logger.info("Starting cron job to process companies")
    
    # Create output directory if it doesn't exist
    os.makedirs("data/output", exist_ok=True)
    
    try:
        # Check if CSV file exists
        csv_path = "data/company_list.csv"
        if not os.path.exists(csv_path):
            logger.error(f"CSV file not found: {csv_path}")
            return
            
        # Read the list of companies from CSV
        company_df = pd.read_csv(csv_path)
        
        # Debug: Print the column names to identify the correct one
        logger.info(f"CSV columns: {company_df.columns.tolist()}")
        
        # Try to find the company name column with common variations
        column_options = ['company_name', 'Company', 'company', 'CompanyName', 'name', 'Name']
        company_column = None
        
        for col in column_options:
            if col in company_df.columns:
                company_column = col
                logger.info(f"Found company column: '{col}'")
                break
                
        if not company_column:
            # If none of the expected columns is found, use the first column
            company_column = company_df.columns[0]
            logger.warning(f"Using first column as company column: '{company_column}'")
            
        # Get the list of companies
        company_list = company_df[company_column].tolist()
        logger.info(f"Loaded {len(company_list)} companies from CSV")
        
        # Process each company
        for company in company_list:
            try:
                # Skip empty values
                if pd.isna(company) or not company:
                    logger.warning("Skipping empty company name")
                    continue
                    
                # Process the company
                analysis = process_company(company)
                
                # Save the analysis to a pickle file
                safe_name = str(company).lower().replace(' ', '_').replace('/', '_').replace('\\', '_')
                output_file = f"data/output/{safe_name}.pkl"
                with open(output_file, 'wb') as f:
                    pickle.dump(analysis, f)
                logger.info(f"Saved analysis for {company} to {output_file}")
            
            except Exception as e:
                logger.error(f"Error processing company {company}: {e}")
    
    except Exception as e:
        logger.error(f"Error in main cron job: {e}")

if __name__ == "__main__":
    main()