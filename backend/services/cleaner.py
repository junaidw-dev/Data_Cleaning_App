import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple


def remove_duplicates(df: pd.DataFrame, subset: List[str] = None, keep: str = 'first') -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Remove duplicate rows from dataframe."""
    initial_rows = len(df)
    
    if subset:
        df_cleaned = df.drop_duplicates(subset=subset, keep=keep)
    else:
        df_cleaned = df.drop_duplicates(keep=keep)
    
    removed_count = initial_rows - len(df_cleaned)
    
    return df_cleaned, {
        "operation": "remove_duplicates",
        "rows_removed": removed_count,
        "rows_remaining": len(df_cleaned),
        "success": removed_count >= 0
    }


def handle_missing_values(df: pd.DataFrame, strategy: str = 'median', columns: List[str] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Handle missing values in dataframe."""
    df_cleaned = df.copy()
    operations = []
    
    target_cols = columns if columns else df.columns
    
    for col in target_cols:
        if col not in df.columns:
            continue
        
        missing_count = df[col].isnull().sum()
        if missing_count == 0:
            continue
        
        if df[col].dtype in [np.int64, np.float64]:
            # Numeric column
            if strategy == 'median':
                fill_value = df[col].median()
                df_cleaned[col].fillna(fill_value, inplace=True)
            elif strategy == 'mean':
                fill_value = df[col].mean()
                df_cleaned[col].fillna(fill_value, inplace=True)
            elif strategy == 'forward_fill':
                df_cleaned[col].fillna(method='ffill', inplace=True)
                df_cleaned[col].fillna(method='bfill', inplace=True)
            elif strategy == 'zero':
                df_cleaned[col].fillna(0, inplace=True)
        else:
            # Categorical column
            if strategy == 'mode' or strategy == 'median':
                mode_value = df[col].mode()
                if len(mode_value) > 0:
                    fill_value = mode_value[0]
                    df_cleaned[col].fillna(fill_value, inplace=True)
            elif strategy == 'forward_fill':
                df_cleaned[col].fillna(method='ffill', inplace=True)
                df_cleaned[col].fillna(method='bfill', inplace=True)
        
        operations.append({
            "column": col,
            "strategy": strategy,
            "values_filled": missing_count
        })
    
    return df_cleaned, {
        "operation": "handle_missing_values",
        "strategy": strategy,
        "columns_processed": len(operations),
        "operations": operations,
        "success": len(operations) > 0
    }


def handle_outliers(df: pd.DataFrame, method: str = 'iqr', columns: List[str] = None, action: str = 'cap') -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Handle outliers in numeric columns."""
    df_cleaned = df.copy()
    operations = []
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    target_cols = [c for c in (columns if columns else numeric_cols) if c in numeric_cols]
    
    for col in target_cols:
        col_data = df_cleaned[col].dropna()
        
        if len(col_data) == 0:
            continue
        
        if method == 'iqr':
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
        else:  # z-score method
            mean = col_data.mean()
            std = col_data.std()
            lower_bound = mean - (3 * std)
            upper_bound = mean + (3 * std)
        
        outlier_mask = (df_cleaned[col] < lower_bound) | (df_cleaned[col] > upper_bound)
        outlier_count = outlier_mask.sum()
        
        if outlier_count > 0:
            if action == 'cap':
                df_cleaned.loc[df_cleaned[col] < lower_bound, col] = lower_bound
                df_cleaned.loc[df_cleaned[col] > upper_bound, col] = upper_bound
            elif action == 'remove':
                df_cleaned = df_cleaned[~outlier_mask]
            elif action == 'iqr_remove':
                df_cleaned = df_cleaned[(df_cleaned[col] >= lower_bound) & (df_cleaned[col] <= upper_bound)]
            
            operations.append({
                "column": col,
                "method": method,
                "action": action,
                "outliers_found": outlier_count,
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound)
            })
    
    return df_cleaned, {
        "operation": "handle_outliers",
        "method": method,
        "action": action,
        "columns_processed": len(operations),
        "operations": operations,
        "rows_removed": len(df) - len(df_cleaned) if action == 'remove' else 0,
        "success": len(operations) > 0
    }


def convert_data_types(df: pd.DataFrame, conversions: Dict[str, str]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Convert data types for specified columns."""
    df_cleaned = df.copy()
    operations = []
    
    for col, target_type in conversions.items():
        if col not in df.columns:
            continue
        
        try:
            if target_type == 'category':
                df_cleaned[col] = df_cleaned[col].astype('category')
            elif target_type == 'numeric':
                df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')
            elif target_type == 'string':
                df_cleaned[col] = df_cleaned[col].astype(str)
            elif target_type == 'datetime':
                df_cleaned[col] = pd.to_datetime(df_cleaned[col], errors='coerce')
            else:
                df_cleaned[col] = df_cleaned[col].astype(target_type)
            
            operations.append({
                "column": col,
                "new_type": target_type,
                "success": True
            })
        except Exception as e:
            operations.append({
                "column": col,
                "new_type": target_type,
                "success": False,
                "error": str(e)
            })
    
    return df_cleaned, {
        "operation": "convert_data_types",
        "columns_processed": len([op for op in operations if op["success"]]),
        "operations": operations,
        "success": len([op for op in operations if op["success"]]) > 0
    }


