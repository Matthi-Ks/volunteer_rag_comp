import os
import sqlite3
import uuid

from models.evaluation_result import EvaluationResult
from models.pipeline_summary import PipelineSummary
from models.query import QueryOptions
from util.config_loader import load_config

config = load_config()

DB_FILE_NAME="evaluation.db"

class EvaluationStore:
    def __init__(self):
        self.path = config["paths"]["sqlite"]
        self._init_db()


    def _init_db(self):
        os.makedirs(self.path, exist_ok=True)
        with self._get_connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS evaluation_results (
                id TEXT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                pipeline_type TEXT NOT NULL,
                information_tier TEXT NOT NULL,
                use_metadata_filter BOOLEAN NOT NULL,
                use_esco_skills BOOLEAN NOT NULL,
                faithfulness REAL,
                answer_relevancy REAL,
                context_precision REAL,
                context_recall REAL,
                token_count INTEGER
            );
            """)

            # Index for fast grouping during benchmark calculations
            conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_pipeline_config 
            ON evaluation_results (pipeline_type, information_tier, use_metadata_filter, use_esco_skills);
            """)
            conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path+"/"+DB_FILE_NAME)
        conn.row_factory = sqlite3.Row
        return conn

    def save_evaluation_result(self, result: EvaluationResult, query_options: QueryOptions):
        record_id = str(uuid.uuid4())
        with self._get_connection() as conn:
            conn.execute("""
            INSERT INTO evaluation_results (
                id, pipeline_type, information_tier, use_metadata_filter, 
                use_esco_skills, faithfulness, answer_relevancy, 
                context_precision, context_recall, token_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record_id,
                query_options.pipeline,
                query_options.informationTier,
                query_options.useMetadataFilter,
                query_options.useESCOSkills,
                result.faithfulness,
                result.answer_relevance,
                result.context_precision,
                result.context_recall,
                result.token_count
            ))
            conn.commit()
        return record_id

    def get_pipeline_averages(self) -> list[PipelineSummary]:
        query = """
        SELECT 
            pipeline_type,
            information_tier,
            use_metadata_filter,
            use_esco_skills,
            COUNT(*) as total_runs,
            ROUND(AVG(faithfulness), 4) as avg_faithfulness,
            ROUND(AVG(answer_relevancy), 4) as avg_answer_relevancy,
            ROUND(AVG(context_precision), 4) as avg_context_precision,
            ROUND(AVG(context_recall), 4) as avg_context_recall,
            SUM(token_count) as sum_token_count
        FROM evaluation_results
        GROUP BY 
            pipeline_type, 
            information_tier, 
            use_metadata_filter, 
            use_esco_skills
        ORDER BY pipeline_type, information_tier;
        """

        with self._get_connection() as conn:
            cursor = conn.cursor()
            rows = cursor.execute(query).fetchall()

            return [
                PipelineSummary(
                    pipeline_type=row["pipeline_type"],
                    information_tier=row["information_tier"],
                    use_metadata_filter=bool(row["use_metadata_filter"]),
                    use_esco_skills=bool(row["use_esco_skills"]),
                    total_runs=row["total_runs"],
                    avg_faithfulness=row["avg_faithfulness"],
                    avg_answer_relevancy=row["avg_answer_relevancy"],
                    avg_context_precision=row["avg_context_precision"],
                    avg_context_recall=row["avg_context_recall"],
                    sum_token_count=row["sum_token_count"]
                ) for row in rows
            ]

    def clear_evaluations(self):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM evaluation_results;")
            conn.commit()