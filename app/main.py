from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.agent import run_business_agent
from app.database import get_connection, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AI Business Operations Agent",
    description=(
        "Analyze business sales and prepare recommendations "
        "for human approval."
    ),
    version="1.0.0",
    lifespan=lifespan,
)



@app.get("/")
def home():
    return {
        "project": "AI Business Operations Agent",
        "status": "running",
        "ai_model": "llama3.2:3b",
        "api_docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/analysis/run")
def run_analysis(
    current_month: str = Query(
        default="2026-09",
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
    ),
    previous_month: str = Query(
        default="2026-08",
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
    ),
):
    if current_month <= previous_month:
        raise HTTPException(
            status_code=400,
            detail="Current month must be later than previous month.",
        )

    try:
        return run_business_agent(
            current_month=current_month,
            previous_month=previous_month,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Analysis failed. Check the application terminal logs.",
        ) from exc


@app.get("/drafts")
def list_drafts(status: str | None = Query(default=None)):
    allowed_statuses = {"pending", "approved", "rejected"}

    if status is not None and status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Status must be pending, approved, or rejected.",
        )

    with get_connection(read_only=True) as conn:
        if status:
            rows = conn.execute(
                """
                SELECT id, product_name, recommendation,
                       rationale, status, created_at
                FROM action_drafts
                WHERE status = ?
                ORDER BY id DESC
                """,
                (status,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, product_name, recommendation,
                       rationale, status, created_at
                FROM action_drafts
                ORDER BY id DESC
                """
            ).fetchall()

    return {"drafts": [dict(row) for row in rows]}


class DraftDecision(BaseModel):
    decision: str = Field(pattern=r"^(approved|rejected)$")


@app.patch("/drafts/{draft_id}/decision")
def decide_draft(draft_id: int, body: DraftDecision):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE action_drafts
            SET status = ?
            WHERE id = ? AND status = 'pending'
            """,
            (body.decision, draft_id),
        )

        if cursor.rowcount == 0:
            exists = conn.execute(
                "SELECT id FROM action_drafts WHERE id = ?",
                (draft_id,),
            ).fetchone()

            if exists is None:
                raise HTTPException(
                    status_code=404,
                    detail="Draft not found.",
                )

            raise HTTPException(
                status_code=409,
                detail="This draft has already been reviewed.",
            )

        conn.commit()

    return {
        "draft_id": draft_id,
        "status": body.decision,
        "message": "Draft decision saved. No external action was executed.",
    }
