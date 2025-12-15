from fastapi import FastAPI
from routes import (
    alunos,
    carteiras,
    disciplinas,
    professores,
    departamentos,
    matriculas
)


app = FastAPI()

app.include_router(alunos.router)
app.include_router(carteiras.router)
app.include_router(professores.router)
app.include_router(disciplinas.router)
app.include_router(matriculas.router)
app.include_router(departamentos.router)

