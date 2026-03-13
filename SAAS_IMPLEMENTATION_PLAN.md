# SaaS Transformation Implementation Plan

**Project:** AI Data Cleaner → Production SaaS Platform  
**Start Date:** March 13, 2026  
**Current Stack:** Next.js, FastAPI, Supabase, Tailwind CSS

---

## Implementation Phases

### Phase 1: Core Infrastructure & Authentication (Weeks 1-2)

#### 1.1 Database Schema Setup
- Create Supabase tables:
  - `users` (email, password_hash, subscription_tier, created_at)
  - `projects` (id, user_id, name, description, created_at, updated_at)
  - `datasets` (id, project_id, filename, file_path, size, upload_date, metadata)
  - `analysis_results` (id, dataset_id, health_score, profiling_data, recommendations, created_at)
  - `team_members` (id, project_id, user_id, role, created_at)
  - `api_keys` (id, user_id, key_hash, created_at)

#### 1.2 User Authentication
- Implement NextAuth.js with Supabase provider
- Create auth API routes:
  - `/api/auth/signup` - User registration with email verification
  - `/api/auth/login` - JWT token generation
  - `/api/auth/logout` - Session cleanup
  - `/api/auth/password-reset` - Password reset flow
  - `/api/auth/verify-email` - Email verification

#### 1.3 Protected Routes & Middleware
- Create middleware to protect authenticated routes
- Implement user context provider for React
- Create session management hooks

---

### Phase 2: User Dashboard & Project Management (Weeks 2-3)

#### 2.1 Dashboard Page
Features:
- Display user projects grid
- Show recent analyses
- Quick stats (total datasets, avg health score)
- Recent activity timeline

#### 2.2 Project Management
- Create project CRUD operations
- Project settings page
- Project deletion with confirmation

#### 2.3 Dataset List View
- Display all datasets in a project
- Sort/filter by upload date, health score
- Quick actions (analyze, download, delete)

---

### Phase 3: Dataset Management & Persistence (Weeks 3-4)

#### 3.1 File Storage
- Local storage: `/data/uploads/{user_id}/{project_id}/{dataset_id}/`
- S3 integration (stub for production):
  - Abstract storage layer in backend
  - Use boto3 for S3 operations

#### 3.2 Dataset Metadata
- Store in database:
  - Filename, size, row count, column count
  - Upload timestamp, data types
  - File path reference

#### 3.3 Enhanced Upload Handler
- Validate file before storage
- Generate unique dataset ID
- Create database record
- Trigger initial profiling

---

### Phase 4: Advanced Profiling & Health Scoring (Weeks 4-5)

#### 4.1 Enhanced Data Profiler
**File:** `backend/services/profiler.py`

Generate comprehensive profile:
- Column statistics (mean, median, std, min, max)
- Missing value percentage per column
- Duplicate row detection
- Outlier detection (IQR method)
- Data type inference and validation
- Unique value counts
- Text length analysis

Return structure:
```python
{
    "overview": {
        "rows": int,
        "columns": int,
        "memory_usage": float,
        "duplicate_rows": int,
        "missing_cells": int
    },
    "columns": [
        {
            "name": str,
            "type": str,
            "missing_pct": float,
            "unique_count": int,
            "stats": {...},
            "outliers": [...]
        }
    ]
}
```

#### 4.2 Health Score Calculation
Algorithm:
```
base_score = 100
- missing_values_penalty: (missing_pct * 10)
- duplicates_penalty: (duplicate_rows / total_rows * 20)
- outliers_penalty: (outlier_count / total_rows * 15)
- data_type_issues_penalty: (issues_count * 5)
health_score = max(0, min(100, base_score - penalties))
```

---

### Phase 5: Data Visualization (Weeks 5-6)

#### 5.1 Chart Components
Create reusable chart components:
- Missing value heatmap (Recharts)
- Numeric column distributions (histograms)
- Categorical bar charts
- Correlation heatmap
- Box plots for outlier detection
- Data quality gauge

#### 5.2 Visualization Data Generation
**File:** `backend/services/visualization.py` (enhance existing)

Endpoints:
- `/api/analyze/{dataset_id}/visualizations` - Get all chart data

---

### Phase 6: Cleaning Recommendations & Code Generation (Weeks 6-7)

#### 6.1 Intelligent Recommendations
**File:** `backend/services/recommendations.py`

Example recommendations:
```json
[
  {
    "id": 1,
    "type": "missing_values",
    "severity": "high",
    "column": "age",
    "description": "15.2% missing values",
    "suggestion": "Fill with median value",
    "impact": "Increases completeness, maintains distribution"
  },
  {
    "id": 2,
    "type": "duplicates",
    "severity": "medium",
    "description": "42 duplicate rows detected",
    "suggestion": "Remove duplicates based on key columns",
    "impact": "Removes noise, improves data integrity"
  }
]
```

#### 6.2 Code Generation
**File:** `backend/services/code_generator.py` (enhance)

Generate Python code for:
- Missing value imputation
- Duplicate removal
- Outlier handling
- Data type conversion
- Text cleaning (trim, lowercase)
- Column renaming

Returns:
```python
df.dropna(subset=['age'], inplace=True)
df.drop_duplicates(inplace=True)
df['salary'] = pd.to_numeric(df['salary'], errors='coerce')
```

