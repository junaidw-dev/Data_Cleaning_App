# Data Cleaning App 🧹

A powerful, full-stack data cleaning and analysis platform with real-time profiling, automated code generation, and comprehensive reporting.

![Status](https://img.shields.io/badge/status-active-success)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features ✨

### 📊 Core Functionality
- **Dataset Upload** - Support for CSV files with instant preview
- **Data Profiling** - Advanced profiling with statistical insights and data quality scores
- **Auto-Cleaning** - AI-driven recommendations and automated cleaning pipeline
- **Code Generation** - Generates Python code for your cleaning transformations
- **Professional Reports** - HTML, CSV, and PDF export with visualizations

### 🔐 Authentication & Security
- **Email/Password Login** - Secure authentication with JWT tokens
- **Google OAuth 2.0** - One-click sign-in with Google
- **Protected Routes** - Role-based access control
- **Secure Sessions** - HTTP-only cookies and token management

### 📈 Analytics & Visualization
- **Interactive Dashboard** - Real-time charts and metrics using Recharts
- **Data Health Score** - Automated data quality assessment
- **Missing Value Analysis** - Detect and handle missing data
- **Outlier Detection** - Identify anomalies in datasets

### 🚀 Advanced Features
- **Project Management** - Create, organize, and manage multiple data projects
- **Cleaning History** - Track all transformations applied to datasets
- **Download Options** - Export cleaned data in multiple formats
- **Responsive UI** - Works on desktop, tablet, and mobile

## Tech Stack 🛠️

### Frontend
- **Next.js 13.5** - React framework with App Router
- **React 18.2** - UI library
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS 3.3** - Utility-first CSS
- **Recharts 2.12.7** - React charting library
- **Shadcn/ui** - Beautiful, accessible components

### Backend
- **FastAPI** - Modern Python web framework with async support
- **Uvicorn** - ASGI server
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing
- **Scikit-learn** - Machine learning utilities
- **ReportLab** - PDF generation
- **Google Auth** - OAuth 2.0 integration

### Database & Storage
- **Supabase** (production-ready setup)
- **Mock Database** (development)
- **Local File Storage** (development)
- **S3** (ready for integration)

## Installation & Setup 🚀

### Prerequisites
- Node.js 16+ 
- Python 3.9+
- npm or yarn

### Clone the Repository
```bash
git clone https://github.com/junaidw-dev/Data_Cleaning_App.git
cd Data_Cleaning_App
```

### Backend Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Start the backend server
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

### Frontend Setup
```bash
# Install Node dependencies
npm install

# Start the development server
npm run dev
```

Frontend will be available at: http://localhost:3000

## Usage 📖

### 1. Sign Up
- Visit http://localhost:3000
- Sign up with email/password or Google OAuth
- Confirm your account

### 2. Create a Project
- Click "New Project" on the dashboard
- Enter project name and description
- View your project on the dashboard

### 3. Upload Dataset
- Navigate to "Upload" section
- Select a CSV file
- Preview the data
- Click "Analyze" to start profiling

### 4. Review Analysis
- View data profiling results
- Check data quality score
- Review recommendations
- See identified issues

### 5. Clean Data
- Click "Auto Clean" for automated transformations
- Review generated Python code
- Apply cleaning manually
- Download cleaned dataset

### 6. Generate Reports
- Choose export format (HTML, CSV, PDF)
- Customize report options
- Download for sharing or archiving

## API Documentation 📚

### Authentication Endpoints
```
POST /api/auth/signup          - Register new user
POST /api/auth/login           - Login with credentials
POST /api/auth/google          - Google OAuth callback
GET  /api/auth/me              - Get current user info
POST /api/auth/logout          - Logout user
```

### Projects Endpoints
```
GET    /api/projects           - List all projects
POST   /api/projects           - Create new project
GET    /api/projects/{id}      - Get project details
PUT    /api/projects/{id}      - Update project
DELETE /api/projects/{id}      - Delete project
```

### Data Analysis Endpoints
```
POST   /api/analyze            - Upload and analyze file
GET    /api/analysis/{id}      - Get analysis results
POST   /api/clean              - Apply cleaning
GET    /api/recommendations    - Get cleaning recommendations
```

### Export Endpoints
```
POST /api/export/html-report   - Generate HTML report
POST /api/export/csv           - Export cleaned data as CSV
POST /api/export/pdf           - Generate PDF report
```

### Utilities
```
GET  /docs                     - Interactive API documentation (Swagger)
GET  /redoc                    - Alternative API documentation
```

## Project Structure 📁

```
Data_Cleaning_App/
├── app/                           # Next.js application
│   ├── auth/                      # Authentication pages
│   │   ├── login/page.tsx
│   │   └── signup/page.tsx
│   ├── dashboard/                 # Dashboard page
│   ├── upload/                    # File upload page
│   ├── analysis/                  # Analysis results
│   ├── preview/                   # Data preview
│   ├── projects/                  # Project management
│   ├── reports/                   # Reports page
│   ├── context/                   # React context (Auth)
│   ├── components/                # Reusable components
│   ├── layout.tsx                 # Root layout
│   └── page.tsx                   # Home page
│
├── backend/                       # FastAPI application
│   ├── main.py                    # Main application file
│   ├── auth.py                    # Authentication logic
│   ├── database.py                # Database service
│   ├── mock_database.py           # Mock DB for development
│   ├── config.py                  # Configuration
│   ├── google_auth.py             # Google OAuth service
│   ├── models.py                  # Database models
│   ├── requirements.txt           # Python dependencies
│   └── services/                  # Business logic
│       ├── cleaner.py             # Data cleaning service
│       ├── profiler.py            # Data profiling
│       ├── visualization.py       # Chart generation
│       ├── storage.py             # File storage
│       ├── error_handler.py       # Error handling
│       └── recommendations.py     # Auto recommendations
│
├── components/                    # Shared UI components
│   ├── layouts/
│   │   └── DashboardLayout.tsx
│   └── ui/                        # Shadcn/ui components
│
├── hooks/                         # Custom React hooks
├── lib/                           # Utility functions
├── public/                        # Static assets
├── tests/                         # Test files
├── package.json                   # Node dependencies
├── tsconfig.json                  # TypeScript config
├── next.config.js                 # Next.js config
├── tailwind.config.ts             # Tailwind config
└── README.md                      # This file
```

## Key Features in Detail 🔍

### Smart Data Profiling
The app analyzes your data and provides:
- Missing value detection and percentage
- Data type classification
- Outlier identification
- Statistical summaries
- Data quality scoring

### Automated Recommendations
Get intelligent suggestions for:
- Handling missing values (drop, fill, interpolate)
- Type conversions
- Outlier treatment
- Duplicate removal
- Data normalization

### Code Generation
Every transformation is backed by generated Python code:
- Review exactly what will happen to your data
- Copy code for your own scripts
- Learn pandas best practices

### Professional Reporting
Export comprehensive reports with:
- Data profiling summaries
- Visual charts and graphs
- Cleaning history
- Data quality metrics
- Downloadable cleaned datasets

## Authentication Details 🔒

### Email/Password
- Passwords hashed with bcrypt
- JWT tokens for session management
- HTTP-only secure cookies
- Token refresh mechanism

### Google OAuth 2.0
- Seamless integration with Google accounts
- Automatic user creation on first login
- Secure token exchange
- Profile data synchronization

## Environment Variables 🔧

Create a `.env.local` file in the root directory:

```env
# Google OAuth (Optional)
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id

# Backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Supabase Configuration (Optional - for production)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## Testing 🧪

### Run E2E Tests
```bash
# Ensure both servers are running
source venv/bin/activate
python test_e2e_workflow.py
```

### Test API Endpoints
```bash
# Signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

## Performance Optimizations ⚡

- Async/await for non-blocking operations
- Client-side data caching
- Lazy component loading
- Optimized image compression
- Database query optimization
- ReportLab streaming for large PDFs

## Production Deployment 🚀

### Frontend (Vercel)
```bash
npm run build
# Deploy to Vercel
vercel deploy
```

### Backend (Railway, Render, or Heroku)
```bash
pip freeze > requirements.txt
# Deploy with your platform's CLI
```

### Database (Supabase)
- Update database.py to use Supabase credentials
- Run migrations from SUPABASE_SCHEMA.sql
- Configure authentication providers

## Troubleshooting 🔧

### Port Already in Use
```bash
# Kill process on port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Kill process on port 3000
lsof -i :3000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Dependencies Issues
```bash
# Clear npm cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Reinstall Python dependencies
pip install -r backend/requirements.txt --force-reinstall
```

### Backend Not Responding
```bash
# Check if backend is running
curl http://localhost:8000/docs

# Check logs
tail -f /tmp/backend.log
```

## Contributing 🤝

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Roadmap 🗺️

- [ ] Team collaboration and sharing
- [ ] API key management
- [ ] Advanced scheduling
- [ ] Data lineage tracking
- [ ] Machine learning predictions
- [ ] Custom transformation templates
- [ ] Webhook integrations
- [ ] Real-time collaboration
- [ ] Mobile app

## Support 💬

Need help? Check out:
- [API Documentation](http://localhost:8000/docs)
- [Quick Start Guide](./QUICK_START.md)
- [Implementation Guide](./IMPLEMENTATION_SUMMARY.md)
- [Test Workflow Guide](./TEST_WORKFLOW.md)

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Author ✍️

**Muhammad Junaid Waheed**
- GitHub: [@junaidw-dev](https://github.com/junaidw-dev)

---

**Made with ❤️ for data excellence**
