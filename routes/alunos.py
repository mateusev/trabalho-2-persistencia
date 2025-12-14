from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlmodel import Session, select, col, func
from sqlalchemy.orm import joinedload, selectinload
from typing import List

from ..database import get_session
from ..models.aluno import Aluno, AlunoBase, AlunoWithCarteira


router = APIRouter(prefix="/alunos", tags=["Alunos"])


@router.post("/", response_model=Aluno)
def create_aluno(aluno: AlunoBase, session: Session = Depends(get_session)):
    # Validação de CPF único
    db_aluno = session.exec(select(Aluno).where(Aluno.cpf == aluno.cpf)).first()
    if db_aluno:
        raise HTTPException(status_code=400, detail="CPF já cadastrado.")

    novo_aluno = Aluno.model_validate(aluno)
    session.add(novo_aluno)
    session.commit()
    session.refresh(novo_aluno)
    return novo_aluno


@router.get("/", response_model=List[Aluno])
def list_alunos(
        offset: int = 0,
        limit: int = Query(default=10, le=100),
        nome: str | None = Query(None),
        ano_nascimento: int | None = Query(None),
        session: Session = Depends(get_session)
):
    # Eager Load: Traz a carteira e as disciplinas automaticamente
    # selectinload é geralmente melhor para listas (disciplinas), joinedload para 1-para-1 (carteira)
    statement = select(Aluno).options(
        joinedload(Aluno.carteira),
        selectinload(Aluno.disciplinas)
    )

    if nome:
        statement = statement.where(col(Aluno.nome).contains(nome))

    if ano_nascimento:
        statement = statement.where(func.strftime('%Y', Aluno.data_nascimento) == str(ano_nascimento))

    # .unique() é essencial aqui pois estamos carregando relacionamentos de lista
    return session.exec(statement.offset(offset).limit(limit)).unique().all()


@router.get("/{aluno_id}", response_model=AlunoWithCarteira)
def get_aluno(aluno_id: int, session: Session = Depends(get_session)):
    statement = (
        select(Aluno)
        .where(Aluno.id == aluno_id)
        .options(joinedload(Aluno.carteira), selectinload(Aluno.disciplinas))
    )

    aluno = session.exec(statement).unique().first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return aluno


@router.put("/{aluno_id}", response_model=Aluno)
def update_aluno(aluno_id: int, aluno_data: AlunoBase, session: Session = Depends(get_session)):
    db_aluno = session.get(Aluno, aluno_id)
    if not db_aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    for key, value in aluno_data.model_dump(exclude_unset=True).items():
        setattr(db_aluno, key, value)

    session.add(db_aluno)
    session.commit()
    session.refresh(db_aluno)
    return db_aluno


@router.delete("/{aluno_id}")
def delete_aluno(aluno_id: int, session: Session = Depends(get_session)):
    db_aluno = session.get(Aluno, aluno_id)
    if not db_aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    session.delete(db_aluno)
    session.commit()
    return {"ok": True}