from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.rag_service import answer
from config import BASE_DIR
import uuid

router = APIRouter()
templates = Jinja2Templates(directory=BASE_DIR / "templates")

PDF_NAME = "protected_areas"

@router.get("/", response_class=HTMLResponse)
async def chat(request: Request):
    session_id = str(uuid.uuid4())
    response = templates.TemplateResponse(
        "chat.html",
        {"request": request}
    )
    response.set_cookie("session_id", session_id)
    return response

@router.post("/ask", response_class=HTMLResponse)
async def ask(request: Request, query: str = Form(...)):
    session_id = request.cookies.get("session_id")
    response, context = answer(query, PDF_NAME, session_id)

    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "query": query,
            "response": response
        }
    )
