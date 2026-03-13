"""
Error handling utilities for the AI Data Cleaner API.
Provides comprehensive error handling, validation, and safe error responses.
"""

import logging
from typing import Any, Dict, Optional
from fastapi import HTTPException
import traceback

# Configure logging
logger = logging.getLogger(__name__)


class DataCleanerError(Exception):
    """Base exception for AI Data Cleaner."""
    
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR", status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(DataCleanerError):
    """File/Data validation errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR", 400)


class FileFormatError(ValidationError):
    """Unsupported file format error."""
    
    def __init__(self, filename: str, supported_formats: list = None):
        formats = supported_formats or [".csv", ".xlsx", ".xls"]
        formats_str = ", ".join(formats)
        message = f"Unsupported file format: {filename}. Supported formats: {formats_str}"
        super().__init__(message)
        self.error_code = "FILE_FORMAT_ERROR"


class FileSizeError(ValidationError):
    """File too large error."""
    
    def __init__(self, filename: str, size_mb: float, max_size_mb: float = 100):
        message = f"File '{filename}' is too large ({size_mb:.1f}MB). Maximum allowed: {max_size_mb}MB."
        super().__init__(message)
        self.error_code = "FILE_SIZE_ERROR"


class FileReadError(DataCleanerError):
    """Error reading/parsing file."""
    
    def __init__(self, filename: str, original_error: str):
        message = f"Failed to read file '{filename}': {original_error}"
        super().__init__(message, "FILE_READ_ERROR", 400)


class DatasetError(DataCleanerError):
    """Dataset validation errors."""
    
    def __init__(self, message: str, error_code: str = "DATASET_ERROR"):
        super().__init__(message, error_code, 400)


class EmptyDatasetError(DatasetError):
    """Dataset is empty error."""
    
    def __init__(self):
        super().__init__("Dataset is empty. Please upload a non-empty file.", "EMPTY_DATASET_ERROR")


class ProcessingError(DataCleanerError):
    """Data processing errors."""
    
    def __init__(self, message: str, operation: str = None):
        if operation:
            message = f"Error during {operation}: {message}"
        super().__init__(message, "PROCESSING_ERROR", 500)


class ProfilingError(ProcessingError):
    """Data profiling errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "profiling")
        self.error_code = "PROFILING_ERROR"


