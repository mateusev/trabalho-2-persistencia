from fastapi import APIRouter, HTTPException, Depends, Query, status, Body
from sqlmodel import Session, select, func
from sqlalchemy.orm import joinedload

from database import get_session
from models.matricula import Matricula
from models.aluno import Aluno
from models.disciplina import Disciplina

Matricula.model_rebuild(_types_namespace={
    "Aluno": Aluno,
    "Disciplina": Disciplina
})

router = APIRouter(
    prefix="/matriculas",
    tags=["Matrículas"],
)


@router.post("/", response_model=Matricula, status_code=status.HTTP_201_CREATED)
def create_matricula(matricula: Matricula, session: Session = Depends(get_session)):
    if not session.get(Aluno, matricula.id_aluno):
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")

    if not session.get(Disciplina, matricula.disciplina_id):
        raise HTTPException(status_code=404, detail="Disciplina não encontrada.")

    matricula_existente = session.get(Matricula, (matricula.id_aluno, matricula.disciplina_id))
    if matricula_existente:
        raise HTTPException(status_code=400, detail="Aluno já matriculado nesta disciplina.")

    session.add(matricula)
    session.commit()
    session.refresh(matricula)
    return matricula


@router.get("/", response_model=list[Matricula])
def list_matriculas(
        offset: int = 0,
        limit: int = Query(default=10, le=100),
        semestre: str | None = Query(None, description="Filtrar por semestre (ex: 25.1)"),
        nota_minima: float | None = Query(None, description="Filtrar por nota maior ou igual a X"),
        id_aluno: int | None = Query(None, description="Ver histórico de um aluno"),
        disciplina_id: int | None = Query(None, description="Ver info de uma disciplina"),
        session: Session = Depends(get_session)
):
    statement = select(Matricula).options(
        joinedload(Matricula.aluno),
        joinedload(Matricula.disciplina)
    )

    if semestre:
        statement = statement.where(Matricula.semestre == semestre)

    if nota_minima is not None:
        statement = statement.where(Matricula.nota_final >= nota_minima)

    if id_aluno:
        statement = statement.where(Matricula.id_aluno == id_aluno)

    if disciplina_id:
        statement = statement.where(Matricula.disciplina_id == disciplina_id)

    statement = statement.order_by(Matricula.semestre.desc())

    return session.exec(statement.offset(offset).limit(limit)).unique().all()


@router.patch("/{id_aluno}/{disciplina_id}", response_model=Matricula)
def update_matricula(
        id_aluno: int,
        disciplina_id: int,
        nota_final: float | None = Body(default=None),
        numero_faltas: int | None = Body(default=None),
        session: Session = Depends(get_session)
):
    db_matricula = session.get(Matricula, (id_aluno, disciplina_id))
    if not db_matricula:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada.")

    if nota_final is not None:
        db_matricula.nota_final = nota_final

    if numero_faltas is not None:
        db_matricula.numero_faltas = numero_faltas

    session.add(db_matricula)
    session.commit()
    session.refresh(db_matricula)
    return db_matricula


@router.delete("/{id_aluno}/{disciplina_id}")
def delete_matricula(id_aluno: int, disciplina_id: int, session: Session = Depends(get_session)):
    db_matricula = session.get(Matricula, (id_aluno, disciplina_id))
    if not db_matricula:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada.")

    session.delete(db_matricula)
    session.commit()
    return {"ok": True}


@router.get("/stats/media-notas", response_model=list[dict])
def stats_media_notas_por_disciplina(session: Session = Depends(get_session)):
    statement = (
        select(
            Disciplina.nome,
            func.avg(Matricula.nota_final).label("media_notas"),
            func.count(Matricula.id_aluno).label("qtd_alunos")
        )
        .join(Matricula, isouter=False)
        .where(Matricula.nota_final != None)
        .group_by(Disciplina.id)
    )

    resultados = session.exec(statement).all()

    return [
        {
            "disciplina": row.nome,
            "media_notas": round(row.media_notas, 2) if row.media_notas else 0.0,
            "qtd_alunos_avaliados": row.qtd_alunos
        }
        for row in resultados
    ]