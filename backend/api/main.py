from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Student(BaseModel):
    first_name: str
    last_name: str
    # Otros campos del estudiante

@app.post("/register-student/")
async def register_student(student: Student):
    # Lógica para interactuar con la base de datos usando Clases Repository
    # Aquí deberías usar las clases Repository para agregar o actualizar datos
    # Puedes utilizar un ORM como SQLAlchemy para interactuar con la base de datos
    # Por simplicidad, solo se imprime la información del estudiante en este ejemplo
    return {"message": f"Student registered: {student.first_name} {student.last_name}"}