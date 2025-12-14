from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
from .departamento import Departamento, DepartamentoBase

if TYPE_CHECKING:
    from .disciplina import Disciplina


class ProfessorBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    email: str = Field(unique=True)


class Professor(ProfessorBase, table=True):
    id_departamento: int = Field(foreign_key="departamento.id")

    departamento: "Departamento" = Relationship(back_populates="professores_departamento")
    disciplinas_ministradas: list["Disciplina"] = Relationship(back_populates="professor_disciplina")


class ProfessorWithDepartamento(ProfessorBase):
    departamento: DepartamentoBase