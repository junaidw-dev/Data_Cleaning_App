import pandas as pd
import numpy as np
from typing import Dict, List, Any


def generate_missing_values_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate data for missing values visualization."""
    missing_counts = df.isnull().sum()
    
    missing_data = {
        "labels": [],
        "values": [],
        "percentages": []
    }
    
    for col in df.columns:
        if missing_counts[col] > 0:
            missing_data["labels"].append(col)
            missing_data["values"].append(int(missing_counts[col]))
            missing_data["percentages"].append(float(round((missing_counts[col] / len(df)) * 100, 2)))
    
    return missing_data


def generate_numeric_distribution_data(df: pd.DataFrame, column: str, bins: int = 20) -> Dict[str, Any]:
    """Generate histogram data for numeric columns."""
    if column not in df.columns or df[column].dtype not in [np.int64, np.float64]:
        return {}
    
    col_data = df[column].dropna()
    counts, edges = np.histogram(col_data, bins=bins)
    
    return {
        "column": column,
        "bins": bins,
        "counts": [int(c) for c in counts],
        "edges": [float(e) for e in edges],
        "mean": float(col_data.mean()),
        "median": float(col_data.median()),
        "min": float(col_data.min()),
        "max": float(col_data.max())
    }


def generate_categorical_distribution_data(df: pd.DataFrame, column: str, top_n: int = 10) -> Dict[str, Any]:
    """Generate bar chart data for categorical columns."""
    if column not in df.columns or df[column].dtype != 'object':
        return {}
    
    col_data = df[column].dropna()
    value_counts = col_data.value_counts().head(top_n)
    
    return {
        "column": column,
        "labels": [str(k) for k in value_counts.index.tolist()],
        "values": [int(v) for v in value_counts.values.tolist()],
        "remaining": int(col_data.nunique() - len(value_counts)) if col_data.nunique() > top_n else 0
    }


def generate_correlation_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate correlation matrix data for numeric columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) < 2:
        return {"columns": [], "correlation_matrix": []}
    
    corr_matrix = df[numeric_cols].corr()
    
    # Convert to list format for JSON serialization
    correlation_data = {
        "columns": numeric_cols,
        "correlation_matrix": [
            [float(corr_matrix.iloc[i, j]) for j in range(len(numeric_cols))]
            for i in range(len(numeric_cols))
        ]
    }
    
    return correlation_data


def generate_outlier_boxplot_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate boxplot data for outlier visualization."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    boxplot_data = {}
    
    for col in numeric_cols:
        col_data = df[col].dropna()
        if len(col_data) > 0:
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            
            boxplot_data[col] = {
                "min": float(col_data.min()),
                "q1": float(Q1),
                "median": float(col_data.median()),
                "q3": float(Q3),
                "max": float(col_data.max()),
                "lower_whisker": float(Q1 - 1.5 * IQR),
                "upper_whisker": float(Q3 + 1.5 * IQR),
                "outlier_count": int(len(col_data[(col_data < Q1 - 1.5 * IQR) | (col_data > Q3 + 1.5 * IQR)]))
            }
    
    return boxplot_data


def generate_data_quality_heatmap(df: pd.DataFrame, profile: Dict) -> Dict[str, Any]:
    """Generate heatmap data showing data quality by column."""
    heatmap_data = {
        "columns": list(df.columns),
        "metrics": {
            "completeness": [],  # 1 - (missing_count / total_rows)
            "uniqueness": [],     # unique_values / total_rows
            "validity": []        # for numeric: percent within expected range
        }
    }
    
    for col in df.columns:
        # Completeness
        missing_pct = (df[col].isnull().sum() / len(df)) * 100
        completeness = 100 - missing_pct
        heatmap_data["metrics"]["completeness"].append(float(round(completeness, 2)))
        
        # Uniqueness
        uniqueness = (df[col].nunique() / len(df)) * 100
        heatmap_data["metrics"]["uniqueness"].append(float(round(uniqueness, 2)))
        
        # Validity (simplified: for numeric columns, check if within reasonable range)
        if df[col].dtype in [np.int64, np.float64]:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                valid_count = len(col_data[(col_data >= Q1 - 1.5 * IQR) & (col_data <= Q3 + 1.5 * IQR)])
                validity = (valid_count / len(col_data)) * 100
            else:
                validity = 0
        else:
            validity = 100  # Assume categorical data is valid
        
        heatmap_data["metrics"]["validity"].append(float(round(validity, 2)))
    
    return heatmap_data


def generate_row_quality_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze data quality at row level."""
    missing_per_row = df.isnull().sum(axis=1)
    
    row_quality = {
        "rows_with_no_missing": int((missing_per_row == 0).sum()),
        "rows_with_missing": int((missing_per_row > 0).sum()),
        "avg_missing_per_row": float(round(missing_per_row.mean(), 2)),
        "max_missing_in_row": int(missing_per_row.max()),
        "distribution": {}
    }
    
    # Distribution of missing values per row
    for missing_count in sorted(missing_per_row.unique()):
        row_count = int((missing_per_row == missing_count).sum())
        if row_count > 0:
            row_quality["distribution"][int(missing_count)] = row_count
    
    return row_quality
