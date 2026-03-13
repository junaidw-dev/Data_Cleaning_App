# AI Data Cleaner - Development & Deployment Guide

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup

1. **Create Virtual Environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install fastapi uvicorn pandas numpy scipy openpyxl python-multipart
   ```

3. **Run Backend Server**
   ```bash
   cd backend
   uvicorn main:app --reload --host 127.0.0.1 --port 9000
   ```

   Server will be available at: `http://127.0.0.1:9000`

### Frontend Setup

1. **Install Dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

2. **Run Development Server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

   Application will be available at: `http://localhost:3000`

3. **Build for Production**
   ```bash
   npm run build
   npm start
   ```

---

## Project Structure

```
Data_Cleaning_App/
├── backend/
│   ├── main.py                    # FastAPI application & endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── profiler.py            # Data profiling engine
│   │   ├── recommendations.py     # Recommendation generation
│   │   ├── code_generator.py      # Python code generation
│   │   ├── cleaner.py             # Data cleaning operations
│   │   ├── visualization.py       # Visualization data generation
│   │   └── error_handler.py       # Error handling utilities
│   └── requirements.txt           # Python dependencies
│
├── app/                           # Next.js/React frontend
│   ├── page.tsx                   # Home page
│   ├── upload/page.tsx            # Upload page
│   ├── preview/page.tsx           # Preview page
│   ├── analysis/page.tsx          # Analysis dashboard
│   └── layout.tsx                 # Layout wrapper
│
├── components/
│   ├── layouts/DashboardLayout.tsx
│   └── ui/                        # Shadcn UI components
│
├── package.json                   # Frontend dependencies
├── tsconfig.json                  # TypeScript configuration
├── tailwind.config.ts             # Tailwind CSS configuration
└── FEATURES.md                    # Feature documentation
```

---

## API Endpoints Reference

### File Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload and preview dataset |
| POST | `/analyze` | Comprehensive data analysis |
| POST | `/clean` | Apply automated cleaning |
| POST | `/natural-language-summary` | Generate text summary |
| POST | `/export/html-report` | Export HTML report |
| POST | `/download/cleaned-dataset` | Download cleaned CSV |

### Visualization Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/visualizations/missing-values` | Missing values chart data |
| POST | `/visualizations/numeric-distribution/{column}` | Numeric distribution |
| POST | `/visualizations/categorical-distribution/{column}` | Category distribution |
| POST | `/visualizations/correlation` | Correlation matrix |
| POST | `/visualizations/box-plots` | Box plot data |

---

## Configuration

### Backend Configuration

Edit `backend/main.py` to customize:

```python
# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File size limit (in main.py endpoints)
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
```

### Frontend Configuration

Edit `app/analysis/page.tsx` to customize API endpoint:

```typescript
const API_BASE_URL = 'http://127.0.0.1:9000';

// Change for different backend URL
fetch(`${API_BASE_URL}/analyze`, { ... })
```

---

## Data Cleaning Pipeline

### Default Cleaning Configuration

```python
cleaning_config = {
    "remove_empty_rows": True,
    "remove_empty_columns": True,
    "remove_duplicates": True,
    "handle_missing_values": True,
    "missing_value_strategy": "median",
    "handle_outliers": False,
    "convert_types": False
}
```

### Cleaning Strategies

**Missing Value Strategies:**
- `median` - Fill numeric with median, categorical with mode
- `mean` - Fill numeric with mean
- `forward_fill` - Forward fill method
- `zero` - Fill numeric with 0

**Outlier Methods:**
- `iqr` - Interquartile range method (default)
- `zscore` - Z-score method

**Outlier Actions:**
- `cap` - Cap values at bounds (default)
- `remove` - Remove outlier rows
- `iqr_remove` - Remove using IQR bounds

---

## Error Handling

### Error Classes

```python
# Base error
DataCleanerError(message, error_code, status_code)

# Specific error types
ValidationError(message)
FileFormatError(filename)
FileSizeError(filename, size_mb)
FileReadError(filename, original_error)
EmptyDatasetError()
ProcessingError(message, operation)
ProfilingError(message)
CleaningError(message)
```

### API Error Response Format

```json
{
  "error_code": "FILE_FORMAT_ERROR",
  "message": "Unsupported file format: file.txt. Supported formats: .csv, .xlsx, .xls",
  "status_code": 400
}
```

---

## Performance Optimization

### Frontend Optimization

1. **Code Splitting**
   - Pages are automatically code-split in Next.js
   - Components use React.lazy() for dynamic imports

2. **Image Optimization**
   - Use next/image for optimized images
   - Enable AVIF format for newer browsers

