# MeetAI Backend API

FastAPI backend for the MeetAI Fivetran Challenge project. This backend processes meeting data, performs analytics, and provides APIs for the frontend application.

## Features

- **Meeting Management**: Create, read, update, and delete meetings
- **Participant Tracking**: Manage meeting participants and their data
- **Sentiment Analysis**: Store and analyze sentiment data from meetings
- **Analytics Dashboard**: Comprehensive analytics and insights
- **Workforce Metrics**: Track department-wise performance metrics
- **Data Connectors**: Manage Fivetran and custom data connectors

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL database
- pip package manager

### Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
   - Copy `.env.example` to `.env` (if exists) or use the existing `.env` file
   - Update database credentials as needed

4. Start the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc

## API Endpoints

### Data Endpoints (`/api/data`)
- `GET /meetings` - List all meetings
- `POST /meetings` - Create a new meeting
- `GET /meetings/{id}` - Get specific meeting
- `PUT /meetings/{id}` - Update meeting
- `DELETE /meetings/{id}` - Delete meeting
- `GET /participants` - List participants
- `POST /participants` - Add participant
- `GET /connectors` - List data connectors
- `POST /connectors` - Create data connector
- `GET /sentiment` - Get sentiment data
- `POST /sentiment` - Add sentiment data

### Analytics Endpoints (`/api/analytics`)
- `GET /dashboard` - Get dashboard data
- `GET /meetings/{id}/analytics` - Get meeting analytics
- `POST /meetings/{id}/analytics` - Create meeting analytics
- `GET /sentiment/trends` - Get sentiment trends
- `GET /workforce/metrics` - Get workforce metrics
- `POST /workforce/metrics` - Add workforce metric
- `GET /summary` - Get analytics summary

## Database Models

- **Meeting**: Core meeting information
- **Participant**: Meeting participants
- **MeetingAnalytics**: Analytics data for meetings
- **SentimentData**: Sentiment analysis results
- **DataConnector**: Fivetran connector configurations
- **WorkforceMetrics**: Department performance metrics

## Environment Variables

```
DATABASE_URL=postgresql://username:password@host:port/database
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Development

The backend is configured with CORS to allow requests from the frontend development servers (ports 3000 and 5173).

For production deployment, update the CORS origins in `main.py` to match your production frontend URL.

## Database Connection

The backend connects to the provided PostgreSQL database:
- Host: 35.226.158.237
- Database: postgres
- Username: fivetran
- Password: (URL-encoded in DATABASE_URL)

The database tables are automatically created when the application starts.