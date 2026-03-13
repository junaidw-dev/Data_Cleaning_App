import pandas as pd
import numpy as np
from typing import Dict, List, Any
from scipy import stats


def analyze_missing_values(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze missing values in the dataset with pattern detection."""
    missing_counts = df.isnull().sum()
    missing_percentages = df.isnull().sum() / len(df) * 100
    
    missing_data = {}
    missing_by_row = {}
    
    for col in df.columns:
        if missing_counts[col] > 0:
            missing_data[col] = {
                "count": int(missing_counts[col]),
                "percentage": float(round(missing_percentages[col], 2))
            }
    
    # Analyze missing value patterns per row
    rows_with_missing = df.isnull().sum(axis=1)
    rows_with_missing_count = (rows_with_missing > 0).sum()
    
    return {
        "total_missing_values": int(missing_counts.sum()),
        "columns_with_missing": missing_data,
        "rows_with_missing": int(rows_with_missing_count),
        "missing_percentage_total": float(round((missing_counts.sum() / (len(df) * len(df.columns))) * 100, 2))
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
    """Analyze data types in the dataset with statistics."""
    dtype_info = {}
    
    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null_count = df[col].count()
        unique_count = df[col].nunique()
        
        dtype_info[col] = {
            "datatype": dtype,
            "non_null_count": int(non_null_count),
            "null_count": int(df[col].isnull().sum()),
            "unique_values": int(unique_count)
        }
    
    return dtype_info


def analyze_numeric_columns(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze numeric columns with detailed statistics."""
    numeric_analysis = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        col_data = df[col].dropna()
        
        if len(col_data) > 0:
            numeric_analysis[col] = {
                "min": float(col_data.min()),
                "max": float(col_data.max()),
                "mean": float(col_data.mean()),
                "median": float(col_data.median()),
                "std": float(col_data.std()),
                "variance": float(col_data.var()),
                "q1": float(col_data.quantile(0.25)),
                "q3": float(col_data.quantile(0.75)),
                "skewness": float(col_data.skew()),
                "kurtosis": float(col_data.kurtosis())
            }
    
    return numeric_analysis


def analyze_categorical_columns(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze categorical columns."""
    categorical_analysis = {}
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    for col in categorical_cols:
        col_data = df[col].dropna()
        value_counts = col_data.value_counts()
        
        categorical_analysis[col] = {
            "unique_values": int(col_data.nunique()),
            "most_common": str(value_counts.index[0]) if len(value_counts) > 0 else None,
            "most_common_freq": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
            "least_common": str(value_counts.index[-1]) if len(value_counts) > 0 else None,
            "least_common_freq": int(value_counts.iloc[-1]) if len(value_counts) > 0 else 0,
            "cardinality": len(value_counts)
        }
    
    return categorical_analysis


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


def analyze_correlation(df: pd.DataFrame) -> Dict[str, List[float]]:
    """Analyze correlations between numeric columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) < 2:
        return {}
    
    correlation_matrix = df[numeric_cols].corr()
    
    # Flatten and find high correlations
    high_correlations = {}
    for i in range(len(numeric_cols)):
        for j in range(i + 1, len(numeric_cols)):
            col1, col2 = numeric_cols[i], numeric_cols[j]
            corr_value = correlation_matrix.iloc[i, j]
            
            if abs(corr_value) > 0.7:  # High correlation threshold
                key = f"{col1} <-> {col2}"
                high_correlations[key] = float(round(corr_value, 3))
    
    return high_correlations


def generate_data_quality_summary(df: pd.DataFrame, profile: Dict) -> Dict[str, Any]:
    """Generate a data quality check summary."""
    checks = {
        "has_missing_values": profile["missing_values"]["total_missing_values"] > 0,
        "has_duplicates": profile["duplicates"]["total_duplicate_rows"] > 0,
        "has_outliers": len(profile["outliers"]["columns_with_outliers"]) > 0,
        "all_columns_populated": profile["missing_values"]["total_missing_values"] == 0,
        "no_duplicates": profile["duplicates"]["total_duplicate_rows"] == 0,
        "numeric_columns": int(len(df.select_dtypes(include=[np.number]).columns)),
        "categorical_columns": int(len(df.select_dtypes(include=['object']).columns)),
    }
    return checks


def profile_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """Complete dataset profiling with advanced analytics."""
    missing_analysis = analyze_missing_values(df)
    duplicates_analysis = analyze_duplicates(df)
    outliers_analysis = analyze_outliers(df)
    datatypes_analysis = analyze_datatypes(df)
    numeric_analysis = analyze_numeric_columns(df)
    categorical_analysis = analyze_categorical_columns(df)
    correlation_analysis = analyze_correlation(df)
    health_score = calculate_health_score(df, missing_analysis, duplicates_analysis, outliers_analysis)
    quality_checks = generate_data_quality_summary(df, {
        "missing_values": missing_analysis,
        "duplicates": duplicates_analysis,
        "outliers": outliers_analysis,
        "datatypes": datatypes_analysis
    })
    
    return {
        "missing_values": missing_analysis,
        "duplicates": duplicates_analysis,
        "outliers": outliers_analysis,
        "datatypes": datatypes_analysis,
        "numeric_analysis": numeric_analysis,
        "categorical_analysis": categorical_analysis,
        "correlations": correlation_analysis,
        "quality_checks": quality_checks,
        "health_score": health_score,
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "memory_usage_mb": float(round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2))
    }
