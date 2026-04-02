# Quickoo Backend (FastAPI + MongoDB + SMTP)

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Ensure `.env` exists (already added).
4. Run server:

```bash
uvicorn app.main:app --reload
```

## API

- Health: `GET /health`
- Create Admin: `POST /api/v1/admins/create`

### Create Admin Payload

```json
{
  "email": "admin@example.com",
  "password": "strongpassword123",
  "is_active": true
}
```
