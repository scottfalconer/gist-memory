from __future__ import annotations

"""Utility to collect basic metrics for available compression engines."""

import json
from pathlib import Path
from typing import Callable

import typer

from compact_memory.contrib import enable_all_experimental_engines
from compact_memory.engines.registry import (
    available_engines,
    get_compression_engine,
    register_compression_engine,
)
from compact_memory.validation.registry import get_validation_metric_class
from compact_memory import embedding_pipeline as ep
from compact_memory.model_utils import download_embedding_model

app = typer.Typer(help="Collect metrics for available compression engines.")


@app.command()
def main(output_file: str = "engine_metrics.json", use_mock: bool = False) -> None:
    """Run each engine on sample text and record metrics.

    If ``use_mock`` is True, the embedding pipeline uses a deterministic mock
    encoder. Otherwise the required models are downloaded if missing.
    """

    enable_all_experimental_engines()

    from compact_memory.engines import pipeline_engine

    register_compression_engine(
        pipeline_engine.PipelineEngine.id, pipeline_engine.PipelineEngine
    )

    if use_mock:
        enc = ep.MockEncoder()
        ep._load_model = lambda *a, **k: enc
    else:
        for model in ["all-MiniLM-L6-v2", "multi-qa-mpnet-base-dot-v1"]:
            try:  # pragma: no cover - network and disk dependent
                download_embedding_model(model)
            except Exception as exc:  # pragma: no cover - best effort
                print(f"warning: unable to download {model}: {exc}")

    engines = list(available_engines())

    text = Path("sample_data/moon_landing/full.txt").read_text()

    ratio_metric = get_validation_metric_class("compression_ratio")()
    embed_metric = get_validation_metric_class("embedding_similarity_multi")(
        model_names=["all-MiniLM-L6-v2", "multi-qa-mpnet-base-dot-v1"],
        max_tokens=8192,
    )

    results: dict[str, dict[str, float]] = {}

    for eng_id in engines:
        EngineCls = get_compression_engine(eng_id)
        if eng_id == "pipeline":
            from compact_memory.engines.first_last_engine import FirstLastEngine
            from compact_memory.engines.no_compression_engine import NoCompressionEngine

            engine = EngineCls([FirstLastEngine(), NoCompressionEngine()])
        else:
            engine = EngineCls()

        if eng_id == "none":
            # Disable truncation for the no-op engine so the metrics reflect
            # a true no-compression baseline.
            compressed, _ = engine.compress(text, llm_token_budget=None)
        else:
            result = engine.compress(text, llm_token_budget=100)
            if isinstance(result, tuple):
                compressed, _ = result
            else:
                compressed = result

        if hasattr(compressed, "text"):
            comp_text = compressed.text
        else:
            comp_text = compressed.get("content", str(compressed))
        ratio = ratio_metric.evaluate(original_text=text, compressed_text=comp_text)[
            "compression_ratio"
        ]
        embed_scores = embed_metric.evaluate(
            original_text=text, compressed_text=comp_text
        )
        results[eng_id] = {
            "compression_ratio": ratio,
            "embedding_similarity_multi": embed_scores,
        }

    Path(output_file).write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    app()
