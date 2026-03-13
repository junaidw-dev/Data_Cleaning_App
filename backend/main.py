import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import io
import json
import base64
from uuid import uuid4
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# FastAPI
from fastapi import FastAPI, UploadFile, File, HTTPException, status, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel

# Import services
from config import Config, get_config, get_supabase_client
from auth import AuthService, PasswordResetService
from database import DatabaseService
from mock_database import get_mock_database, MockDatabaseService
from google_auth import GoogleOAuthService
from models import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    ProjectCreate, ProjectResponse, DatasetResponse,
    AnalysisResult, ColumnProfile, DataQualityProfile, Recommendation,
    TeamMemberCreate, TeamMemberResponse, APIKeyCreate, APIKeyResponse, APIKeyListResponse
)
from services.profiler import profile_dataset
from services.recommendations import generate_recommendations, categorize_recommendations
from services.code_generator import generate_cleaning_code, generate_advanced_pipeline_code
from services.visualization import (
    generate_missing_values_data,
    generate_numeric_distribution_data,
    generate_categorical_distribution_data,
    generate_correlation_data,
    generate_outlier_boxplot_data,
    generate_data_quality_heatmap,
    generate_row_quality_analysis
)
from services.cleaner import apply_cleaning_pipeline
from services.storage import get_storage_service

# ==================== APP INITIALIZATION ====================

app = FastAPI(
    title="AI Data Cleaner SaaS API",
    description="Production-ready data quality platform",
    version="1.0.0"
)

config = get_config()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# ==================== HELPERS ====================

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

