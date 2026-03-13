# End-to-End Workflow Testing Guide

## Quick Start (Manual Testing)

### 1. Test User Login
- Go to: `http://localhost:3001/auth/login`
- Email: `test@example.com`
- Password: `password123`
- ✅ Should successfully login and redirect to dashboard

### 2. Test Dashboard
- After login, verify at: `http://localhost:3001`
- Check metrics are visible:
  - Total Projects
  - Total Datasets
  - Average Health Score
  - New Datasets This Month
- Check visualizations render:
  - Line chart (Dataset upload trend)
  - Pie chart (Health score distribution)
  - Bar chart (Projects overview)

### 3. Test Project Creation
- Click "New Project" button (if available)
- Fill in project name: "Test Project"
- Click Create
- ✅ Should create and redirect

### 4. Test Dataset Upload
- Go to: `http://localhost:3001/upload`
- Select a CSV or Excel file from your computer
- Click "Upload"
- ✅ Should upload and appear in dashboard

### 5. Test Reports Page
- Go to: `http://localhost:3001/reports`
- Verify table shows your uploaded datasets
- Click "HTML" button
- ✅ Should download HTML report file
- Click "CSV" button
- ✅ Should download cleaned CSV file

---

## Automated Testing (API)

### Test Login
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"automation@test.com","password":"test123"}'

curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"automation@test.com","password":"test123"}'
```

### Get Token for Authenticated Requests
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' | jq -r '.access_token')

echo "Token: $TOKEN"
```

### Test Project Creation
```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Workflow Test Project","description":"Testing end-to-end"}'
```

### Test Dataset Analysis
```bash
# After creating a project and uploading a dataset
curl -X GET http://localhost:8000/api/datasets/{dataset_id}/analysis \
  -H "Authorization: Bearer $TOKEN"
```

### Test Report Downloads
```bash
# Download HTML Report
curl -X GET http://localhost:8000/api/datasets/{dataset_id}/report/html \
  -H "Authorization: Bearer $TOKEN" \
  -o report.html

# Download Cleaned CSV
curl -X GET http://localhost:8000/api/datasets/{dataset_id}/download-cleaned \
  -H "Authorization: Bearer $TOKEN" \
  -o cleaned_data.csv

# Download PDF Report (if supported)
curl -X GET http://localhost:8000/api/datasets/{dataset_id}/report/pdf \
  -H "Authorization: Bearer $TOKEN" \
  -o report.pdf
```

---

## Expected Features

### ✅ Working
- Email/Password signup and login
- Google OAuth login
- Dashboard with visualizations
- Project creation and management
- Dataset upload and storage
- Data quality profiling
- Reports page with working downloads
- HTML report generation
- CSV export (cleaned data)

### 🔄 In Progress
- PDF report generation
- Advanced filtering on reports
- Report scheduling
- Data comparison (before/after cleaning)

### ⏳ Coming Soon
- Team collaboration features
- API key management
- Data quality trend tracking
- Batch dataset processing

---

## Troubleshooting

### Issue: "Failed to fetch" on login
- Check backend is running: `pgrep -f uvicorn.*8000`
- Check frontend has correct API URL: `echo $NEXT_PUBLIC_API_URL`
- Check CORS is enabled in backend

### Issue: Reports page shows no datasets
- Go to upload page and upload a file first
- Check backend logs for errors: `ps aux | grep uvicorn`

### Issue: Report download fails
- Check file exists in storage (`cd backend && ls -la uploads/`)
- Verify dataset ID is correct

### Issue: Server not starting
```bash
# Kill existing processes
pkill -9 -f uvicorn
pkill -9 -f "next dev"

# Start fresh
cd backend && python -m uvicorn main:app --reload &
cd ../ && npm run dev &
```

---

## Success Criteria

✅ All workflows complete without errors
✅ All downloads work (HTML, CSV)
✅ Dashboard displays real data from uploaded files
✅ Reports page shows all uploaded datasets
✅ Authentication works (email/password + Google)
✅ Error messages are clear and helpful
