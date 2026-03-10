from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import json
import numpy as np
import sys
import os

# Add the backend directory to the path so we can import services
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.profiler import profile_dataset
from services.recommendations import generate_recommendations, categorize_recommendations
from services.code_generator import generate_cleaning_code, generate_advanced_pipeline_code

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def convert_nan_to_none(obj):
    """Recursively convert NaN, inf, -inf to None for JSON serialization."""
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: convert_nan_to_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_nan_to_none(item) for item in obj]
    return obj

@app.get("/")
def home():
    return {"message": "AI Data Cleaning Assistant Backend Running"}

@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """Upload a CSV or Excel file and return dataset preview."""
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
            
        if not (file.filename.endswith(".csv") or file.filename.endswith(".xlsx") or file.filename.endswith(".xls")):
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload CSV or Excel files.")
        
        # Read the file
        contents = await file.read()
        
        if not contents:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Try to read the CSV
        try:
            if file.filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(contents))
            else:
                df = pd.read_excel(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
        
        # Validate dataset
        if df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")
        
        # Generate preview (all rows) and convert NaN to None
        preview_dict = df.to_dict(orient="records")
        preview = convert_nan_to_none(preview_dict)

        return {
            "success": True,
            "filename": file.filename,
            "columns": list(df.columns),
            "rows": len(df),
            "preview": preview
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/analyze")
async def analyze_dataset(file: UploadFile = File(...)):
    """Analyze a CSV or Excel file and return comprehensive data quality analysis."""
    try:
        # Validate and read file
        if not file.filename or not (file.filename.endswith((".csv", ".xlsx", ".xls"))):
            raise HTTPException(status_code=400, detail="Invalid file format")
        
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="File is empty")
        
        print(f"[ANALYZE] Reading file: {file.filename} ({len(contents)} bytes)")
        # Read the CSV or Excel
        try:
            if file.filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(contents))
            else:
                df = pd.read_excel(io.BytesIO(contents))
            print(f"[ANALYZE] DataFrame loaded: {len(df)} rows, {len(df.columns)} cols")
        except Exception as read_err:
            print(f"[ANALYZE] Error reading file: {read_err}")
            raise HTTPException(status_code=400, detail=f"Failed to read file: {str(read_err)}")
        
        if df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")
        
        print("[ANALYZE] Starting profiling...")
        # Profile the dataset
        profile = profile_dataset(df)
        profile = convert_nan_to_none(profile)
        print(f"[ANALYZE] Profile complete, health_score: {profile.get('health_score')}")
        
        print("[ANALYZE] Generating recommendations...")
        # Generate recommendations
        recommendations = generate_recommendations(profile, list(df.columns))
        recommendations = convert_nan_to_none(recommendations)
        print(f"[ANALYZE] Generated {len(recommendations)} recommendations")
        
        # Categorize recommendations
        categorized_recs = categorize_recommendations(recommendations)
        categorized_recs = convert_nan_to_none(categorized_recs)
        
        print("[ANALYZE] Generating cleaning codes...")
        # Generate cleaning codes
        basic_code = generate_cleaning_code(profile)
        advanced_code = generate_advanced_pipeline_code(profile)
        print(f"[ANALYZE] Code generated ({len(basic_code)} + {len(advanced_code)} bytes)")

        print("[ANALYZE] Returning response...")
        return {
            "success": True,
            "filename": file.filename,
            "profile": profile,
            "recommendations": recommendations,
            "categorized_recommendations": categorized_recs,
            "cleaning_code": {
                "basic": basic_code,
                "advanced": advanced_code
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ANALYZE] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")