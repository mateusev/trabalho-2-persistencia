from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlmodel import Session, select, col
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone

from database import get_session
from models.carteira_estudantil import CarteiraEstudantil, CarteiraEstudantilBase, CarteiraWithAluno
from models.aluno import Aluno, AlunoBase

CarteiraWithAluno.model_rebuild(_types_namespace={"AlunoBase": AlunoBase})

router = APIRouter(
    prefix="/carteiras",
    tags=["Carteiras Estudantis"],
)


@router.post("/", response_model=CarteiraEstudantil, status_code=status.HTTP_201_CREATED)
def create_carteira(carteira: CarteiraEstudantilBase, id_aluno: int, session: Session = Depends(get_session)):
    # 1. Verifica se o Aluno existe
    aluno = session.get(Aluno, id_aluno)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado para emissão da carteira.")


    carteira_existente = session.exec(select(CarteiraEstudantil).where(CarteiraEstudantil.id_aluno == id_aluno)).first()
    if carteira_existente:
        raise HTTPException(status_code=400, detail="Este aluno já possui uma carteira estudantil.")

    if session.exec(select(CarteiraEstudantil).where(
            CarteiraEstudantil.numero_de_registro == carteira.numero_de_registro)).first():
        raise HTTPException(status_code=400, detail="Número de registro já existente.")

    # Criação do objeto completo
    dados_carteira = carteira.model_dump()
    dados_carteira["id_aluno"] = id_aluno

    nova_carteira = CarteiraEstudantil.model_validate(dados_carteira)

    session.add(nova_carteira)
    session.commit()
    session.refresh(nova_carteira)
    return nova_carteira



@router.get("/", response_model=list[CarteiraWithAluno])
def list_carteiras(
        offset: int = 0,
        limit: int = Query(default=10, le=100),
        status_ativa: bool | None = Query(None, description="Filtrar por status (Ativa/Inativa)"),
        somente_validas: bool = Query(False,
                                      description="Se True, retorna apenas carteiras dentro do prazo de validade"),
        session: Session = Depends(get_session)
):
    statement = select(CarteiraEstudantil).options(joinedload(CarteiraEstudantil.aluno))

    # Filtro por Status
    if status_ativa is not None:
        statement = statement.where(CarteiraEstudantil.status_carteira == status_ativa)

    if somente_validas:
        agora = datetime.now(timezone.utc)
        statement = statement.where(CarteiraEstudantil.validade > agora)

    statement = statement.order_by(col(CarteiraEstudantil.data_criacao).desc())

    return session.exec(statement.offset(offset).limit(limit)).unique().all()


@router.get("/{carteira_id}", response_model=CarteiraWithAluno)
def get_carteira(carteira_id: int, session: Session = Depends(get_session)):
    statement = (
        select(CarteiraEstudantil)
        .where(CarteiraEstudantil.id == carteira_id)
        .options(joinedload(CarteiraEstudantil.aluno))
    )
    carteira = session.exec(statement).unique().first()

    if not carteira:
        raise HTTPException(status_code=404, detail="Carteira não encontrada")
    return carteira


@router.get("/busca/por-aluno", response_model=list[CarteiraWithAluno])
def get_carteira_by_aluno_name(
        nome_aluno: str = Query(..., description="Nome parcial do aluno"),
        session: Session = Depends(get_session)
):
    """
    Busca carteiras fazendo JOIN com a tabela de Alunos e filtrando pelo nome do aluno.
    """
    statement = (
        select(CarteiraEstudantil)
        .join(Aluno)  # Join explícito para filtrar
        .where(col(Aluno.nome).contains(nome_aluno))
        .options(joinedload(CarteiraEstudantil.aluno))  # Carrega os dados do aluno no retorno
    )

    return session.exec(statement).unique().all()


@router.patch("/{carteira_id}", response_model=CarteiraEstudantil)
def update_carteira(
        carteira_id: int,
        validade_nova: datetime | None = None,
        status_novo: bool | None = None,
        session: Session = Depends(get_session)
):
    db_carteira = session.get(CarteiraEstudantil, carteira_id)
    if not db_carteira:
        raise HTTPException(status_code=404, detail="Carteira não encontrada")

    if validade_nova:
        db_carteira.validade = validade_nova
    if status_novo is not None:
        db_carteira.status_carteira = status_novo

    session.add(db_carteira)
    session.commit()
    session.refresh(db_carteira)
    return db_carteira


# DELETE
@router.delete("/{carteira_id}")
def delete_carteira(carteira_id: int, session: Session = Depends(get_session)):
    db_carteira = session.get(CarteiraEstudantil, carteira_id)
    if not db_carteira:
        raise HTTPException(status_code=404, detail="Carteira não encontrada")

    session.delete(db_carteira)
    session.commit()
    return {"ok": True}