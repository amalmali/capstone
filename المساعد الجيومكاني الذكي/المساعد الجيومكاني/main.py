import logging
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware  
from fastapi.staticfiles import StaticFiles         
from contextlib import asynccontextmanager


from routers.chat import router


from services.retriever_service import register_pdf
from services.db import Database
from config import DATA_DIR, DB_CONFIG


logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
   
    logging.info("📚 جاري تحميل ملفات اللوائح القانونية...")
    for pdf in DATA_DIR.glob("*.pdf"):
        register_pdf(pdf.stem, str(pdf))
    
   
    logging.info("🗄️ جاري الاتصال بقاعدة البيانات الجغرافية...")
    db = Database(DB_CONFIG)
    app.state.db_gps = db 
    
   
    app.state.current_gps = {"is_inside": False, "region": None}
    
    yield
   
    if hasattr(app.state, "db_gps"):
        app.state.db_gps.close()
        logging.info("🔌 تم إغلاق اتصال قاعدة البيانات.")


app = FastAPI(title="Smart Kiosk AI & GPS", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="templates"), name="static")


app.include_router(router)

@app.get("/")
def read_root():
   
    return RedirectResponse(url="/llm/chat")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)