import os
import re
import time
import uuid
from typing import Final

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI
from pydantic import BaseModel, StrictStr

DEFAULT_FRONTEND_ORIGIN: Final[str] = "http://localhost:5173"
SELF_HARM_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(suicide|kill myself|end my life|self[- ]harm|hurt myself|want to die|don't want to live)\b",
    re.IGNORECASE,
)
SYSTEM_MESSAGE: Final[str] = (
    "You are a supportive affirmation assistant. Write a short affirmation of 2 to 4 sentences. "
    "Use warm, plain language and avoid clinical tone. "
    "Do not provide medical advice, legal advice, diagnoses, or crisis counseling."
)

app = FastAPI()

frontend_origin_raw = os.getenv("FRONTEND_ORIGIN", DEFAULT_FRONTEND_ORIGIN).strip()
allowed_origins = [
    origin.strip()
    for origin in frontend_origin_raw.split(",")
    if origin.strip()
]
if not allowed_origins:
    allowed_origins = [DEFAULT_FRONTEND_ORIGIN]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AffirmationRequest(BaseModel):
    name: StrictStr
    feeling: StrictStr


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(_, __):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Please send both 'name' and 'feeling' as non-empty text."
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}


def contains_self_harm_intent(text: str) -> bool:
    return bool(SELF_HARM_PATTERN.search(text))


def log_affirmation_event(
    status: str,
    request_id: str,
    started: float,
    model: str,
    name: str,
    feeling: str,
) -> None:
    duration_ms = int((time.perf_counter() - started) * 1000)
    print(
        f"[affirmation] {status} request_id={request_id} "
        f"duration_ms={duration_ms} model={model} "
        f"name_len={len(name)} feeling_len={len(feeling)}"
    )


@app.post("/api/affirmation")
def create_affirmation(payload: AffirmationRequest):
    name = payload.name.strip()
    feeling = payload.feeling.strip()

    if not name or not feeling:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Please send both 'name' and 'feeling' as non-empty text."
            },
        )

    request_id = uuid.uuid4().hex[:8]
    started = time.perf_counter()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if contains_self_harm_intent(f"{name} {feeling}"):
        log_affirmation_event("ok", request_id, started, model, name, feeling)
        return {
            "affirmation": (
                "I'm really glad you reached out. You matter, and you deserve support right now. "
                "Please contact a trusted person or a mental health professional today. "
                "If you feel in immediate danger, please contact your local emergency number right now "
                "(for example, 112 in many countries) or go to the nearest emergency department."

            )
        }

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        log_affirmation_event("fail", request_id, started, model, name, feeling)
        return JSONResponse(
            status_code=500,
            content={
                "error": "The affirmation service is not configured yet. Please try again soon."
            },
        )

    client = OpenAI(api_key=api_key, timeout=20.0)
    user_message = (
        f"Name: {name}\n"
        f"Current feeling: {feeling}\n"
        "Write a personalized affirmation addressed to this person."
    )

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": user_message},
            ],
            temperature=0.8,
            max_tokens=180,
        )
    except APITimeoutError:
        log_affirmation_event("fail", request_id, started, model, name, feeling)
        return JSONResponse(
            status_code=504,
            content={
                "error": "The affirmation service took too long to respond. Please try again."
            },
        )
    except (APIConnectionError, APIStatusError):
        log_affirmation_event("fail", request_id, started, model, name, feeling)
        return JSONResponse(
            status_code=502,
            content={
                "error": "The affirmation service is temporarily unavailable. Please try again shortly."
            },
        )
    except Exception:
        log_affirmation_event("fail", request_id, started, model, name, feeling)
        return JSONResponse(
            status_code=502,
            content={
                "error": "The affirmation service is temporarily unavailable. Please try again shortly."
            },
        )

    message = (completion.choices[0].message.content or "").strip()
    if not message:
        log_affirmation_event("fail", request_id, started, model, name, feeling)
        return JSONResponse(
            status_code=502,
            content={
                "error": "I couldn't generate an affirmation right now. Please try again shortly."
            },
        )

    log_affirmation_event("ok", request_id, started, model, name, feeling)
    return {"affirmation": message}
