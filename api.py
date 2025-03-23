from fastapi import FastAPI, HTTPException
import os
import pickle
from typing import Dict, Any, List
import logging
from pydantic import BaseModel
from utils.text_to_speech import TextToSpeechService
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="News Sentiment Analysis API")

# Initialize Text-to-Speech service
tts_service = TextToSpeechService()

# Create a model for responses
class CompanyResponse(BaseModel):
    company: str
    data: Dict[str, Any]

class CompanyListResponse(BaseModel):
    companies: List[str]

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint to check if API is running"""
    return {"message": "News Sentiment Analysis API is running"}

@app.get("/companies", response_model=CompanyListResponse)
async def get_companies():
    """Get a list of all available companies"""
    try:
        # Get all pickle files in the output directory
        output_dir = "data/output"
        if not os.path.exists(output_dir):
            return {"companies": []}
            
        company_files = [f for f in os.listdir(output_dir) if f.endswith('.pkl')]
        companies = [os.path.splitext(f)[0].replace('_', ' ').title() for f in company_files]
        
        return {"companies": companies}
    
    except Exception as e:
        logger.error(f"Error getting companies: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/company/{company_name}", response_model=CompanyResponse)
async def get_company_data(company_name: str):
    """
    Get sentiment analysis data for a specific company.
    
    Args:
        company_name: Name of the company
        
    Returns:
        CompanyResponse object with company name and analysis data
    """
    try:
        # Normalize the company name
        company_file = company_name.lower().replace(' ', '_') + '.pkl'
        file_path = f"data/output/{company_file}"
        
        # Check if the file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Data for {company_name} not found")
        
        # Load the data from the pickle file
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        return {"company": company_name, "data": data}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting data for {company_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/tts/{company_name}")
async def get_tts(company_name: str):
    """
    Generate text-to-speech for a company's sentiment analysis in Hindi.
    
    Args:
        company_name: Name of the company
        
    Returns:
        Path to the audio file
    """
    try:
        # Get the company data
        company_file = company_name.lower().replace(' ', '_') + '.pkl'
        file_path = f"data/output/{company_file}"
        
        # Check if the file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Data for {company_name} not found")
        
        # Load the data from the pickle file
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        # Get the final sentiment analysis
        sentiment_text = data.get("Final Sentiment Analysis", "No sentiment analysis available")
        
        # Translate to Hindi
        hindi_text = tts_service.translate_to_hindi(sentiment_text)
        
        # Generate speech
        audio_path, temp_dir = tts_service.text_to_speech(hindi_text)
        
        if not audio_path:
            raise HTTPException(status_code=500, detail="Failed to generate speech")
        
        # In a real application, you would return the audio file or a URL to it
        # For this example, we'll just return the path
        # Note: Normally you would handle the temporary file cleanup properly
        return {"audio_path": audio_path}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating TTS for {company_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")