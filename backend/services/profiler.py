import pandas as pd
import numpy as np
from typing import Dict, List, Any


def analyze_missing_values(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze missing values in the dataset."""
    missing_counts = df.isnull().sum()
    missing_percentages = df.isnull().sum() / len(df) * 100
    
    missing_data = {}
    for col in df.columns:
        if missing_counts[col] > 0:
            missing_data[col] = {
                "count": int(missing_counts[col]),
                "percentage": float(round(missing_percentages[col], 2))
            }
    
    return {
        "total_missing_values": int(missing_counts.sum()),
        "columns_with_missing": missing_data
    }


def analyze_duplicates(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze duplicate rows in the dataset."""
    total_duplicates = df.duplicated().sum()
    duplicate_columns = {}
    
    for col in df.columns:
        col_duplicates = df[col].duplicated().sum()
        if col_duplicates > 0:
            duplicate_columns[col] = int(col_duplicates)
    
    return {
        "total_duplicate_rows": int(total_duplicates),
        "duplicate_percentage": float(round(total_duplicates / len(df) * 100, 2)),
        "columns_with_duplicates": duplicate_columns
    }


def analyze_outliers(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect outliers in numeric columns using IQR method."""
    outliers_data = {}
    
    for col in df.select_dtypes(include=[np.number]).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outlier_count = len(df[(df[col] < lower_bound) | (df[col] > upper_bound)])
        
        if outlier_count > 0:
            outliers_data[col] = {
                "count": int(outlier_count),
                "percentage": float(round(outlier_count / len(df) * 100, 2)),
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound)
            }
    
    return {
        "columns_with_outliers": outliers_data,
        "total_outlier_columns": len(outliers_data)
    }


def analyze_datatypes(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze data types in the dataset."""
    dtype_info = {}
    
    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null_count = df[col].count()
        
        dtype_info[col] = {
            "datatype": dtype,
            "non_null_count": int(non_null_count),
            "null_count": int(df[col].isnull().sum()),
            "unique_values": int(df[col].nunique())
        }
    
    return dtype_info


def calculate_health_score(df: pd.DataFrame, missing_analysis: Dict, duplicates_analysis: Dict, outliers_analysis: Dict) -> int:
    """Calculate overall dataset health score (0-100)."""
    score = 100
    total_cells = len(df) * len(df.columns)
    
    # Penalty for missing values (30 points max)
    missing_percentage = (missing_analysis["total_missing_values"] / total_cells) * 100
    missing_penalty = min(30, (missing_percentage / 100) * 30)
    score -= missing_penalty
    
    # Penalty for duplicates (20 points max)
    duplicate_penalty = min(20, duplicates_analysis["duplicate_percentage"] / 5)
    score -= duplicate_penalty
    
    # Penalty for outliers (20 points max)
    outlier_count = sum(data["count"] for data in outliers_analysis["columns_with_outliers"].values())
    outlier_percentage = (outlier_count / total_cells) * 100
    outlier_penalty = min(20, (outlier_percentage / 100) * 20)
    score -= outlier_penalty
    
    # Penalty for data type issues (10 points max)
    dtypes = analyze_datatypes(df)
    object_cols = sum(1 for col in dtypes if "object" in dtypes[col]["datatype"])
    dtype_penalty = min(10, (object_cols / len(df.columns)) * 10)
    score -= dtype_penalty
    
    return max(0, int(score))


def profile_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """Complete dataset profiling."""
    missing_analysis = analyze_missing_values(df)
    duplicates_analysis = analyze_duplicates(df)
    outliers_analysis = analyze_outliers(df)
    datatypes_analysis = analyze_datatypes(df)
    health_score = calculate_health_score(df, missing_analysis, duplicates_analysis, outliers_analysis)
    
    return {
        "missing_values": missing_analysis,
        "duplicates": duplicates_analysis,
        "outliers": outliers_analysis,
        "datatypes": datatypes_analysis,
        "health_score": health_score,
        "total_rows": len(df),
        "total_columns": len(df.columns)
    }
