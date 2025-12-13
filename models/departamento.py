from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
    from .professor import Professor
    from .disciplina import Disciplina

class Departamento(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str = Field(unique=True, index = True)
    codigo_departamento: str = Field(unique=True, max_length=5, index=True)
    professores_departamento: list["Professor"] = Relationship(back_populates="departamento")
    disciplinas_departamento: list["Disciplina"] = Relationship(back_populates="departamento")

