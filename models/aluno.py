from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .carteira_estudantil import CarteiraEstudantil, CarteiraEstudantilBase
    from .matricula import Matricula

class AlunoBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    cpf: str = Field(unique=True, max_length=14)
    data_nascimento: date
    numero_matricula: int
    email: str

class Aluno(AlunoBase, table=True):
    carteira: "CarteiraEstudantil" = Relationship(
        back_populates="aluno",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"}
    )

    matriculas_disciplinas: list["Matricula"] = Relationship(
        back_populates="aluno",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class AlunoWithCarteira(AlunoBase):
    carteira: CarteiraEstudantilBase | None = None