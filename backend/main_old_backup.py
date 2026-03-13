from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
import pandas as pd
import io
import json
import numpy as np
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add the backend directory to the path so we can import services
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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

def convert_numpy_types(obj):
    """Recursively convert NumPy types to native Python types for JSON serialization."""
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
        
        # Generate visualization data
        print("[ANALYZE] Generating visualization data...")
        visualizations = {
            "missing_values": generate_missing_values_data(df),
            "correlation": convert_nan_to_none(generate_correlation_data(df)),
            "box_plots": convert_nan_to_none(generate_outlier_boxplot_data(df)),
            "quality_heatmap": convert_nan_to_none(generate_data_quality_heatmap(df, profile)),
            "row_quality": convert_nan_to_none(generate_row_quality_analysis(df))
        }

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
            },
            "visualizations": visualizations
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ANALYZE] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ==================== ADVANCED ENDPOINTS ====================

@app.post("/clean")
async def clean_dataset(file: UploadFile = File(...)):
    """Apply automated cleaning to a dataset based on recommended operations."""
    try:
        if not file.filename or not (file.filename.endswith((".csv", ".xlsx", ".xls"))):
            raise HTTPException(status_code=400, detail="Invalid file format")
        
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Read the file
        try:
            if file.filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(contents))
            else:
                df = pd.read_excel(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
        
        if df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")
        
        # Apply default cleaning pipeline
        cleaning_config = {
            "remove_empty_rows": True,
            "remove_empty_columns": True,
            "remove_duplicates": True,
            "handle_missing_values": True,
            "missing_value_strategy": "median",
            "handle_outliers": False,
        }
        
        df_cleaned, cleaning_result = apply_cleaning_pipeline(df, cleaning_config)
        
        # Convert NumPy types in cleaning_result
        cleaning_result = convert_numpy_types(cleaning_result)
        
        # Profile the cleaned dataset
        profile = profile_dataset(df_cleaned)
        profile = convert_nan_to_none(profile)
        
        # Convert cleaned dataframe to CSV format for download
        output_buffer = io.BytesIO()
        df_cleaned.to_csv(output_buffer, index=False)
        csv_data = output_buffer.getvalue()
        
        return {
            "success": True,
            "original_filename": file.filename,
            "cleaned_filename": f"cleaned_{file.filename}",
            "original_shape": (len(df), len(df.columns)),
            "cleaned_shape": (len(df_cleaned), len(df_cleaned.columns)),
            "cleaning_result": cleaning_result,
            "profile_after": profile,
            "cleaned_csv_base64": __import__('base64').b64encode(csv_data).decode('utf-8')
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[CLEAN] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during cleaning: {str(e)}")


@app.post("/natural-language-summary")
async def get_natural_language_summary(file: UploadFile = File(...)):
    """Generate natural language summary of the dataset."""
    try:
        contents = await file.read()
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        profile = profile_dataset(df)
        profile = convert_nan_to_none(profile)
        
        # Generate summary
        summary = generate_dataset_summary(df, profile)
        
        return {
            "success": True,
            "summary": summary
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/export/html-report")
async def export_html_report(file: UploadFile = File(...)):
    """Export a comprehensive HTML report of the data analysis."""
    try:
        contents = await file.read()
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        if df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")
        
        # Generate all analysis
        profile = profile_dataset(df)
        profile = convert_nan_to_none(profile)
        recommendations = generate_recommendations(profile, list(df.columns))
        summary = generate_dataset_summary(df, profile)
        
        # Generate HTML report
        html_content = generate_html_report(file.filename, df, profile, recommendations, summary)
        
        return {
            "success": True,
            "html": html_content
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ==================== HELPER FUNCTIONS ====================

def generate_dataset_summary(df: pd.DataFrame, profile: Dict) -> str:
    """Generate natural language summary of the dataset."""
    health_score = profile.get('health_score', 0)
    total_rows = profile.get('total_rows', 0)
    total_cols = profile.get('total_columns', 0)
    missing_vals = profile.get('missing_values', {}).get('total_missing_values', 0)
    duplicates = profile.get('duplicates', {}).get('total_duplicate_rows', 0)
    outliers_count = sum(v.get('count', 0) for v in profile.get('outliers', {}).get('columns_with_outliers', {}).values())
    
    if health_score >= 80:
        quality_text = "is in excellent condition"
    elif health_score >= 60:
        quality_text = "is in good condition with some issues to address"
    elif health_score >= 40:
        quality_text = "requires significant data cleaning"
    else:
        quality_text = "requires immediate attention for data quality"
    
    summary = f"Your dataset contains {total_rows} rows and {total_cols} columns. "
    summary += f"The overall data health score is {health_score}/100, indicating that the dataset {quality_text}. "
    
    if missing_vals > 0:
        missing_pct = round((missing_vals / (total_rows * total_cols)) * 100, 1) if (total_rows * total_cols) > 0 else 0
        summary += f"There are {missing_vals} missing values ({missing_pct}% of total cells). "
    else:
        summary += "There are no missing values. "
    
    if duplicates > 0:
        dup_pct = round((duplicates / total_rows) * 100, 1) if total_rows > 0 else 0
        summary += f"Found {duplicates} duplicate rows ({dup_pct}%). "
    
    if outliers_count > 0:
        summary += f"Detected {outliers_count} potential outliers in numeric columns. "
    
    numeric_cols = len(df.select_dtypes(include=[np.number]).columns)
    categorical_cols = len(df.select_dtypes(include=['object']).columns)
    
    summary += f"The dataset has {numeric_cols} numeric columns and {categorical_cols} categorical columns. "
    
    if health_score < 80:
        summary += "We recommend reviewing the generated cleaning recommendations to improve data quality."
    else:
        summary += "The dataset is ready for analysis and modeling."
    
    return summary


def generate_html_report(filename: str, df: pd.DataFrame, profile: Dict, recommendations: List, summary: str) -> str:
    """Generate a comprehensive HTML report."""
    health_score = profile.get('health_score', 0)
    score_class = 'excellent' if health_score >= 80 else 'good' if health_score >= 60 else 'fair' if health_score >= 40 else 'poor'
    
    datatypes_rows = ''.join(f'<tr><td><code>{col}</code></td><td>{data["datatype"]}</td><td>{data["non_null_count"]}</td><td>{data["null_count"]}</td><td>{data["unique_values"]}</td></tr>' for col, data in profile.get('datatypes', {}).items())
    
    recommendations_html = ''.join(f'<div class="recommendation"><div class="recommendation-title"><span class="badge badge-{rec.get("severity", "low").lower()}">{rec.get("severity", "Low")}</span> {rec.get("column")} - {rec.get("issue")}</div><div class="recommendation-text"><strong>Problem:</strong> {rec.get("problem")}<br/><strong>Action:</strong> {rec.get("recommendation")}</div></div>' for rec in recommendations[:10])
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Quality Report - {filename}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }}
        .container {{ max-width: 1000px; margin: 0 auto; padding: 20px; background: white; }}
        .header {{ border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }}
        .header h1 {{ color: #007bff; font-size: 28px; margin-bottom: 10px; }}
        .header p {{ color: #666; line-height: 1.6; }}
        .section {{ margin-bottom: 40px; }}
        .section h2 {{ color: #333; font-size: 22px; border-bottom: 1px solid #ddd; padding-bottom: 10px; margin-bottom: 20px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }}
        .metric-label {{ color: #666; font-size: 12px; text-transform: uppercase; margin-bottom: 5px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
        .health-score {{ text-align: center; }}
        .health-score-circle {{ width: 120px; height: 120px; margin: 0 auto 15px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 48px; font-weight: bold; color: white; }}
        .health-score-excellent {{ background: #28a745; }}
        .health-score-good {{ background: #ffc107; }}
        .health-score-fair {{ background: #ff9800; }}
        .health-score-poor {{ background: #dc3545; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; font-weight: 600; }}
        tr:hover {{ background: #f8f9fa; }}
        .recommendation {{ background: #f0f7ff; padding: 15px; border-radius: 5px; margin-bottom: 10px; border-left: 4px solid #007bff; }}
        .recommendation-title {{ font-weight: 600; color: #007bff; }}
        .recommendation-text {{ color: #666; margin-top: 5px; }}
        .badge {{ display: inline-block; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; margin-right: 5px; }}
        .badge-high {{ background: #f8d7da; color: #721c24; }}
        .badge-medium {{ background: #fff3cd; color: #856404; }}
        .badge-low {{ background: #d1ecf1; color: #0c5460; }}
        .footer {{ text-align: center; padding-top: 30px; border-top: 1px solid #ddd; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Data Quality Analysis Report</h1>
            <p><strong>File:</strong> {filename}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="section">
            <h2>Executive Summary</h2>
            <p style="line-height: 1.8; color: #555;">{summary}</p>
        </div>
        
        <div class="section">
            <h2>Data Overview</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Total Rows</div>
                    <div class="metric-value">{profile.get('total_rows', 0)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Total Columns</div>
                    <div class="metric-value">{profile.get('total_columns', 0)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Memory Usage</div>
                    <div class="metric-value">{profile.get('memory_usage_mb', 0)} MB</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Health Score</h2>
            <div class="health-score">
                <div class="health-score-circle health-score-{score_class}">{health_score}</div>
                <p style="color: #666;">Overall Data Quality Score (0-100)</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Data Quality Issues</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Missing Values</div>
                    <div class="metric-value">{profile.get('missing_values', {}).get('total_missing_values', 0)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Duplicate Rows</div>
                    <div class="metric-value">{profile.get('duplicates', {}).get('total_duplicate_rows', 0)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Outliers Found</div>
                    <div class="metric-value">{sum(v.get('count', 0) for v in profile.get('outliers', {}).get('columns_with_outliers', {}).values())}</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Column Information</h2>
            <table>
                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Data Type</th>
                        <th>Non-Null</th>
                        <th>Null</th>
                        <th>Unique</th>
                    </tr>
                </thead>
                <tbody>
                    {datatypes_rows}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>Recommendations</h2>
            {recommendations_html}
        </div>
        
        <div class="footer">
            <p>Report generated by AI Data Cleaner • {datetime.now().strftime('%Y-%m-%d')}</p>
        </div>
    </div>
</body>
</html>"""
    
    return html