from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .professor import Professor
    from .disciplina import Disciplina

class DepartamentoBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    nome: str = Field(unique=True, index=True)
    codigo_departamento: str = Field(unique=True, max_length=5, index=True)

class Departamento(DepartamentoBase, table=True):
    professores_departamento: list["Professor"] = Relationship(back_populates="departamento")
    disciplinas_departamento: list["Disciplina"] = Relationship(back_populates="departamento")

class DepartamentoWithProfessores(DepartamentoBase):
    professores_departamento: list["ProfessorBase"] = []