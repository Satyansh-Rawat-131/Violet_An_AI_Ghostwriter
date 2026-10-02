import threading
import uuid
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

import violet_agent as va

api = FastAPI()
api.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SESSIONS: dict[str, list] = {}
DOCS: dict[str, str] = {}
LOCK = threading.Lock()


class ChatIn(BaseModel):
    message: str
    session_id: str | None = None


def text_of(msg) -> str:
    c = msg.content
    if isinstance(c, list):
        return "".join(b.get("text", "") for b in c if isinstance(b, dict))
    return c or ""


@api.post("/chat")
def chat(body: ChatIn):
    sid = body.session_id or str(uuid.uuid4())
    history = SESSIONS.get(sid, [])
    start = len(history) + 1

    with LOCK:
        va.docu_content = DOCS.get(sid, "")
        try:
            result = va.app.invoke({"messages": history + [HumanMessage(content=body.message)]})
        except Exception as e:
            return {"session_id": sid, "reply": f"Sorry, the model call failed: {e}",
                    "document": DOCS.get(sid, "")}
        DOCS[sid] = va.docu_content

    SESSIONS[sid] = list(result["messages"])
    new = SESSIONS[sid][start:]

    reply = next((text_of(m) for m in reversed(new)
                  if isinstance(m, AIMessage) and text_of(m).strip()), "")
    if not reply:  # e.g. the turn ended on a save
        reply = next((text_of(m) for m in reversed(new) if isinstance(m, ToolMessage)), "")
    return {"session_id": sid, "reply": reply, "document": DOCS.get(sid, "")}


@api.post("/reset/{sid}")
def reset(sid: str):
    SESSIONS.pop(sid, None)
    DOCS.pop(sid, None)
    return {"ok": True}


@api.get("/")
def index():
    return FileResponse(Path(__file__).parent / "index.html")
