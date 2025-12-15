from fastapi import APIRouter, HTTPException, Depends, Query, status, Body
from sqlmodel import Session, select, func, col
from sqlalchemy.orm import selectinload

from database import get_session
from models.departamento import Departamento, DepartamentoBase
from models.professor import Professor
from models.disciplina import Disciplina

Departamento.model_rebuild(_types_namespace={
    "Professor": Professor,
    "Disciplina": Disciplina
})

router = APIRouter(
    prefix="/departamentos",
    tags=["Departamentos"],
)


@router.post("/", response_model=Departamento, status_code=status.HTTP_201_CREATED)
def create_departamento(departamento: DepartamentoBase, session: Session = Depends(get_session)):
    if session.exec(
            select(Departamento).where(Departamento.codigo_departamento == departamento.codigo_departamento)).first():
        raise HTTPException(status_code=400, detail="Código de departamento já existente.")

    if session.exec(select(Departamento).where(Departamento.nome == departamento.nome)).first():
        raise HTTPException(status_code=400, detail="Nome de departamento já existente.")

    novo_dep = Departamento.model_validate(departamento)
    session.add(novo_dep)
    session.commit()
    session.refresh(novo_dep)
    return novo_dep


@router.get("/", response_model=list[Departamento])
def list_departamentos(
        offset: int = 0,
        limit: int = Query(default=10, le=100),
        nome: str | None = Query(None, description="Filtrar por nome"),
        session: Session = Depends(get_session)
):
    statement = select(Departamento).options(
        selectinload(Departamento.professores_departamento),
        selectinload(Departamento.disciplinas_departamento)
    )

    if nome:
        statement = statement.where(col(Departamento.nome).contains(nome))

    return session.exec(statement.offset(offset).limit(limit)).unique().all()


@router.get("/{departamento_id}", response_model=Departamento)
def get_departamento(departamento_id: int, session: Session = Depends(get_session)):
    statement = (
        select(Departamento)
        .where(Departamento.id == departamento_id)
        .options(
            selectinload(Departamento.professores_departamento),
            selectinload(Departamento.disciplinas_departamento)
        )
    )
    departamento = session.exec(statement).unique().first()

    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    return departamento


@router.patch("/{departamento_id}", response_model=Departamento)
def update_departamento(
        departamento_id: int,
        nome: str | None = Body(default=None),
        codigo_departamento: str | None = Body(default=None),
        session: Session = Depends(get_session)
):
    db_dep = session.get(Departamento, departamento_id)
    if not db_dep:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")

    # Atualiza só se o usuário enviou o valor
    if nome is not None:
        db_dep.nome = nome

    if codigo_departamento is not None:
        db_dep.codigo_departamento = codigo_departamento

    session.add(db_dep)
    session.commit()
    session.refresh(db_dep)
    return db_dep


@router.delete("/{departamento_id}")
def delete_departamento(departamento_id: int, session: Session = Depends(get_session)):
    dep = session.get(Departamento, departamento_id)
    if not dep:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")

    session.delete(dep)
    session.commit()
    return {"ok": True}


@router.get("/stats/professores", response_model=list[dict])
def stats_professores_por_departamento(session: Session = Depends(get_session)):
    statement = (
        select(Departamento.nome, func.count(Professor.id).label("total_professores"))
        .join(Professor, isouter=True)
        .group_by(Departamento.id)
    )

    resultados = session.exec(statement).all()
    return [{"departamento": row.nome, "total_professores": row.total_professores} for row in resultados]