# CleanGenius AI API Documentation

The Python backend runs on `http://127.0.0.1:5000`.

## Endpoints

### System Info
- **GET `/api/system/info`**
  - Returns OS info, total disk space, used disk space, free space, and drive list.

### Scanning
- **POST `/api/scan/start`**
  - Request body: `{ "mode": "fast|deep|custom|registry", "paths": [], "options": {} }`
  - Returns: `{ "success": true, "scan_id": 1 }`
- **GET `/api/scan/<scan_id>`**
  - Returns status, progress percentage, and scan result summary.

### Cleanup
- **POST `/api/cleanup/start`**
  - Request body: `{ "scan_id": 1, "categories": [], "options": { "recycle_bin": true } }`
  - Returns: `{ "success": true, "cleanup_id": 1 }`
- **POST `/api/cleanup/rollback/<cleanup_id>`**
  - Restores files deleted during the specified cleanup session.

### AI Operations
- **POST `/api/ai/analyze`**
  - Sends scan results to configured AI provider and logs API cost.
- **GET `/api/ai/test/<provider>`**
  - Tests API connectivity to specified provider.
- **GET `/api/ai/cost`**
  - Returns monthly usage token and USD cost stats.

### Dashboard & Reports
- **GET `/api/dashboard`**
  - Returns health score, system info, latest scan, and activity log.
- **POST `/api/reports/export`**
  - Request body: `{ "type": "pdf|csv|json", "filePath": "/path/to/report.pdf", "data": {} }`
