"""Extract structured attributes from raw persona text using a local Ollama LLM."""

import json
import time
from pathlib import Path

import ollama

from pipeline.common.paths import EXTRACTION_BATCH_SIZE, PERSONAS_STRUCTURED_PATH
from pipeline.p01_persona_extraction.schema import PersonaProfile, schema_json

SYSTEM_PROMPT = """\
Dado el siguiente perfil de persona, extrae los atributos en formato JSON.
Responde ÚNICAMENTE con el JSON, sin texto adicional.
Si no puedes inferir un atributo con certeza razonable, usa null.
"""

EXTRACTION_TEMPLATE = """\
Perfil: {raw_text}

Esquema esperado: {schema}
"""


def _build_prompt(raw_text: str) -> str:
    return EXTRACTION_TEMPLATE.format(raw_text=raw_text, schema=json.dumps(schema_json()))


def extract_attributes(
    persona_id: str,
    raw_text: str,
    model: str = "llama3.2",
    max_retries: int = 3,
) -> PersonaProfile:
    prompt = _build_prompt(raw_text)
    last_error: Exception | None = None

    for attempt in range(max_retries):
        try:
            response = ollama.chat(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            payload = json.loads(response["message"]["content"])
            return PersonaProfile(persona_id=persona_id, raw_text=raw_text, **payload)
        except (json.JSONDecodeError, KeyError, ollama.ResponseError) as exc:
            last_error = exc
            time.sleep(2**attempt)

    raise RuntimeError(f"Failed to extract attributes for {persona_id}") from last_error


def extract_batch(
    records: list[dict],
    output_path: Path = PERSONAS_STRUCTURED_PATH,
    model: str = "llama3.2",
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("a", encoding="utf-8") as f:
        for i in range(0, len(records), EXTRACTION_BATCH_SIZE):
            batch = records[i : i + EXTRACTION_BATCH_SIZE]
            for record in batch:
                profile = extract_attributes(
                    persona_id=str(record["persona_id"]),
                    raw_text=record["raw_text"],
                    model=model,
                )
                f.write(profile.model_dump_json() + "\n")

    return output_path
