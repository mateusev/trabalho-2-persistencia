from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlmodel import Session, select, col
from sqlalchemy.orm import joinedload, selectinload

from database import get_session
from models.professor import Professor, ProfessorBase
from models.departamento import Departamento
from models.disciplina import Disciplina

Professor.model_rebuild(_types_namespace={
    "Departamento": Departamento,
    "Disciplina": Disciplina
})

router = APIRouter(
    prefix="/professores",
    tags=["Professores"],
)


@router.post("/", response_model=Professor, status_code=status.HTTP_201_CREATED)
def create_professor(professor: Professor, session: Session = Depends(get_session)):
    if professor.id_departamento:
        if not session.get(Departamento, professor.id_departamento):
            raise HTTPException(status_code=404, detail="Departamento não encontrado.")

    if session.exec(select(Professor).where(Professor.email == professor.email)).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado.")

    professor.id = None

    session.add(professor)
    session.commit()
    session.refresh(professor)
    return professor


@router.get("/", response_model=list[Professor])
def list_professores(
        offset: int = 0,
        limit: int = Query(default=10, le=100),
        nome: str | None = Query(None, description="Filtrar por nome parcial"),
        id_departamento: int | None = Query(None, description="Filtrar por departamento"),
        session: Session = Depends(get_session)
):
    statement = select(Professor).options(
        joinedload(Professor.departamento),
        selectinload(Professor.disciplinas_ministradas)
    )

    if nome:
        statement = statement.where(col(Professor.nome).contains(nome))

    if id_departamento:
        statement = statement.where(Professor.id_departamento == id_departamento)

    statement = statement.order_by(Professor.nome)

    return session.exec(statement.offset(offset).limit(limit)).unique().all()


@router.get("/{professor_id}", response_model=Professor)
def get_professor(professor_id: int, session: Session = Depends(get_session)):
    statement = (
        select(Professor)
        .where(Professor.id == professor_id)
        .options(
            joinedload(Professor.departamento),
            selectinload(Professor.disciplinas_ministradas)
        )
    )
    professor = session.exec(statement).unique().first()

    if not professor:
        raise HTTPException(status_code=404, detail="Professor não encontrado")
    return professor


@router.put("/{professor_id}", response_model=Professor)
def update_professor(professor_id: int, prof_data: ProfessorBase, session: Session = Depends(get_session)):
    db_prof = session.get(Professor, professor_id)
    if not db_prof:
        raise HTTPException(status_code=404, detail="Professor não encontrado")

    dados = prof_data.model_dump(exclude_unset=True)
    for key, value in dados.items():
        setattr(db_prof, key, value)

    session.add(db_prof)
    session.commit()
    session.refresh(db_prof)
    return db_prof


@router.delete("/{professor_id}")
def delete_professor(professor_id: int, session: Session = Depends(get_session)):
    prof = session.get(Professor, professor_id)
    if not prof:
        raise HTTPException(status_code=404, detail="Professor não encontrado")

    session.delete(prof)
    session.commit()
    return {"ok": True}