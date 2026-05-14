# Sanjeevani — Disease Prediction & Early Warning System

Sanjeevani is a full-stack web application that predicts disease outbreak risk from environmental conditions, shows live weather and AQI data, stores user prediction history, and visualizes risk zones on a map.

## Features

- Disease risk prediction with a lightweight ensemble model
- Real-time weather and AQI integration from OpenWeather
- JWT authentication with MongoDB user storage
- Prediction history saved per user
- Dashboard with charts and live alerts
- Leaflet map with risk zones
- Dockerized frontend, backend, and MongoDB
- Basic GitHub Actions CI workflow

## Project Structure

```text
frontend/
  src/
    components/
    context/
    pages/
    services/
backend/
  app/
    routes/
    main.py
    model.py
    auth.py
    database.py
docker-compose.yml
```

## Prerequisites

- Docker and Docker Compose
- Python 3.9 for local backend development
- Node.js 18 for local frontend development
- An OpenWeather API key for live data

## Environment Variables

Copy the example file and update the values:

```bash
cp .env.example .env
```

Important variables:

- `MONGODB_URI`
- `MONGODB_DB`
- `JWT_SECRET`
- `OPENWEATHER_API_KEY`

## Run With Docker

1. Create `.env` from `.env.example` and set your OpenWeather key.
2. Build and start the stack:

```bash
docker compose up --build
```

3. Open the apps:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- MongoDB: localhost:27017

## Run Backend Locally

1. Create a virtual environment inside `backend/`.
2. Install dependencies:

```bash
cd backend
pip install -r backend/requirements.txt
```

3. Start FastAPI:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run Frontend Locally

1. Install packages:

```bash
cd frontend
npm install
```

2. Start Vite:

```bash
npm run dev
```

3. Open http://localhost:3000

## API Endpoints

- `POST /signup` - create a user and return a JWT
- `POST /login` - log in and return a JWT
- `GET /predict?temperature=&humidity=&aqi=` - predict outbreak risk and store history
- `GET /aqi?lat=&lon=` - fetch AQI data
- `GET /weather?lat=&lon=` - fetch weather data
- `GET /history` - fetch saved predictions for the authenticated user

## Notes

- If no OpenWeather API key is configured, the backend uses deterministic mock weather and AQI values so the app still runs.
- The risk model uses a lightweight ensemble tuned for this workspace environment, so it runs without binary ML dependencies.
- Frontend auth tokens are stored in `localStorage` for simplicity.
