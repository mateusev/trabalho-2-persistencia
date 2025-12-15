from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlmodel import Session, select, func, col
from sqlalchemy.orm import joinedload, selectinload

from database import get_session
from models.disciplina import Disciplina, DisciplinaBase
from models.professor import Professor
from models.departamento import Departamento
from models.aluno import Aluno
from models.matricula import Matricula

Disciplina.model_rebuild(_types_namespace={
    "Aluno": Aluno,
    "Professor": Professor,
    "Departamento": Departamento,
    "Matricula": Matricula
})

router = APIRouter(
    prefix="/disciplinas",
    tags=["Disciplinas"],
)


@router.post("/", response_model=Disciplina, status_code=status.HTTP_201_CREATED)
def create_disciplina(disciplina: Disciplina, session: Session = Depends(get_session)):
    if disciplina.id_professor and not session.get(Professor, disciplina.id_professor):
        raise HTTPException(status_code=404, detail="Professor informado não encontrado.")

    if disciplina.departamento_disciplina_cod:
        dep = session.exec(select(Departamento).where(
            Departamento.codigo_departamento == disciplina.departamento_disciplina_cod)).first()
        if not dep:
            raise HTTPException(status_code=404, detail="Departamento informado não encontrado.")

    disciplina.id = None

    session.add(disciplina)
    session.commit()
    session.refresh(disciplina)
    return disciplina


@router.get("/", response_model=list[Disciplina])
def list_disciplinas(
        offset: int = 0,
        limit: int = Query(default=10, le=100),
        nome: str | None = Query(None, description="Filtro por nome parcial"),
        id_professor: int | None = Query(None, description="Filtrar disciplinas de um professor"),
        cod_departamento: str | None = Query(None, description="Filtrar por código do departamento"),
        session: Session = Depends(get_session)
):
    statement = select(Disciplina).options(
        joinedload(Disciplina.professor_disciplina),
        joinedload(Disciplina.departamento),
        selectinload(Disciplina.alunos)
    )

    if nome:
        statement = statement.where(col(Disciplina.nome).contains(nome))

    if id_professor:
        statement = statement.where(Disciplina.id_professor == id_professor)

    if cod_departamento:
        statement = statement.where(Disciplina.departamento_disciplina_cod == cod_departamento)

    statement = statement.order_by(Disciplina.nome)

    return session.exec(statement.offset(offset).limit(limit)).unique().all()


@router.get("/{disciplina_id}", response_model=Disciplina)
def get_disciplina(disciplina_id: int, session: Session = Depends(get_session)):
    statement = (
        select(Disciplina)
        .where(Disciplina.id == disciplina_id)
        .options(
            joinedload(Disciplina.professor_disciplina),
            joinedload(Disciplina.departamento),
            selectinload(Disciplina.alunos)
        )
    )
    disciplina = session.exec(statement).unique().first()

    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")
    return disciplina


@router.put("/{disciplina_id}", response_model=Disciplina)
def update_disciplina(disciplina_id: int, disciplina_data: DisciplinaBase, session: Session = Depends(get_session)):
    db_disciplina = session.get(Disciplina, disciplina_id)
    if not db_disciplina:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")

    dados = disciplina_data.model_dump(exclude_unset=True)
    for key, value in dados.items():
        setattr(db_disciplina, key, value)

    session.add(db_disciplina)
    session.commit()
    session.refresh(db_disciplina)
    return db_disciplina


@router.delete("/{disciplina_id}")
def delete_disciplina(disciplina_id: int, session: Session = Depends(get_session)):
    disciplina = session.get(Disciplina, disciplina_id)
    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")

    session.delete(disciplina)
    session.commit()
    return {"ok": True}


@router.get("/stats/alunos-por-disciplina", response_model=list[dict])
def stats_alunos_por_disciplina(session: Session = Depends(get_session)):
    statement = (
        select(Disciplina.nome, func.count(Matricula.id_aluno).label("total_alunos"))
        .join(Matricula, isouter=True)
        .group_by(Disciplina.id)
    )

    resultados = session.exec(statement).all()

    return [{"disciplina": row.nome, "total_alunos": row.total_alunos} for row in resultados]