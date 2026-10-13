import asyncio
import io
import logging
import os
import sys
import zipfile
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware

ROOT_DIR = Path(__file__).parent
APP_DIR = ROOT_DIR.parent / "windows_app"
load_dotenv(ROOT_DIR / '.env')
sys.path.insert(0, str(APP_DIR))

from guardian_shield import __version__  # noqa: E402
from guardian_shield.linkcheck import check  # noqa: E402
from guardian_shield.signatures import REMOTE_TOOLS, SCAM_COMMANDS, SCAM_DOMAINS  # noqa: E402

client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")


class CheckRequest(BaseModel):
    text: str = Field(max_length=5000)


class UrlResult(BaseModel):
    url: str
    host: str
    score: int


class CheckResult(BaseModel):
    verdict: str
    score: int
    reasons: List[str]
    urls: List[UrlResult]


class Stats(BaseModel):
    checks: int = 0
    downloads: int = 0


class Signatures(BaseModel):
    version: str
    remote_tools: List[str]
    commands: List[str]
    scam_domain_count: int


async def bump(field: str):
    await db.stats.update_one({"key": "global"}, {"$inc": {field: 1}}, upsert=True)


@api_router.get("/")
async def root():
    return {"message": "Guardian Shield API", "version": __version__}


@api_router.post("/check", response_model=CheckResult)
async def check_link(req: CheckRequest):
    await bump("checks")
    return check(req.text)


@api_router.get("/stats", response_model=Stats)
async def get_stats():
    doc: Optional[dict] = await db.stats.find_one({"key": "global"}, {"_id": 0, "checks": 1, "downloads": 1})
    return Stats(**(doc or {}))


@api_router.get("/signatures", response_model=Signatures)
async def signatures():
    return Signatures(version=__version__, remote_tools=[t["name"] for t in REMOTE_TOOLS],
                      commands=[c["name"] for c in SCAM_COMMANDS], scam_domain_count=len(SCAM_DOMAINS))


def build_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for path in APP_DIR.rglob("*"):
            rel = path.relative_to(APP_DIR)
            if path.is_file() and not any(p in ("__pycache__", ".pytest_cache", ".build", "dist", "build") for p in rel.parts):
                z.write(path, Path("GuardianShield") / rel)
    return buf.getvalue()


@api_router.get("/download")
async def download():
    await bump("downloads")
    name = f"GuardianShield-{__version__}-windows.zip"
    data = await asyncio.to_thread(build_zip)
    return StreamingResponse(io.BytesIO(data), media_type="application/zip",
                             headers={"Content-Disposition": f'attachment; filename="{name}"'})


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
