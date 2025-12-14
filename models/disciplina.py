from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
from .departamento import Departamento, DepartamentoBase
from .professor import Professor, ProfessorBase

if TYPE_CHECKING:
    from .matricula import Matricula

class DisciplinaBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    carga_horaria: int

class Disciplina(DisciplinaBase, table=True):
    id_professor: int | None = Field(default=None, foreign_key="professor.id")
    departamento_disciplina_cod: str | None = Field(default=None, foreign_key="departamento.codigo_departamento")

    professor_disciplina: "Professor" = Relationship(back_populates="disciplinas_ministradas")
    departamento: "Departamento" = Relationship(back_populates="disciplinas_departamento")
    matriculas: list["Matricula"] = Relationship(back_populates="disciplina")

class DisciplinaWithProfessor(DisciplinaBase):
    professor_disciplina: ProfessorBase | None = None