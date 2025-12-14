from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .aluno import Aluno, AlunoBase

class CarteiraEstudantilBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    validade: datetime
    data_criacao: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status_carteira: bool = Field(default=True)
    numero_de_registro: str = Field(unique=True, max_length=10)

class CarteiraEstudantil(CarteiraEstudantilBase, table=True):
    id_aluno: int = Field(foreign_key="aluno.id")
    aluno: "Aluno" = Relationship(back_populates="carteira")

class CarteiraWithAluno(CarteiraEstudantilBase):
    aluno: "AlunoBase"