def convert_numpy_types(obj):
    """Recursively convert NumPy types to native Python types."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj

# ==================== AUTHENTICATION DEPENDENCY ====================

async def get_current_user(credentials = Depends(security)) -> Dict:
    """Verify JWT token and return user info."""
    try:
        token = credentials.credentials
        payload = AuthService.verify_token(token)
        return payload
    except HTTPException:
        raise

async def get_db_service():
    """Get database service."""
    config = get_config()
    # Use mock database if Supabase credentials are not configured
    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        return get_mock_database()
    return DatabaseService(get_supabase_client())

# ==================== PUBLIC ENDPOINTS ====================

@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "AI Data Cleaner SaaS",
        "version": "1.0.0"
    }

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/api/auth/signup", response_model=TokenResponse)
async def signup(user_data: UserCreate, db: DatabaseService = Depends(get_db_service)):
    """Register a new user."""
    try:
        # Check if user already exists
        existing_user = db.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and create user
        password_hash = AuthService.hash_password(user_data.password)
        user = db.create_user(user_data.email, password_hash, user_data.full_name)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Create token
        access_token = AuthService.create_access_token(user["id"], user["email"])
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse(**user)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: DatabaseService = Depends(get_db_service)):
    """Login user."""
    try:
        user = db.get_user_by_email(credentials.email)
        
        if not user or not AuthService.verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        access_token = AuthService.create_access_token(user["id"], user["email"])
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse(**user)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/google", response_model=TokenResponse)
async def google_login(data: Dict, db: DatabaseService = Depends(get_db_service)):
    """Login/register with Google OAuth."""
    try:
        google_service = GoogleOAuthService()
        
        # Extract token from request
        token = data.get("token")
        if not token:
            raise HTTPException(status_code=400, detail="Token is required")
        
        # Verify Google token
        claims = google_service.verify_google_token(token)
        if not claims:
            raise HTTPException(status_code=401, detail="Invalid Google token")
        
        email = claims.get("email")
        name = claims.get("name", "Google User")
        picture = claims.get("picture", "")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")
        
        # Check if user exists
        user = db.get_user_by_email(email)
        
        if not user:
            # Create new user from Google info
            # Generate a random password for OAuth users
            random_password = AuthService.hash_password(str(uuid4())[:16])
            user = db.create_user(email, random_password, name)
            
            if not user:
                raise HTTPException(status_code=500, detail="Failed to create user")
        
        # Create access token
        access_token = AuthService.create_access_token(user["id"], user["email"])
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse(**user)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/password-reset")
async def request_password_reset(data: Dict, db: DatabaseService = Depends(get_db_service)):
    """Request password reset."""
    try:
        user = db.get_user_by_email(data.get("email"))
        if not user:
            # Don't reveal if email exists (security)
            return {"message": "If email exists, reset link will be sent"}
        
        reset_token = PasswordResetService.create_reset_token(user["id"])
        
        # TODO: Send email with reset link
        # email_service.send_password_reset_email(user["email"], reset_token)
        
        return {"message": "Reset link sent to email"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== USER ENDPOINTS ====================

@app.get("/api/user/me", response_model=UserResponse)
async def get_current_user_profile(
    user: Dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service)
):
    """Get current user profile."""
    try:
        profile = db.get_user_by_id(user["user_id"])
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(**profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== PROJECT ENDPOINTS ====================

@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    user: Dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service)
):
    """Create a new project."""
    try:
        project = db.create_project(
            user_id=user["user_id"],
            name=project_data.name,
            description=project_data.description
        )
        
        if not project:
            raise HTTPException(status_code=500, detail="Failed to create project")
        
        return ProjectResponse(**project, dataset_count=0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects", response_model=List[ProjectResponse])
async def list_projects(
    user: Dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service)
):
    """List all projects for the user."""
    try:
        projects = db.get_user_projects(user["user_id"])
        return [ProjectResponse(**p, dataset_count=0) for p in projects]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    user: Dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service)
):
    """Get project details."""
    try:
        project = db.get_project(project_id, user["user_id"])
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return ProjectResponse(**project, dataset_count=0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/projects/{project_id}")
async def delete_project(
    project_id: str,
    user: Dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service)
):
    """Delete a project."""
    try:
        db.delete_project(project_id, user["user_id"])
        return {"message": "Project deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== DATASET ENDPOINTS ====================

@app.post("/api/projects/{project_id}/datasets")
async def upload_dataset(
    project_id: str,
    file: UploadFile = File(...),
    user: Dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service),
    storage = Depends(get_storage_service)
):
    """Upload dataset to a project."""
    try:
        # Verify project exists
        project = db.get_project(project_id, user["user_id"])
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Validate file
        if not file.filename or not file.filename.endswith((".csv", ".xlsx", ".xls")):
            raise HTTPException(status_code=400, detail="Invalid file format")
        
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Check file size
        file_size_mb = len(contents) / (1024 * 1024)
        if file_size_mb > config.MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"File too large (max {config.MAX_FILE_SIZE_MB}MB)"
            )
        
        # Read dataset for metadata
        try:
            if file.filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(contents))
            else:
                df = pd.read_excel(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
        
        if df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")
        
        # Create dataset record
        dataset_id = str(uuid4())
        metadata = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns)
        }
        
        # Save file
        file_path = f"datasets/{user['user_id']}/{project_id}/{dataset_id}/{file.filename}"
        await storage.save_file(file_path, contents)
        
        # Create database record
        dataset = db.create_dataset(
            project_id=project_id,
            filename=file.filename,
            file_path=file_path,
            size_bytes=len(contents),
            metadata=metadata
        )
        
        return {
            "dataset_id": dataset["id"],
            "filename": dataset["filename"],
            "size_bytes": dataset["size_bytes"],
            "metadata": metadata,
            "upload_date": dataset["upload_date"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_id}/datasets")
async def list_datasets(
    project_id: str,
    user: Dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service)
):
    """List all datasets in a project."""
    try:
        # Verify project exists
        project = db.get_project(project_id, user["user_id"])
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        datasets = db.get_project_datasets(project_id)
        return datasets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/datasets/{dataset_id}")
async def get_dataset(
    dataset_id: str,
    user: Dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service)
):
    """Get dataset details."""
    try:
        dataset = db.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Verify user has access to this project
        project = db.get_project(dataset["project_id"], user["user_id"])
        if not project:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return dataset
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYSIS ENDPOINTS ====================

@app.post("/api/datasets/{dataset_id}/analyze")
async def analyze_dataset(
    dataset_id: str,
    user: Dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service),
    storage = Depends(get_storage_service)
):
    """Analyze an uploaded dataset."""
    try:
        # Get dataset
        dataset = db.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Verify access
        project = db.get_project(dataset["project_id"], user["user_id"])
        if not project:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Load file
        file_content = await storage.get_file(dataset["file_path"])
        if not file_content:
            raise HTTPException(status_code=404, detail="Dataset file not found")
        
        # Read dataset
        try:
            if dataset["filename"].endswith(".csv"):
                df = pd.read_csv(io.BytesIO(file_content))
            else:
                df = pd.read_excel(io.BytesIO(file_content))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read dataset: {str(e)}")
        
        # Generate analysis
        profile = profile_dataset(df)
        profile = convert_nan_to_none(profile)
        
        recommendations = generate_recommendations(profile, list(df.columns))
        recommendations = convert_nan_to_none(recommendations)
        
        # Store analysis
        analysis = db.create_analysis(
            dataset_id=dataset_id,
            health_score=profile.get("health_score", 0),
            profile=profile,
            recommendations=recommendations
        )
        
        # Update dataset with health score
        db.update_dataset(dataset_id, {
            "health_score": profile.get("health_score", 0),
            "last_analysis": datetime.utcnow().isoformat()
        })
        
        # Generate visualization data
        visualizations = {
            "missing_values": generate_missing_values_data(df),
            "correlation": convert_nan_to_none(generate_correlation_data(df)),
            "box_plots": convert_nan_to_none(generate_outlier_boxplot_data(df)),
            "quality_heatmap": convert_nan_to_none(generate_data_quality_heatmap(df, profile))
        }
        
        return {
            "analysis_id": analysis["id"],
            "dataset_id": dataset_id,
            "health_score": profile.get("health_score", 0),
            "profile": profile,
            "recommendations": recommendations,
            "visualizations": visualizations,
            "created_at": analysis["created_at"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/datasets/{dataset_id}/analysis")
async def get_latest_analysis(
    dataset_id: str,
    user: Dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service)
):
    """Get latest analysis for a dataset."""
    try:
        dataset = db.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Verify access
        project = db.get_project(dataset["project_id"], user["user_id"])
        if not project:
            raise HTTPException(status_code=403, detail="Access denied")
        
        analysis = db.get_latest_analysis(dataset_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="No analysis found")
        
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CLEANING ENDPOINTS ====================

@app.post("/api/datasets/{dataset_id}/clean")
async def clean_dataset_endpoint(
    dataset_id: str,
    user: Dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service),
    storage = Depends(get_storage_service)
):
    """Apply cleaning to a dataset and generate cleaned version."""
    try:
        # Get dataset
        dataset = db.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Verify access
        project = db.get_project(dataset["project_id"], user["user_id"])
        if not project:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Load file
        file_content = await storage.get_file(dataset["file_path"])
        if not file_content:
            raise HTTPException(status_code=404, detail="Dataset file not found")
        
        # Read dataset
        try:
            if dataset["filename"].endswith(".csv"):
                df = pd.read_csv(io.BytesIO(file_content))
            else:
                df = pd.read_excel(io.BytesIO(file_content))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read dataset: {str(e)}")
        
        # Apply cleaning
        cleaning_config = {
            "remove_empty_rows": True,
            "remove_empty_columns": True,
            "remove_duplicates": True,
            "handle_missing_values": True,
            "missing_value_strategy": "median"
        }
        
        df_cleaned, cleaning_result = apply_cleaning_pipeline(df, cleaning_config)
        cleaning_result = convert_numpy_types(cleaning_result)
        
        # Generate CSV
        output_buffer = io.BytesIO()
        df_cleaned.to_csv(output_buffer, index=False)
        csv_data = output_buffer.getvalue()
        
        # Save cleaned version
        cleaned_filename = f"cleaned_{dataset['filename']}"
        cleaned_path = dataset["file_path"].rsplit("/", 1)[0] + f"/cleaned/{cleaned_filename}"
        await storage.save_file(cleaned_path, csv_data)
        
        return {
            "message": "Dataset cleaned successfully",
            "original_rows": len(df),
            "cleaned_rows": len(df_cleaned),
            "rows_removed": len(df) - len(df_cleaned),
            "cleaning_result": cleaning_result,
            "download_url": f"/api/datasets/{dataset_id}/download-cleaned",
            "cleaned_filename": cleaned_filename
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== REPORTS ENDPOINTS ====================

def build_html_report(filename: str, profile: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> str:
    """Build a simple HTML data quality report."""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Data Quality Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 1100px; margin: 0 auto; background-color: white; padding: 24px; border-radius: 8px; }}
            h1 {{ color: #0f172a; }}
            .metric {{ margin: 8px 0; }}
            .label {{ color: #475569; font-size: 12px; }}
            .value {{ font-size: 20px; font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
            th, td {{ border-bottom: 1px solid #e2e8f0; padding: 8px; text-align: left; font-size: 12px; }}
            th {{ background: #f8fafc; }}
            .rec {{ background: #fef3c7; padding: 10px; border-radius: 6px; margin: 8px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Data Quality Report</h1>
            <p class="label">Dataset: {filename}</p>
            <div class="metric"><span class="label">Rows</span><div class="value">{profile['total_rows']}</div></div>
            <div class="metric"><span class="label">Columns</span><div class="value">{profile['total_columns']}</div></div>
            <div class="metric"><span class="label">Health Score</span><div class="value">{profile['health_score']}</div></div>

            <h2>Column Overview</h2>
            <table>
                <tr>
                    <th>Column</th>
                    <th>Type</th>
                    <th>Non-Null</th>
                    <th>Null</th>
                    <th>Unique</th>
                </tr>
    """

    for col, info in profile.get("datatypes", {}).items():
        html_content += f"""
                <tr>
                    <td>{col}</td>
                    <td>{info.get('datatype')}</td>
                    <td>{info.get('non_null_count')}</td>
                    <td>{info.get('null_count')}</td>
                    <td>{info.get('unique_values')}</td>
                </tr>
        """

    html_content += """
            </table>

            <h2>Recommendations</h2>
    """

    if recommendations:
        for rec in recommendations:
            html_content += f"""
            <div class="rec">
                <strong>{rec.get('column')}</strong>: {rec.get('recommendation')}
            </div>
            """
    else:
        html_content += "<p>No recommendations generated.</p>"

    html_content += """
        </div>
    </body>
    </html>
    """

    return html_content