def remove_rows_with_all_nulls(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Remove rows where all values are null."""
    initial_rows = len(df)
    df_cleaned = df.dropna(how='all')
    removed_count = initial_rows - len(df_cleaned)
    
    return df_cleaned, {
        "operation": "remove_empty_rows",
        "rows_removed": removed_count,
        "rows_remaining": len(df_cleaned),
        "success": removed_count >= 0
    }


def remove_columns_with_all_nulls(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Remove columns where all values are null."""
    initial_cols = len(df.columns)
    df_cleaned = df.dropna(axis=1, how='all')
    removed_count = initial_cols - len(df_cleaned.columns)
    
    return df_cleaned, {
        "operation": "remove_empty_columns",
        "columns_removed": removed_count,
        "columns_remaining": len(df_cleaned.columns),
        "success": removed_count >= 0
    }


def apply_cleaning_pipeline(df: pd.DataFrame, config: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Apply a complete cleaning pipeline with multiple operations."""
    df_cleaned = df.copy()
    all_operations = []
    
    # Step 1: Remove completely empty rows and columns
    if config.get('remove_empty_rows', False):
        df_cleaned, result = remove_rows_with_all_nulls(df_cleaned)
        all_operations.append(result)
    
    if config.get('remove_empty_columns', False):
        df_cleaned, result = remove_columns_with_all_nulls(df_cleaned)
        all_operations.append(result)
    
    # Step 2: Remove duplicates
    if config.get('remove_duplicates', False):
        df_cleaned, result = remove_duplicates(df_cleaned)
        all_operations.append(result)
    
    # Step 3: Handle missing values
    if config.get('handle_missing_values', False):
        strategy = config.get('missing_value_strategy', 'median')
        df_cleaned, result = handle_missing_values(df_cleaned, strategy=strategy)
        all_operations.append(result)
    
    # Step 4: Handle outliers
    if config.get('handle_outliers', False):
        method = config.get('outlier_method', 'iqr')
        action = config.get('outlier_action', 'cap')
        df_cleaned, result = handle_outliers(df_cleaned, method=method, action=action)
        all_operations.append(result)
    
    # Step 5: Convert data types
    if config.get('convert_types', False) and config.get('type_conversions'):
        df_cleaned, result = convert_data_types(df_cleaned, config['type_conversions'])
        all_operations.append(result)
    
    return df_cleaned, {
        "total_operations": len(all_operations),
        "operations": all_operations,
        "initial_shape": (len(df), len(df.columns)),
        "final_shape": (len(df_cleaned), len(df_cleaned.columns)),
        "success": True
    }
