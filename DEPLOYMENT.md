# 🚀 Quick Deployment Guide

## Prerequisites
- Python 3.8+
- pip3
- Docker (optional, for containerized deployment)

## Option 1: Quick Start (Local)

1. **Clone or download the project files**
2. **Run the startup script:**
   ```bash
   ./start.sh
   ```

## Option 2: Manual Local Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the API:**
   ```bash
   python main.py
   ```

## Option 3: Docker Deployment

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Or build manually:**
   ```bash
   docker build -t batik-api .
   docker run -p 8000:8000 batik-api
   ```

## Verify Deployment

1. **Check health:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Run tests:**
   ```bash
   python test_api.py
   ```

3. **View API docs:**
   - Open http://localhost:8000/docs in your browser

## API Endpoints

- **Health Check**: `GET /health`
- **Model Info**: `GET /model-info`
- **Single Prediction**: `POST /predict`
- **Batch Prediction**: `POST /predict-batch`

## Troubleshooting

- **Port 8000 in use**: Change port in `main.py` or `docker-compose.yml`
- **Model not loading**: Check if `final_tuned_genetic_algorithm_model.keras` exists
- **Memory issues**: Increase Docker memory limits or use GPU

## Production Deployment

For production, consider:
- Using a reverse proxy (nginx)
- Setting up SSL/TLS
- Implementing authentication
- Using a process manager (systemd, supervisor)
- Setting up monitoring and logging 