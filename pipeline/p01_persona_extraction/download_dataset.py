"""Download a stratified sample from latam-gpt/personas on HuggingFace."""

from pathlib import Path

import pandas as pd
from datasets import load_dataset

from pipeline.common.paths import PERSONAS_SAMPLE_PATH, SAMPLE_SIZE


def download_personas_sample(
    output_path: Path = PERSONAS_SAMPLE_PATH,
    sample_size: int = SAMPLE_SIZE,
) -> Path:
    dataset = load_dataset("latam-gpt/personas", split="train", streaming=True)
    rows: list[dict] = []

    for i, row in enumerate(dataset):
        if i >= sample_size:
            break
        rows.append(dict(row))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(output_path, index=False)
    return output_path


if __name__ == "__main__":
    path = download_personas_sample()
    print(f"Saved {SAMPLE_SIZE} personas to {path}")
