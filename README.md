# Simple FastAPI Backend

This is a simple Python backend using FastAPI with Swagger integration to verify functionality.

## Setup

1.  **Create a virtual environment (optional but recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Configuration:**
    Create a `.env` file in the root directory and add your Groq API key:
    ```env
    GROQ_API_KEY=your_groq_api_key_here
    DATABASE_URL=sqlite:///./database.db
    ```


## running with script
You can also use the included script to handle setup and running automatically:

```bash
./run.sh
```

## Running the Application

Run the server using:

```bash
python3 main.py
```
Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

## API Documentation

Once the server is running, you can access the interactive API documentation (Swagger UI) at:

-   **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
-   **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Test Endpoints

-   **Test Route:** [http://localhost:8000/test](http://localhost:8000/test)
-   **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)
