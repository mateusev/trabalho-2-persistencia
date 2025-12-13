from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from .professor import Professor

if TYPE_CHECKING:
    from .departamento import Departamento
    from .matricula import Matricula

class Disciplina(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    carga_horaria: int
    id_professor: int = Field(default=None, foreign_key="professor.id")
    departamento_disciplina: str = Field(default=None, foreign_key="departamento.codigo_departamento")

    professor_disciplina: "Professor" = Relationship(back_populates="disciplina")
    matriculas: list["Matricula"] = Relationship(back_populates="disciplina")