3. **Bundle Analysis**
   ```bash
   npm run build --analyze
   ```

### Backend Optimization

1. **Pandas Performance**
   ```python
   # Use chunked reading for large files
   chunks = pd.read_csv(file, chunksize=10000)
   
   # Use dtypes parameter for memory efficiency
   dtypes = {'column_name': 'category'}
   df = pd.read_csv(file, dtype=dtypes)
   ```

2. **Async Processing**
   - All endpoints use async/await
   - File uploads don't block request handling

3. **Caching**
   - Consider Redis for analysis caching
   - Profile results can be cached by file hash

---

## Testing

### Backend Testing

```bash
# Test API endpoints
curl -X POST -F "file=@test.csv" http://127.0.0.1:9000/analyze

# Test with Python
import requests
with open('test.csv', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://127.0.0.1:9000/analyze', files=files)
    print(response.json())
```

### Frontend Testing

```bash
# Run linter
npm run lint

# Type check
npm run typecheck
```

---

## Production Deployment

### Backend Deployment (Using Gunicorn)

1. **Install Production Server**
   ```bash
   pip install gunicorn
   ```

2. **Create systemd Service**
   ```ini
   [Unit]
   Description=AI Data Cleaner Backend
   After=network.target

   [Service]
   Type=notify
   User=www-data
   WorkingDirectory=/path/to/backend
   Environment="PATH=/path/to/venv/bin"
   ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:9000 main:app

   [Install]
   WantedBy=multi-user.target
   ```

3. **Start Service**
   ```bash
   sudo systemctl start ai-data-cleaner
   sudo systemctl enable ai-data-cleaner
   ```

### Frontend Deployment (Using Netlify/Vercel)

1. **Connect Repository**
   - Push code to GitHub
   - Connect with Netlify/Vercel

2. **Configure Build**
   ```
   Build Command: npm run build
   Publish Directory: .next
   ```

3. **Environment Variables**
   ```
   NEXT_PUBLIC_API_URL=https://api.yourdomain.com
   ```

### Docker Deployment

**Dockerfile for Backend:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .

EXPOSE 9000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "9000:9000"
    environment:
      - MAX_FILE_SIZE=104857600

  frontend:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:9000
```

---

## Troubleshooting

### Backend Issues

**CORS Errors**
- Ensure backend is running on correct port
- Check CORS middleware configuration
- Verify frontend API URL

**Module Import Errors**
- Ensure all dependencies are installed
- Check Python path includes backend directory
- Verify service files are in `backend/services/`

**File Upload Fails**
- Check file format (CSV/XLSX only)
- Verify file is not empty
- Check file size doesn't exceed limit

### Frontend Issues

**Build Errors**
- Clear `.next` directory: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`
- Clear npm cache: `npm cache clean --force`

**API Connection Issues**
- Verify backend is running
- Check browser console for CORS errors
- Verify API endpoint in `app/analysis/page.tsx`

### Dataset Issues

**"Dataset is Empty" Error**
- Ensure CSV has data rows (not just headers)
- Check file encoding (UTF-8 recommended)
- Verify headers are not duplicated

**Memory Issues with Large Files**
- Upgrade server memory
- Implement chunked processing
- Use Dask for out-of-memory operations

---

## Security Considerations

1. **File Validation**
   - Only accept CSV/XLSX files
   - Validate file size limits
   - Scan for malicious content

2. **CORS Configuration**
   - In production, set specific origins
   - Disable wildcard (`*`) for security

3. **Input Validation**
   - All file inputs are validated
   - Column names are sanitized
   - File paths are never exposed

4. **Error Messages**
   - Avoid exposing system paths
   - Don't log sensitive data
   - Provide user-friendly messages

---

## Future Enhancements

- [ ] User authentication & authorization
- [ ] Dataset history & versioning
- [ ] Advanced ML-based data profiling
- [ ] Scheduled batch processing
- [ ] Custom cleaning rules
- [ ] Data governance features
- [ ] Advanced visualization charts
- [ ] API rate limiting
- [ ] Database integration
- [ ] Mobile app

---

## Contributing

When contributing code:

1. Follow PEP 8 (Python)
2. Use TypeScript for new components
3. Include error handling
4. Write docstrings
5. Test thoroughly

---

## Support & Documentation

- **Issues**: Report bugs on GitHub Issues
- **Features**: Suggest features via GitHub Discussions  
- **Docs**: See [FEATURES.md](./FEATURES.md) for detailed feature docs

---

## License

This project is part of the AI Data Cleaner application.

---

**Last Updated:** March 2026
**Version:** 2.0 (Advanced Features)
