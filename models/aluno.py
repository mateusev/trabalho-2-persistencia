from sqlmodel import SQLModel

class Aluno(SQLModel, table=True):
    id: int 
    nome: str 
    numero_matricula: int
    email: str