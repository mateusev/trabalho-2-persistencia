from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlmodel import Session, select, func, col
from sqlalchemy.orm import joinedload, selectinload

from database import get_session
from models.aluno import Aluno, AlunoBase, AlunoWithCarteira
from models.matricula import Matricula
from models.disciplina import Disciplina

router = APIRouter(
    prefix="/alunos",
    tags=["Alunos"],
)


@router.get("/{aluno_id}", response_model=AlunoWithCarteira)
def read_aluno(aluno_id: int, session: Session = Depends(get_session)):
    """
    """
    statement = (
        select(Aluno)
        .where(Aluno.id == aluno_id)
        .options(
            joinedload(Aluno.carteira),
            selectinload(Aluno.disciplinas)
        )
    )
    aluno = session.exec(statement).unique().first()

    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return aluno


@router.get("/", response_model=list[AlunoWithCarteira])  # Usando list nativo
def read_alunos(
        offset: int = 0,
        limit: int = Query(default=10, le=100),
        nome: str | None = Query(None, description="Filtrar por nome parcial (Case insensitive)"),
        ano_nascimento: int | None = Query(None, description="Filtrar por ano de nascimento"),
        ordenar_por_nome: bool = Query(False, description="Ordenar alfabeticamente por nome"),
        session: Session = Depends(get_session)
):
    """
    Lista alunos com paginação e filtros.
    Traz Carteira e Disciplinas carregadas (Eager Loading).
    """
    statement = select(Aluno).options(
        joinedload(Aluno.carteira),
        selectinload(Aluno.disciplinas)
    )

    # Busca por texto parcial
    if nome:
        statement = statement.where(col(Aluno.nome).contains(nome))

    #  Filtro por Ano (Extraindo ano da data de nascimento)
    if ano_nascimento:
        # strftime funciona bem no SQLite para extrair o ano
        statement = statement.where(func.extract('year', Aluno.data_nascimento) == ano_nascimento)
    #  Ordenação
    if ordenar_por_nome:
        statement = statement.order_by(Aluno.nome)

    resultados = session.exec(statement.offset(offset).limit(limit)).unique().all()
    return resultados


@router.post("/", response_model=Aluno, status_code=status.HTTP_201_CREATED)
def create_aluno(aluno: AlunoBase, session: Session = Depends(get_session)):
    # Validação extra: CPF Único
    if session.exec(select(Aluno).where(Aluno.cpf == aluno.cpf)).first():
        raise HTTPException(status_code=400, detail="CPF já cadastrado.")

    novo_aluno = Aluno.model_validate(aluno)
    session.add(novo_aluno)
    session.commit()
    session.refresh(novo_aluno)
    return novo_aluno


@router.put("/{aluno_id}", response_model=Aluno)
def update_aluno(aluno_id: int, aluno_data: AlunoBase, session: Session = Depends(get_session)):
    db_aluno = session.get(Aluno, aluno_id)
    if not db_aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    dados = aluno_data.model_dump(exclude_unset=True)
    for key, value in dados.items():
        setattr(db_aluno, key, value)

    session.add(db_aluno)
    session.commit()
    session.refresh(db_aluno)
    return db_aluno


# Delete
@router.delete("/{aluno_id}")
def delete_aluno(aluno_id: int, session: Session = Depends(get_session)):
    aluno = session.get(Aluno, aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    session.delete(aluno)
    session.commit()
    return {"ok": True}


#  Contagem Total
@router.get("/stats/contagem", response_model=dict)
def count_alunos(session: Session = Depends(get_session)):
    """
    Retorna o total de alunos cadastrados no banco.
    """
    total = session.exec(select(func.count(Aluno.id))).one()
    return {"total_alunos": total}


# Consulta Complexa: Alunos por Disciplina
@router.get("/by-disciplina/{disciplina_id}", response_model=list[Aluno])  # Usando list nativo
def get_alunos_por_disciplina(disciplina_id: int, session: Session = Depends(get_session)):
    """
    Retorna todos os alunos matriculados em uma disciplina específica.
    Faz um JOIN entre Aluno e Matricula.
    """
    statement = (
        select(Aluno)
        .join(Matricula)  # Join explícito na tabela de associação
        .where(Matricula.disciplina_id == disciplina_id)
        .options(selectinload(Aluno.disciplinas))
    )

    return session.exec(statement).unique().all()