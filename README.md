# ADaVS
Asset discovery and an open source vulnerability scanner to display enterprise vulnerabilities

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