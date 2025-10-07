# ADaVS

Asset discovery and an open source vulnerability scanner to display enterprise vulnerabilities

## Disclaimer

**Authorized Use Only**: ADaVS is designed for asset discovery and vulnerability scanning within environments you own or are explicitly authorized to test.

**Educational & Research**: This project is open-source for learning, research, and authorized security testing only.

**Responsible Disclosure**: Follow responsible disclosure practices i.e. do not exploit or share vulnerabilities without the owner’s consent.

## Project Structure

Frontend: React and Vite
Backend: Python and FastAPI

## Running with Docker

### 1. Prerequisites

- Install [Docker](https://docs.docker.com/get-docker/)

### 2. Start the application

From the project root (where `docker-compose.yml` is located):

    docker compose up --build

This will:

- Build production-ready Docker images for both frontend and backend

### 3. Access the app

- **Frontend (React + Vite served by Nginx)** → http://localhost:3000
- **Backend (FastAPI)** → http://localhost:8000
- **API Docs (Swagger UI)** → http://localhost:8000/docs

### 4. Stopping the app

To stop and remove containers:

    docker compose down

If you want to run in the background (detached mode):

    docker compose up -d

And then view logs with:

    docker compose logs -f

### 5. Development Notes

- No need for `npm install` or Python `venv` locally
- All services run in isolated containers, ensuring consistent environments across machines.