---

### Phase 7: Automatic Cleaning & Download (Weeks 7-8)

#### 7.1 Cleaning Pipeline
**File:** `backend/services/cleaner.py`

Interface:
```python
def apply_cleaning_pipeline(
    df: pd.DataFrame,
    recommendations: List[Dict],
    config: Dict
) -> pd.DataFrame
```

#### 7.2 Download Endpoint
- `/api/datasets/{dataset_id}/download-cleaned`
- Returns CSV/Excel with cleaned data

---

### Phase 8: Report Generation (Weeks 8-9)

#### 8.1 HTML Report
Generate comprehensive HTML report:
- Dataset overview
- Data quality metrics
- Charts/visualizations
- Recommendations list
- Generated code snippet
- Timestamp

#### 8.2 PDF Export
- Use ReportLab or similar
- Include all HTML report content

Endpoint: `/api/datasets/{dataset_id}/report`

---

### Phase 9: Team Collaboration (Weeks 9-10)

#### 9.1 Team Invitation
- Add team member UI
- Email invitation system
- Role-based access (owner, editor, viewer)

#### 9.2 Collaboration Features
- Share project with team
- Activity log
- Comments on datasets (nice-to-have)

---

### Phase 10: Public API (Weeks 10-11)

#### 10.1 API Keys
- `/api/account/api-keys` - Create/manage keys
- Secure storage (hash keys in DB)

#### 10.2 Public Endpoints
```
POST /api/v1/analyze
  Body: { dataset_file, project_id }
  Returns: { dataset_id, health_score, recommendations }

GET /api/v1/analysis/{dataset_id}
  Returns: Analysis results

GET /api/v1/report/{dataset_id}
  Returns: HTML/PDF report
```

---

### Phase 11: Production & Deployment (Weeks 11-12)

#### 11.1 Environment Setup
- Create `.env.production`
- S3 configuration
- Database connection pooling
- Error logging (Sentry)

#### 11.2 Testing & QA
- Unit tests for backend services
- Integration tests
- E2E tests for critical flows

#### 11.3 Deployment
- Deploy to Vercel (frontend)
- Deploy to Railway/Render (FastAPI backend)
- Database migrations
- Monitoring setup

---

## Current Status

✅ **Already Implemented:**
- Basic FastAPI backend with upload endpoint
- Profiling services (profiler.py)
- Recommendation system (recommendations.py)
- Code generation (code_generator.py)
- Visualization functions (visualization.py)
- Cleaning pipeline (cleaner.py)
- Next.js frontend with UI components
- Tailwind CSS styling

❌ **Not Yet Implemented:**
- User authentication (NextAuth)
- Database schema (Supabase tables)
- Dashboard page
- Project management
- Persistent dataset storage
- Analysis history tracking
- API key system
- Team collaboration
- Report generation
- Production deployment config

---

## Technology Decisions

### Authentication
- **NextAuth.js** - Easy integration with Supabase
- JWT tokens for API access
- Email/password + optional OAuth

### Database
- **Supabase** - PostgreSQL + real-time features
- RLS (Row-Level Security) for data isolation

### Storage
- **Local FS** for development
- **S3** for production (via boto3)

### Reports
- **Generate HTML** for quick viewing
- **ReportLab** for PDF generation

### API
- FastAPI with OAuth2
- API keys stored as bcrypt hashes
- Rate limiting for public endpoints

---

## Success Criteria

1. ✅ Users can sign up and authenticate
2. ✅ Users can create multiple projects
3. ✅ Users can upload datasets with persistent storage
4. ✅ System generates detailed analysis with health scores
5. ✅ Users see actionable recommendations
6. ✅ Users can download cleaned datasets and reports
7. ✅ Users can manage team members
8. ✅ Public API for programmatic access
9. ✅ Production-ready deployment

---

## File Structure Changes

```
backend/
  ├── main.py (enhanced with auth, storage, API)
  ├── config.py (new: environment config)
  ├── database.py (new: Supabase connection)
  ├── auth.py (new: JWT, password hashing)
  ├── services/
  │   ├── profiler.py (enhanced)
  │   ├── recommendations.py (enhanced)
  │   ├── code_generator.py (enhanced)
  │   ├── visualization.py (enhanced)
  │   ├── cleaner.py (enhanced)
  │   ├── storage.py (new: S3 + local)
  │   ├── report_generator.py (new)
  │   └── team_service.py (new)
  ├── models.py (new: Pydantic models)
  └── requirements.txt (updated dependencies)

app/
  ├── page.tsx (landing page)
  ├── auth/
  │   ├── login/
  │   ├── signup/
  │   └── reset-password/
  ├── dashboard/
  │   ├── page.tsx
  │   ├── projects/
  │   └── settings/
  ├── projects/
  │   ├── [id]/
  │   │   ├── page.tsx
  │   │   └── datasets/
  │   │       └── [id]/
  │   │           ├── page.tsx
  │   │           └── analysis/
  │   └── new/
  ├── api/
  │   ├── auth/
  │   ├── datasets/
  │   └── projects/
  └── components/
      └── dashboard/

```

---

## Next Steps

1. Start with Phase 1: Database schema + Authentication
2. Test each phase before moving to next
3. Deploy incrementally (not all at once)
4. Gather user feedback early

