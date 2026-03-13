from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# ==================== User Models ====================

class UserCreate(BaseModel):
    """User registration model."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str

class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """User response model."""
    id: str
    email: str
    full_name: str
    created_at: datetime
    updated_at: datetime
    subscription_tier: str = "free"

class PasswordReset(BaseModel):
    """Password reset model."""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8)

# ==================== Authentication Models ====================

class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str
    user: UserResponse

class AuthPayload(BaseModel):
    """JWT payload."""
    user_id: str
    email: str

# ==================== Project Models ====================

class ProjectCreate(BaseModel):
    """Create project model."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    
class ProjectUpdate(BaseModel):
    """Update project model."""
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    """Project response model."""
    id: str
    user_id: str
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    dataset_count: int = 0

# ==================== Dataset Models ====================

class DatasetMetadata(BaseModel):
    """Dataset metadata."""
    rows: int
    columns: int
    column_names: List[str]
    size_bytes: int

class DatasetCreate(BaseModel):
    """Create dataset model."""
    project_id: str
    filename: str

class DatasetResponse(BaseModel):
    """Dataset response model."""
    id: str
    project_id: str
    filename: str
    file_path: str
    size_bytes: int
    upload_date: datetime
    health_score: Optional[float] = None
    metadata: Optional[DatasetMetadata] = None
    last_analysis: Optional[datetime] = None

# ==================== Analysis Models ====================

class ColumnProfile(BaseModel):
    """Profile for a single column."""
    name: str
    type: str
    missing_count: int
    missing_pct: float
    unique_count: int
    duplicates_count: int = 0
    
    # Numeric columns
    mean: Optional[float] = None
    median: Optional[float] = None
    std: Optional[float] = None
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    
    # Text columns
    avg_length: Optional[float] = None
    max_length: Optional[int] = None

class DataQualityProfile(BaseModel):
    """Overall data quality profile."""
    rows: int
    columns: int
    memory_usage: float
    duplicate_rows: int
    missing_cells: int
    complete_rows: int
    column_profiles: List[ColumnProfile]

class Recommendation(BaseModel):
    """Cleaning recommendation."""
    id: str
    type: str  # missing_values, duplicates, outliers, datatype
    severity: str  # low, medium, high, critical
    column: Optional[str] = None
    description: str
    suggestion: str
    impact: str
    code_snippet: Optional[str] = None

class AnalysisResult(BaseModel):
    """Analysis result model."""
    id: str
    dataset_id: str
    health_score: float
    profile: DataQualityProfile
    recommendations: List[Recommendation]
    created_at: datetime

class AnalysisResultResponse(BaseModel):
    """Analysis result response."""
    id: str
    dataset_id: str
    health_score: float
    created_at: datetime
    profile: Optional[Dict[str, Any]] = None

# ==================== Team Models ====================

class TeamMemberCreate(BaseModel):
    """Add team member model."""
    email: EmailStr
    role: str = "editor"  # owner, editor, viewer

class TeamMemberResponse(BaseModel):
    """Team member response."""
    id: str
    project_id: str
    user_id: str
    email: str
    full_name: str
    role: str
    created_at: datetime

# ==================== API Key Models ====================

class APIKeyCreate(BaseModel):
    """Create API key model."""
    name: str = Field(..., min_length=1, max_length=50)

class APIKeyResponse(BaseModel):
    """API key response (only shown once)."""
    id: str
    name: str
    key: str
    created_at: datetime

class APIKeyListResponse(BaseModel):
    """API key list item (without full key)."""
    id: str
    name: str
    key_preview: str  # e.g., "sk_live_****abcd"
    created_at: datetime
    last_used: Optional[datetime] = None

# ==================== Report Models ====================

class ReportRequest(BaseModel):
    """Report generation request."""
    format: str = "html"  # html or pdf
    include_recommendations: bool = True
    include_code: bool = True

class ReportResponse(BaseModel):
    """Report response."""
    dataset_id: str
    created_at: datetime
    format: str
    url: str

# ==================== Error Models ====================

class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str
    error_code: Optional[str] = None
    status_code: int
