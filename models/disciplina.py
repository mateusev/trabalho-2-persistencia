from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

from .departamento import Departamento, DepartamentoBase
from .professor import Professor, ProfessorBase

# 1. IMPORTAÇÃO REAL (Mova o Matricula para fora do TYPE_CHECKING)
from .matricula import Matricula

if TYPE_CHECKING:
    from .aluno import Aluno
    # O Matricula saiu daqui e foi para cima


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

    alunos: list["Aluno"] = Relationship(
        back_populates="disciplinas",
        link_model=Matricula
    )


class DisciplinaWithProfessor(DisciplinaBase):
    professor_disciplina: ProfessorBase | None = None