from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from .aluno import Aluno


class Carteira_estudantil(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    validade: datetime
    id_aluno: int = Field(default=None, foreign_key="aluno.id")
    data_criacao: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status_carteira: bool = Field(default=True)
    numero_de_registro: str = Field(unique=True, max_length=10)