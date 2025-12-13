from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .aluno import Aluno
    from .disciplina import Disciplina

class Matricula(SQLModel, table=True):
    id_aluno: int | None = Field(default=None, foreign_key="aluno.id",primary_key=True)
    disciplina_id: int | None = Field(default=None, foreign_key="disciplina.id", primary_key=True)

    nota_final: float | None = Field(default=None)
    numero_faltas: int = Field(default=0)
    semestre: str = Field(max_length=4)

    aluno: "Aluno" = Relationship(back_populates="matricula")
    disciplina: "Disciplina" = Relationship(back_populates="matricula")
