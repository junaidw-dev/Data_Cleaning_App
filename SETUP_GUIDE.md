# SaaS Development Setup Guide

## Phase 1 Complete: Backend Infrastructure & Authentication

### What's Been Implemented

✅ **Backend Services:**
- Configuration management with environment variables
- JWT-based authentication with bcrypt password hashing
- Supabase database integration
- Full CRUD operations for users, projects, datasets, and analyses
- Secure storage abstraction layer (local file or S3)
- API key management for public API access

✅ **New Dependencies:**
- FastAPI with async support
- PyJWT for JWT tokens
- Bcrypt for password hashing
- Supabase Python SDK
- Boto3 for S3 integration

✅ **Database Schema:**
- Users table with email uniqueness
- Projects for organizing datasets
- Datasets with metadata and health scores
- Analysis results with comprehensive profiling
- Team members for collaboration
- API keys for programmatic access

### Setup Instructions

#### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

If `requirements.txt` doesn't install properly, use:

```bash
pip install fastapi uvicorn python-multipart python-dotenv pydantic pydantic-settings \
            pandas numpy openpyxl python-jose bcrypt cryptography PyJWT email-validator \
            supabase boto3 requests aiofiles jinja2 reportlab matplotlib seaborn \
            scikit-learn scipy sqlalchemy
```

#### 2. Setup Supabase Project

1. **Create a Supabase Project:**
   - Visit [supabase.com](https://supabase.com)
   - Create a new project (choose your region)
   - Note your project URL and API key

2. **Create Database Schema:**
   - Go to Supabase Dashboard → SQL Editor
   - Create a new query
   - Copy the contents of `backend/SUPABASE_SCHEMA.sql`
   - Paste and run the SQL

3. **Configure Authentication:**
   - Go to Authentication → Providers
   - Enable "Email" provider
   - Configure SMTP settings or use Supabase's built-in email

#### 3. Environment Configuration

Create `.env.development` in the `backend/` directory:

```bash
# Database
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your-anon-key-here"

# Security
JWT_SECRET="your-secret-key-change-in-production"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_HOURS=24

# Storage (Development: local files)
UPLOAD_DIR="./data/uploads"
MAX_FILE_SIZE_MB=100
ENVIRONMENT="development"

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000","http://127.0.0.1:3000"]

# S3 (For production only)
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
AWS_S3_BUCKET=""
AWS_S3_REGION="us-east-1"
```

#### 4. Run the Backend

```bash
# Development with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use Python directly
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

**API Documentation:** `http://localhost:8000/docs`

---

## Seed an Admin User (Development)

Create or update an admin user using environment variables:

```bash
cd backend
export ADMIN_EMAIL="admin@example.com"
export ADMIN_PASSWORD="ChangeMe123!"
export ADMIN_NAME="Admin User"
python seed_admin.py
```

This creates the user if it doesn't exist, or resets the password if it does.

---

## API Endpoints Overview

### Authentication Endpoints

```
POST   /api/auth/signup             - Register new user
POST   /api/auth/login              - Login user
POST   /api/auth/password-reset     - Request password reset
```

### User Endpoints

```
GET    /api/user/me                 - Get current user profile
```

### Project Endpoints

```
POST   /api/projects                - Create project
GET    /api/projects                - List user's projects
GET    /api/projects/{project_id}   - Get project details
DELETE /api/projects/{project_id}   - Delete project
```

### Dataset Endpoints

```
POST   /api/projects/{project_id}/datasets           - Upload dataset
GET    /api/projects/{project_id}/datasets           - List datasets
GET    /api/datasets/{dataset_id}                    - Get dataset details
POST   /api/datasets/{dataset_id}/analyze            - Analyze dataset
GET    /api/datasets/{dataset_id}/analysis           - Get latest analysis
POST   /api/datasets/{dataset_id}/clean              - Clean dataset
GET    /api/datasets/{dataset_id}/download-cleaned   - Download cleaned data
```

### API Key Endpoints

```
POST   /api/account/api-keys        - Create API key
GET    /api/account/api-keys        - List API keys
DELETE /api/account/api-keys/{id}   - Delete API key
```

### Legacy Endpoints (No Auth Required)

```
POST   /upload   - Upload and preview dataset
POST   /analyze  - Analyze dataset
```

---

## Example API Usage

### 1. Sign Up

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password_123",
    "full_name": "John Doe"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "subscription_tier": "free",
    "created_at": "2026-03-13T..."
  }
}
```

### 2. Create Project

```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales Data Analysis",
    "description": "Q1 2026 sales data"
  }'
