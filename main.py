from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import uvicorn
import json
import os
from typing import Optional
from pydantic import BaseModel
from fitscore_calculator import FitScoreCalculator, FitScoreResult

# Initialize FastAPI app
app = FastAPI(
    title="FitScore Calculator API",
    description="A comprehensive candidate evaluation system with GPT-4o-mini integration",
    version="1.0.0"
)

# Initialize the FitScore calculator
calculator = FitScoreCalculator()

# Create templates directory and mount static files
templates = Jinja2Templates(directory="templates")

# Pydantic models for request/response
class FitScoreRequest(BaseModel):
    resume_text: str
    job_description: str
    collateral: Optional[str] = None
    openai_api_key: Optional[str] = None
    use_gpt4: bool = True

class FitScoreResponse(BaseModel):
    total_score: float
    education_score: float
    career_trajectory_score: float
    company_relevance_score: float
    tenure_stability_score: float
    most_important_skills_score: float
    bonus_signals_score: float
    red_flags_penalty: float
    submittable: bool
    recommendations: list
    details: dict
    timestamp: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with form for testing FitScore calculator"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/calculate-fitscore", response_model=FitScoreResponse)
async def calculate_fitscore(request: FitScoreRequest):
    """
    Calculate FitScore for a candidate based on resume and job description
    """
    try:
        # Set OpenAI API key if provided
        if request.openai_api_key:
            os.environ["OPENAI_API_KEY"] = request.openai_api_key
            # Reinitialize calculator with new API key
            global calculator
            calculator = FitScoreCalculator(openai_api_key=request.openai_api_key)
        
        # Calculate FitScore
        result = calculator.calculate_fitscore(
            resume_text=request.resume_text,
            job_description=request.job_description,
            collateral=request.collateral,
            use_gpt4=request.use_gpt4
        )
        
        # Convert to response model
        response = FitScoreResponse(
            total_score=result.total_score,
            education_score=result.education_score,
            career_trajectory_score=result.career_trajectory_score,
            company_relevance_score=result.company_relevance_score,
            tenure_stability_score=result.tenure_stability_score,
            most_important_skills_score=result.most_important_skills_score,
            bonus_signals_score=result.bonus_signals_score,
            red_flags_penalty=result.red_flags_penalty,
            submittable=result.total_score >= 8.2,
            recommendations=result.recommendations,
            details=result.details,
            timestamp=result.timestamp
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating FitScore: {str(e)}")

@app.post("/calculate-fitscore-form")
async def calculate_fitscore_form(
    resume_text: str = Form(...),
    job_description: str = Form(...),
    collateral: Optional[str] = Form(None),
    openai_api_key: Optional[str] = Form(None),
    use_gpt4: str = Form("on")
):
    """
    Calculate FitScore using form data (for web interface)
    """
    try:
        # Set OpenAI API key if provided
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
            global calculator
            calculator = FitScoreCalculator(openai_api_key=openai_api_key)
        
        # Convert checkbox value to boolean
        use_gpt4_bool = use_gpt4 == "on"
        
        # Calculate FitScore
        result = calculator.calculate_fitscore(
            resume_text=resume_text,
            job_description=job_description,
            collateral=collateral,
            use_gpt4=use_gpt4_bool
        )
        
        # Return results for template
        return {
            "success": True,
            "total_score": round(result.total_score, 2),
            "education_score": round(result.education_score, 2),
            "career_trajectory_score": round(result.career_trajectory_score, 2),
            "company_relevance_score": round(result.company_relevance_score, 2),
            "tenure_stability_score": round(result.tenure_stability_score, 2),
            "most_important_skills_score": round(result.most_important_skills_score, 2),
            "bonus_signals_score": round(result.bonus_signals_score, 2),
            "red_flags_penalty": round(result.red_flags_penalty, 2),
            "submittable": result.total_score >= 8.2,
            "recommendations": result.recommendations,
            "details": result.details,
            "timestamp": result.timestamp
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "FitScore Calculator API is running"}

@app.get("/api-docs")
async def api_docs():
    """API documentation endpoint"""
    return {
        "endpoints": {
            "POST /calculate-fitscore": "Calculate FitScore with JSON payload",
            "POST /calculate-fitscore-form": "Calculate FitScore with form data",
            "GET /": "Web interface for testing",
            "GET /health": "Health check",
            "GET /api-docs": "This documentation"
        },
        "example_request": {
            "resume_text": "Candidate resume text...",
            "job_description": "Job description text...",
            "collateral": "Additional context (optional)",
            "openai_api_key": "Your OpenAI API key (optional)",
            "use_gpt4": True
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

# For Vercel deployment
app.debug = True 
