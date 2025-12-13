from sqlmodel import SQLModel, Field, Relationship
from .departamento import Departamento
from .disciplina import Disciplina

class Professor(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    email: str = Field(unique=True)

    id_departamento: int = Field(foreign_key="departamento.id" )

    disciplinas_ministradas: list["Disciplina"] = Relationship(back_populates="professor_disciplina")