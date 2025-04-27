# lifestats.me
life analytics for everyone

## Backend Setup

Follow these steps to run the FastAPI backend locally.

1. Install Python 3.8+ and (optionally) create a virtual environment:
   ```bash
   cd backend
   python3 -m venv .venv
   ```

2. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows (PowerShell):
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - On Windows (cmd.exe):
     ```cmd
     .venv\Scripts\activate.bat
     ```

3. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Run the server:
   Ensure your virtual environment is activated (your prompt shows `.venv`).
   From the project root (so the database file is created at `backend/life_metrics.db`):
   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   Alternatively, you can run directly from within the `backend/` folder:
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. Open your browser to http://localhost:8000/docs to explore the API.
