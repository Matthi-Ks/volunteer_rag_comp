import queue
import sys
import threading
import types

fake_vertex_module = types.ModuleType("langchain_community.chat_models.vertexai")

class ChatVertexAI:
    pass

fake_vertex_module.ChatVertexAI = ChatVertexAI
sys.modules["langchain_community.chat_models.vertexai"] = fake_vertex_module


import asyncio
import itertools
import json
import logging
import time
from pathlib import Path
from typing import List

from evaluation.eval import evaluate
from knowledge_bases.evaluation_store import EvaluationStore
from models.activity import Region, StartTimeframe, ActivityMetadata
from models.enums import QuestionVariant, InformationTier, RagPipeline
from models.profile import Profile
from models.query import Query, QueryOptions

from pipelines.pipeline_factory import PipelineFactory

eval_store = EvaluationStore()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ConcurrentBenchmark")

# 1. Define Concurrency Controls
MAX_CONCURRENT_TASKS = 5
API_SEMAPHORE = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

result_queue = queue.Queue()

def db_writer_worker(eval_store, result_queue):
    """Dedicated single worker thread for database writes."""
    while True:
        item = result_queue.get()
        if item is None:  # Sentinel signal to stop
            break
        res, options = item
        try:
            eval_store.save_evaluation_result(res, options)
            logger.info("Saved entry to DB")
        except Exception as e:
            print(f"Error saving result to DB: {e}")
        finally:
            result_queue.task_done()

def generate_query_options() -> List[QueryOptions]:
    """Generates the Cartesian product of all configuration option combinations (24 total)."""
    options_list = []

    # 4 tiers x 3 pipelines x 2 esco flags = 24 combinations
    for tier, pipeline, use_esco in itertools.product(
            InformationTier,
            RagPipeline,
            [True, False]
    ):
        # MAT_... is only used with use_Mat = true
        use_mat = tier.name.lower().startswith("mat_")

        options_list.append(
            QueryOptions(
                informationTier=tier,
                pipeline=pipeline,
                useMaT=use_mat,
                useESCOSkills=use_esco
            )
        )
    return options_list


def augment_queries(raw_data: list, profiles: List[Profile]) -> List[Query]:
    """
    Expands raw template queries across:
    1. Region x StartTimeframe combinations (12 variants)
    2. QueryOptions combinations (24 option sets)
    3. User Profiles
    """
    expanded_queries: List[Query] = []
    region_timeframe_combos = list(itertools.product(Region, StartTimeframe))
    options_combos = generate_query_options()

    for item in raw_data:
        raw_id = item.get("id") or item.get("query_id")
        normal = item.get("text_variants", {}).get("normal", "")
        abstract = item.get("text_variants", {}).get("abstract", "")
        detailed = item.get("text_variants", {}).get("detailed", "")

        for region, timeframe in region_timeframe_combos:
            # Interpolate text placeholders
            interpolated_variants = {
                QuestionVariant.NORMAL: normal.replace("[location]", region).replace("[timeframe]", timeframe),
                QuestionVariant.ABSTRACT: abstract.replace("[location]", region).replace("[timeframe]", timeframe),
                QuestionVariant.DETAILED: detailed.replace("[location]", region).replace("[timeframe]", timeframe),
            }

            for options in options_combos:
                for profile in profiles:
                    expanded_queries.append(
                        Query(
                            query_id=raw_id,
                            profile=profile,
                            filter_values=ActivityMetadata(
                                region=Region(region),
                                timeFrame=StartTimeframe(timeframe)
                            ),
                            options=options,
                            text_variants=interpolated_variants
                        )
                    )

    return expanded_queries


def get_profiles():
    json_file = Path("resources/datasets/profiles.json")

    if not json_file.exists():
        raise FileNotFoundError(f"Could not find query file at {json_file.resolve()}")

    with open(json_file, "r", encoding="utf-8") as f:
        profiles = json.load(f)

    return [profiles[1], profiles[2]]


def get_all_queries():
    json_file = Path("resources/datasets/queries.json")

    if not json_file.exists():
        raise FileNotFoundError(f"Could not find query file at {json_file.resolve()}")

    with open(json_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    return augment_queries(raw_data, get_profiles())


async def run_single_query_evaluation(query: Query):
    async with API_SEMAPHORE:
        try:
            pipeline = await asyncio.to_thread(PipelineFactory.create_pipeline, query.options)
        except Exception as e:
            logger.error(f"Failed to create pipeline for QID [{query.query_id}]: {e}", exc_info=True)
            return

        # Exponential backoff retry loop for API rate limits
        max_retries = 3
        backoff_delay = 2.0

        for attempt in range(max_retries):
            try:
                # Execute your custom evaluate function
                results = await evaluate(query=query, pipeline=pipeline)
                logger.info("computed result")
                # Save results immediately to SQLite
                for res in results:
                    result_queue.put((res, query.options))

                break

            except Exception as e:
                err_msg = str(e).lower()
                # Catch rate limits (HTTP 429) or token limits
                if "429" in err_msg or "rate limit" in err_msg:
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Rate limit hit for Query [{query.query_id}]. Retrying in {backoff_delay}s... (Attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(backoff_delay)
                        backoff_delay *= 2  # Exponential backoff
                    else:
                        logger.error(f"Max retries reached for Query [{query.query_id}]: {e}")
                else:
                    logger.error(f"Execution error on Query [{query.query_id}]: {e}", exc_info=True)
                    break


async def run_full_benchmark_concurrent():
    logger.info("Loading and expanding query matrix...")
    queries = get_all_queries()
    total_runs = len(queries)

    logger.info(f"Launching {total_runs} evaluation runs (Max Concurrency: {MAX_CONCURRENT_TASKS})...")

    start_bench_time = time.perf_counter()

    # Schedule all query runs bounded by API_SEMAPHORE
    tasks = [run_single_query_evaluation(q) for q in queries]
    await asyncio.gather(*tasks, return_exceptions=True)

    total_duration = time.perf_counter() - start_bench_time
    logger.info(f"Benchmark complete! Processed {total_runs} evaluations in {total_duration:.2f} seconds.")


if __name__ == "__main__":
    #eval_store.clear_evaluations()
    writer_thread = threading.Thread(
        target=db_writer_worker,
        args=(eval_store, result_queue),
        daemon=True
    )
    writer_thread.start()

    try:
        PipelineFactory._get_stores()
        asyncio.run(run_full_benchmark_concurrent())
    finally:
        result_queue.join()
        result_queue.put(None)
        writer_thread.join()
        logger.info("All benchmark results saved successfully.")