from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from hybrid import hybrid_search


# ==========================================
# INITIALIZE API
# ==========================================

app = FastAPI(
    title="UniGuide AI API",
    description="AI-powered university student assistant",
    version="1.0.0"
)


# ==========================================
# CORS CONFIGURATION
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ==========================================
# REQUEST MODEL
# ==========================================

class QuestionRequest(BaseModel):
    question: str


# ==========================================
# HOME ROUTE
# ==========================================

@app.get("/")
def home():

    return {
        "message": "UniGuide AI Backend is running",
        "status": "online"
    }


# ==========================================
# CHAT ENDPOINT
# ==========================================

@app.post("/chat")
def chat(request: QuestionRequest):

    result = hybrid_search(request.question)

    return result


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "UniGuide AI"
    }