# ADaVS

Asset discovery and an open source vulnerability scanner to display enterprise vulnerabilities

## Disclaimer

**Authorized Use Only**: ADaVS is designed for asset discovery and vulnerability scanning within environments you own or are explicitly authorized to test.
**Educational & Research**: This project is open-source for learning, research, and authorized security testing only.
**Responsible Disclosure**: Follow responsible disclosure practices i.e. do not exploit or share vulnerabilities without the owner’s consent.

## Project Structure

Frontend: React and Vite
Backend: Python and FastAPI

## Frontend Setup (Make sure Node is installed)

cd frontend
npm install
npm run dev

App URL: http://localhost:5173

## Backend Setup

cd backend (Make sure everything is done within the backend folder)
python -m venv venv

- Activate the virtual environment:
  Windows: venv\Scripts\activate

Mac/Linux: source venv/bin/activate

- Install dependencies
  pip install -r requirements.txt

- Run the server
  uvicorn app.main:app --reload

API URL: http://localhost:8000
Docs: http://localhost:8000/docs
