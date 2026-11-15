from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.health import router as health_router
from .api.profiles import router as profiles_router
from .api.projects import router as projects_router
from .api.skills import router as skills_router

app = FastAPI(title = "AI resume builder", description = "AI resume builder is a web application that allows users to create professional resumes using artificial intelligence. The application uses natural language processing and machine learning algorithms to analyze user input and generate a customized resume that highlights the user's skills and experience.", version = "1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(profiles_router)
app.include_router(projects_router)
app.include_router(skills_router)
