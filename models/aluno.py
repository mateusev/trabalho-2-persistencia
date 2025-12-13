from typing import TYPE_CHECKING # Importações de tipagem
from sqlmodel import SQLModel, Field, Relationship
from datetime import date

if TYPE_CHECKING:
    from .carteira_estudantil import Carteira_estudantil
    from .matricula import Matricula

class Aluno(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    cpf: str = Field(unique=True, max_length=14) 
    data_nascimento: date
    numero_matricula: int
    email: str

   
    carteira: "Carteira_estudantil" = Relationship(
        back_populates="aluno",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"}
    )

    matriculas_disciplinas: list["Matricula"] = Relationship(
        back_populates="aluno",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )