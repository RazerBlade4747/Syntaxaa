from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
import os

# Read database connection parameters from environment variables
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASS = os.getenv("MYSQL_PASS")
MYSQL_NAME = os.getenv("MYSQL_NAME", "defaultdb")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))


def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=DB_PORT
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Automatically runs on application startup to initialize MySQL tables."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teacher_codes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                teacher_id INT NOT NULL,
                code VARCHAR(50) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Cloud database tables initialized successfully!")
    except Exception as e:
        print(f"⚠️ Could not initialize database table: {e}")
    
    yield  # Application handles incoming HTTP requests here


app = FastAPI(title="Syntaxaa Shared API", lifespan=lifespan)


class TeacherCodeSchema(BaseModel):
    teacher_id: int
    code: str


@app.get("/")
def health_check():
    return {"status": "online", "system": "Syntaxaa Central Server"}


@app.post("/api/teacher-codes/create")
def create_teacher_code(data: TeacherCodeSchema):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO teacher_codes (teacher_id, code) VALUES (%s, %s)",
            (data.teacher_id, data.code)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "success", "message": "Code registered globally"}
    except mysql.connector.IntegrityError:
        raise HTTPException(status_code=400, detail="Teacher code already exists")
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@app.get("/api/teacher-codes/verify/{code}")
def verify_teacher_code(code: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM teacher_codes WHERE code = %s", (code,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Invalid teacher code")
        
        return {"status": "valid", "data": result}
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