class CleaningError(ProcessingError):
    """Data cleaning errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "cleaning")
        self.error_code = "CLEANING_ERROR"


def handle_error(error: Exception, context: str = "", fallback_message: str = None) -> HTTPException:
    """
    Convert any exception to appropriate HTTPException.
    
    Args:
        error: The exception to handle
        context: Additional context about the error
        fallback_message: Message to use if error message is empty
    
    Returns:
        HTTPException ready to be raised
    """
    error_message = str(error) or fallback_message or "An unknown error occurred"
    error_code = "UNKNOWN_ERROR"
    status_code = 500
    
    if isinstance(error, DataCleanerError):
        error_message = error.message
        error_code = error.error_code
        status_code = error.status_code
    elif isinstance(error, HTTPException):
        raise error
    
    # Log the error
    logger.error(f"[{error_code}] {context}: {error_message}", exc_info=error)
    
    # Create detailed response
    detail = {
        "error": error_code,
        "message": error_message,
    }
    
    if context:
        detail["context"] = context
    
    return HTTPException(status_code=status_code, detail=detail)


def validate_file(filename: str, contents: bytes, max_size_mb: float = 100) -> Dict[str, Any]:
    """
    Validate uploaded file.
    
    Args:
        filename: Name of the file
        contents: File bytes
        max_size_mb: Maximum file size in MB
    
    Returns:
        Dictionary with validation results
    
    Raises:
        ValidationError: If file is invalid
    """
    if not filename:
        raise ValidationError("No filename provided")
    
    # Check format
    valid_formats = {".csv", ".xlsx", ".xls"}
    file_ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    
    if file_ext not in valid_formats:
        raise FileFormatError(filename, list(valid_formats))
    
    # Check size
    if not contents:
        raise ValidationError(f"File '{filename}' is empty")
    
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > max_size_mb:
        raise FileSizeError(filename, size_mb, max_size_mb)
    
    return {
        "filename": filename,
        "size_bytes": len(contents),
        "size_mb": size_mb,
        "format": file_ext
    }


def validate_dataframe(df: Any, filename: str = "dataset") -> Dict[str, Any]:
    """
    Validate pandas DataFrame.
    
    Args:
        df: Pandas DataFrame to validate
        filename: Name of the dataset for error messages
    
    Returns:
        Dictionary with validation results
    
    Raises:
        DatasetError: If DataFrame is invalid
    """
    if df is None:
        raise DatasetError(f"Failed to read {filename}. Invalid file format or corrupted data.")
    
    if df.empty:
        raise EmptyDatasetError()
    
    if len(df.columns) == 0:
        raise DatasetError("Dataset has no columns.", "NO_COLUMNS_ERROR")
    
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
    }


def safe_profile_dataset(df, error_context: str = "dataset profiling"):
    """
    Safely profile a dataset with error handling.
    
    Args:
        df: Pandas DataFrame to profile
        error_context: Context for error messages
    
    Returns:
        Profile dictionary or None if error
    """
    try:
        from services.profiler import profile_dataset as original_profile
        profile = original_profile(df)
        return profile
    except Exception as e:
        logger.error(f"Error in {error_context}", exc_info=e)
        raise ProfilingError(str(e))


def safe_generate_recommendations(profile, columns, error_context: str = "recommendation generation"):
    """
    Safely generate recommendations with error handling.
    
    Args:
        profile: Data profile dictionary
        columns: List of column names
        error_context: Context for error messages
    
    Returns:
        Recommendations list
    """
    try:
        from services.recommendations import generate_recommendations as original_gen
        recommendations = original_gen(profile, columns)
        return recommendations
    except Exception as e:
        logger.error(f"Error in {error_context}", exc_info=e)
        logger.warning("Returning empty recommendations due to error")
        return []


def safe_clean_dataset(df, config, error_context: str = "data cleaning"):
    """
    Safely clean a dataset with error handling.
    
    Args:
        df: Pandas DataFrame to clean
        config: Cleaning configuration dictionary
        error_context: Context for error messages
    
    Returns:
        Tuple of (cleaned_df, result_dict) or (None, error_dict) if error
    """
    try:
        from services.cleaner import apply_cleaning_pipeline
        cleaned_df, result = apply_cleaning_pipeline(df, config)
        return cleaned_df, result
    except Exception as e:
        logger.error(f"Error in {error_context}", exc_info=e)
        raise CleaningError(str(e))


def safe_conversion_nan_to_none(obj):
    """
    Safely convert NaN/Inf values to None for JSON serialization.
    
    Args:
        obj: Object to convert (can be dict, list, float, etc)
    
    Returns:
        Converted object safe for JSON serialization
    """
    import numpy as np
    
    try:
        if isinstance(obj, float):
            if np.isnan(obj) or np.isinf(obj):
                return None
            return obj
        elif isinstance(obj, dict):
            return {k: safe_conversion_nan_to_none(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [safe_conversion_nan_to_none(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return safe_conversion_nan_to_none(obj.tolist())
        return obj
    except Exception as e:
        logger.warning(f"Error converting value to JSON-safe format: {e}")
        return None


def create_error_response(error_code: str, message: str, details: dict = None) -> Dict[str, Any]:
    """
    Create a consistent error response format.
    
    Args:
        error_code: Error code identifier
        message: Human-readable error message
        details: Additional error details
    
    Returns:
        Dictionary with error response
    """
    response = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    return response


def log_error_details(func_name: str, error: Exception, context: dict = None):
    """
    Log detailed error information for debugging.
    
    Args:
        func_name: Name of the function where error occurred
        error: The exception
        context: Additional context information
    """
    logger.error(f"Error in {func_name}: {str(error)}")
    logger.error(f"Error type: {type(error).__name__}")
    logger.error(f"Traceback:\n{traceback.format_exc()}")
    
    if context:
        logger.error(f"Context: {context}")