def build_pdf_report(filename: str, profile: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> bytes:
    """Build a simple PDF report using reportlab."""
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, height - 40, "Data Quality Report")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(40, height - 70, f"Dataset: {filename}")
    pdf.drawString(40, height - 90, f"Rows: {profile.get('total_rows', 0)}")
    pdf.drawString(40, height - 110, f"Columns: {profile.get('total_columns', 0)}")
    pdf.drawString(40, height - 130, f"Health Score: {profile.get('health_score', 0)}")

    y = height - 170
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, y, "Top Recommendations")
    y -= 18
    pdf.setFont("Helvetica", 10)

    if not recommendations:
        pdf.drawString(40, y, "No recommendations generated.")
    else:
        for rec in recommendations[:10]:
            if y < 60:
                pdf.showPage()
                y = height - 40
                pdf.setFont("Helvetica", 10)
            pdf.drawString(40, y, f"- {rec.get('column')}: {rec.get('recommendation')}")
            y -= 14

    pdf.save()
    buffer.seek(0)
    return buffer.read()


@app.get("/api/datasets/{dataset_id}/report/html")
async def get_dataset_html_report(
    dataset_id: str,
    user: Dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service),
    storage = Depends(get_storage_service)
):
    """Generate an HTML report for a dataset."""
    try:
        dataset = db.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        project = db.get_project(dataset["project_id"], user["user_id"])
        if not project:
            raise HTTPException(status_code=403, detail="Access denied")

        file_content = await storage.get_dataset(dataset["file_path"])
        if not file_content:
            raise HTTPException(status_code=404, detail="Dataset file not found")

        if dataset["filename"].endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_content))
        else:
            df = pd.read_excel(io.BytesIO(file_content))

        profile = profile_dataset(df)
        profile = convert_nan_to_none(profile)
        recommendations = generate_recommendations(profile, list(df.columns))
        recommendations = convert_nan_to_none(recommendations)

        html_content = build_html_report(dataset["filename"], profile, recommendations)
        return StreamingResponse(
            io.BytesIO(html_content.encode("utf-8")),
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename=report_{dataset_id}.html"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/datasets/{dataset_id}/report/pdf")
async def get_dataset_pdf_report(
    dataset_id: str,
    user: Dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service),
    storage = Depends(get_storage_service)
):
    """Generate a PDF report for a dataset."""
    try:
        dataset = db.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        project = db.get_project(dataset["project_id"], user["user_id"])
        if not project:
            raise HTTPException(status_code=403, detail="Access denied")

        file_content = await storage.get_dataset(dataset["file_path"])
        if not file_content:
            raise HTTPException(status_code=404, detail="Dataset file not found")

        if dataset["filename"].endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_content))
        else:
            df = pd.read_excel(io.BytesIO(file_content))

        profile = profile_dataset(df)
        profile = convert_nan_to_none(profile)
        recommendations = generate_recommendations(profile, list(df.columns))
        recommendations = convert_nan_to_none(recommendations)

        pdf_bytes = build_pdf_report(dataset["filename"], profile, recommendations)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report_{dataset_id}.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/datasets/{dataset_id}/download-cleaned")