```

### 3. Upload Dataset

```bash
curl -X POST http://localhost:8000/api/projects/{project_id}/datasets \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@sales_data.csv"
```

### 4. Analyze Dataset

```bash
curl -X POST http://localhost:8000/api/datasets/{dataset_id}/analyze \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Database Structure

### Users
- `id` (UUID): Primary key
- `email` (Text): Unique email address
- `password_hash` (Text): Bcrypt hashed password
- `full_name` (Text): User's name
- `subscription_tier` (Enum): free/pro/enterprise
- `created_at`, `updated_at` (Timestamps)

### Projects
- `id` (UUID): Primary key
- `user_id` (UUID): Owner (FK to users)
- `name` (Text): Project name
- `description` (Text): Optional description
- `created_at`, `updated_at` (Timestamps)

### Datasets
- `id` (UUID): Primary key
- `project_id` (UUID): Owning project (FK)
- `filename` (Text): Original filename
- `file_path` (Text): Storage path
- `size_bytes` (Integer): File size
- `metadata` (JSON): Rows, columns, column names
- `health_score` (Float): Data quality score
- `created_at`, `updated_at` (Timestamps)

### Analysis Results
- `id` (UUID): Primary key
- `dataset_id` (UUID): Analyzed dataset (FK)
- `health_score` (Float): Score 0-100
- `profiling_data` (JSON): Complete profile
- `recommendations` (JSON): Array of recommendations
- `created_at` (Timestamp)

---

## Frontend Setup (Next Steps)

The frontend will be updated in Phase 2 with:
- NextAuth.js integration with Supabase
- Login/signup pages
- Dashboard component
- Project management UI
- Dataset upload and analysis interface

---

## Production Deployment Checklist

### Backend
- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Configure S3 bucket with AWS credentials
- [ ] Set strong `JWT_SECRET`
- [ ] Enable HTTPS only
- [ ] Setup database backups
- [ ] Configure error logging (Sentry)
- [ ] Setup monitoring (e.g., DataDog)
- [ ] Run load testing

### Infrastructure
- [ ] Deploy to Railway, Render, or similar
- [ ] Setup CI/CD pipeline (GitHub Actions)
- [ ] Configure custom domain
- [ ] Setup SSL certificates
- [ ] Enable rate limiting on API
- [ ] Setup API documentation

### Security
- [ ] Enable Row-Level Security (RLS) on Supabase
- [ ] Validate all input fields
- [ ] Setup CORS correctly (don't use "*")
- [ ] Implement rate limiting
- [ ] Add request signing for API keys
- [ ] Regular security audits

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'config'"

**Solution:**
```bash
# Make sure you're in the backend directory
cd backend
# Try running with Python module syntax
python -m uvicorn main:app --reload
```

### Issue: "Supabase connection failed"

**Solution:**
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Check that your Supabase project is active
- Ensure firewall doesn't block Supabase API

### Issue: "JWT token validation failed"

**Solution:**
- Check that `JWT_SECRET` matches in `.env`
- Verify token wasn't modified
- Check token expiration time

---

## Next Steps

1. **Phase 2:** Frontend authentication with NextAuth.js
2. **Phase 3:** Dashboard and project management UI
3. **Phase 4:** Advanced features (teams, reports, etc.)
4. **Phase 5:** Production deployment

For questions or issues, refer to the implementation plan in `SAAS_IMPLEMENTATION_PLAN.md`.
