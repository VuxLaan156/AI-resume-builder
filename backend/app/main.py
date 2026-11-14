from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
@app.get("/")
def root():
    return {"message": "Welcome to the AI resume builder API!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