async def download_cleaned_dataset(
    dataset_id: str,
    user: Dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service),
    storage = Depends(get_storage_service)
):
    """Download cleaned dataset."""
    try:
        dataset = db.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Verify access
        project = db.get_project(dataset["project_id"], user["user_id"])
        if not project:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Try to get cleaned version
        cleaned_path = dataset["file_path"].rsplit("/", 1)[0] + f"/cleaned/cleaned_{dataset['filename']}"
        content = await storage.get_file(cleaned_path)
        
        if not content:
            raise HTTPException(status_code=404, detail="Cleaned dataset not found")
        
        return StreamingResponse(
            iter([content]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=cleaned_{dataset['filename']}"}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== API KEY ENDPOINTS ====================

@app.post("/api/account/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    user: Dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service)
):
    """Create a new API key."""
    try:
        # Generate key
        api_key = AuthService.generate_api_key()
        key_hash = AuthService.hash_api_key(api_key)
        
        # Store in database
        stored_key = db.create_api_key(user["user_id"], key_data.name, key_hash)
        
        return {
            "id": stored_key["id"],
            "name": stored_key["name"],
            "key": api_key,  # Only shown once
            "created_at": stored_key["created_at"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/account/api-keys")
async def list_api_keys(
    user: Dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service)
):
    """List user's API keys."""
    try:
        keys = db.get_user_api_keys(user["user_id"])
        
        # Hide actual keys, show preview
        return [
            {
                "id": k["id"],
                "name": k["name"],
                "key_preview": f"{k['key_hash'][:4]}...{k['key_hash'][-4:]}",
                "created_at": k["created_at"],
                "last_used": k.get("last_used")
            }
            for k in keys
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/account/api-keys/{key_id}")
async def delete_api_key(
    key_id: str,
    user: Dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service)
):
    """Delete an API key."""
    try:
        db.delete_api_key(key_id)
        return {"message": "API key deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== LEGACY ENDPOINTS (kept for compatibility) ====================

@app.post("/upload")
async def legacy_upload_dataset(file: UploadFile = File(...)):
    """Legacy upload endpoint (no auth required)."""
    try:
        if not file.filename or not file.filename.endswith((".csv", ".xlsx", ".xls")):
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="File is empty")
        
        try:
            if file.filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(contents))
            else:
                df = pd.read_excel(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
        
        if df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")
        
        preview = convert_nan_to_none(df.to_dict(orient="records"))
        
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
async def legacy_analyze_dataset(file: UploadFile = File(...)):
    """Legacy analyze endpoint (no auth required)."""
    try:
        if not file.filename or not file.filename.endswith((".csv", ".xlsx", ".xls")):
            raise HTTPException(status_code=400, detail="Invalid file format")
        
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="File is empty")
        
        try:
            if file.filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(contents))
            else:
                df = pd.read_excel(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
        
        if df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")
        
        profile = profile_dataset(df)
        profile = convert_nan_to_none(profile)
        
        recommendations = generate_recommendations(profile, list(df.columns))
        recommendations = convert_nan_to_none(recommendations)
        
        categorized_recs = categorize_recommendations(recommendations)
        categorized_recs = convert_nan_to_none(categorized_recs)
        
        basic_code = generate_cleaning_code(profile)
        advanced_code = generate_advanced_pipeline_code(profile)
        
        visualizations = {
            "missing_values": generate_missing_values_data(df),
            "correlation": convert_nan_to_none(generate_correlation_data(df)),
            "box_plots": convert_nan_to_none(generate_outlier_boxplot_data(df)),
            "quality_heatmap": convert_nan_to_none(generate_data_quality_heatmap(df, profile))
        }
        
        return {
            "success": True,
            "filename": file.filename,
            "profile": profile,
            "recommendations": recommendations,
            "categorized_recommendations": categorized_recs,
            "cleaning_code": {
                "basic": basic_code,
                "advanced": advanced_code
            },
            "visualizations": visualizations
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/clean")
async def legacy_clean_dataset(file: UploadFile = File(...)):
    """Legacy clean endpoint (no auth required) - applies automated cleaning."""
    try:
        if not file.filename or not file.filename.endswith((".csv", ".xlsx", ".xls")):
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="File is empty")
        
        try:
            if file.filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(contents))
            else:
                df = pd.read_excel(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
        
        if df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")
        
        # Apply cleaning with default sensible options
        cleaning_config = {
            "remove_empty_rows": True,
            "remove_empty_columns": True,
            "remove_duplicates": True,
            "handle_missing_values": True,
            "missing_value_strategy": "median",
            "handle_outliers": False,
            "convert_types": False
        }
        cleaned_df, clean_result = apply_cleaning_pipeline(df, cleaning_config)
        
        # Generate cleaned CSV
        cleaned_csv = cleaned_df.to_csv(index=False)
        cleaned_csv_base64 = base64.b64encode(cleaned_csv.encode()).decode()
        
        cleaned_filename = f"cleaned_{file.filename}"
        
        return {
            "success": True,
            "filename": file.filename,
            "cleaned_filename": cleaned_filename,
            "cleaned_csv_base64": cleaned_csv_base64,
            "rows_before": len(df),
            "rows_after": len(cleaned_df)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/export/html-report")
async def legacy_export_html_report(file: UploadFile = File(...)):
    """Legacy export HTML report endpoint (no auth required)."""
    try:
        if not file.filename or not file.filename.endswith((".csv", ".xlsx", ".xls")):
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="File is empty")
        
        try:
            if file.filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(contents))
            else:
                df = pd.read_excel(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
        
        if df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")
        
        # Profile the dataset
        profile = profile_dataset(df)
        recommendations = generate_recommendations(profile, list(df.columns))
        
        # Generate HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Data Analysis Report</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                h1 {{ color: #1f2937; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }}
                h2 {{ color: #374151; margin-top: 30px; }}
                .metric {{ background-color: #f9fafb; padding: 15px; border-left: 4px solid #3b82f6; margin: 10px 0; }}
                .metric-label {{ font-weight: bold; color: #1f2937; }}
                .metric-value {{ font-size: 24px; color: #3b82f6; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                table th {{ background-color: #f3f4f6; color: #1f2937; padding: 12px; text-align: left; border-bottom: 2px solid #e5e7eb; }}
                table td {{ padding: 12px; border-bottom: 1px solid #e5e7eb; }}
                table tr:hover {{ background-color: #f9fafb; }}
                .recommendation {{ background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px; margin: 10px 0; border-radius: 4px; }}
                .recommendation-title {{ font-weight: bold; color: #92400e; }}
                .timestamp {{ color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Data Analysis Report</h1>
                <p class="timestamp">Generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h2>Dataset Overview</h2>
                <div class="metric">
                    <div class="metric-label">File Name</div>
                    <div class="metric-value">{file.filename}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Total Rows</div>
                    <div class="metric-value">{profile['total_rows']:,}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Total Columns</div>
                    <div class="metric-value">{profile['total_columns']}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Data Health Score</div>
                    <div class="metric-value">{profile['health_score']:.1f}%</div>
                </div>
                
                <h2>Data Quality Issues</h2>
                <div class="metric">
                    <div class="metric-label">Missing Values</div>
                    <div class="metric-value">{profile['missing_values']['total_missing_values']}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Duplicate Rows</div>
                    <div class="metric-value">{profile['duplicates']['total_duplicate_rows']}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Columns with Outliers</div>
                    <div class="metric-value">{profile['outliers']['total_outlier_columns']}</div>
                </div>
                
                <h2>Detailed Column Analysis</h2>
                <table>
                    <tr>
                        <th>Column</th>
                        <th>Data Type</th>
                        <th>Non-Null</th>
                        <th>Null Count</th>
                        <th>Unique Values</th>
                    </tr>
        """
        
        for col, info in profile['datatypes'].items():
            html_content += f"""
                    <tr>
                        <td>{col}</td>
                        <td>{info['datatype']}</td>
                        <td>{info['non_null_count']}</td>
                        <td>{info['null_count']}</td>
                        <td>{info['unique_values']}</td>
                    </tr>
            """
        
        html_content += """
                </table>
                
                <h2>Recommendations</h2>
        """
        
        for rec in recommendations:
            html_content += f"""
                <div class="recommendation">
                    <div class="recommendation-title">{rec['column']}: {rec['issue']}</div>
                    <p>{rec['recommendation']}</p>
                </div>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        return {
            "success": True,
            "html": html_content,
            "filename": file.filename
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
