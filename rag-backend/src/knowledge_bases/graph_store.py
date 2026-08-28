import os

from neo4j import GraphDatabase

from models.activity import Activity
from models.enums import InformationTier
from models.query import QueryOptions, Query
from models.retrieval_result import RetrievalResult
from util.config_loader import load_config
from util.llm_factory import LLMFactory

config = load_config()

class GraphStore:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            config["neo4j"]["uri"],
            auth=(config["neo4j"]["user"], os.getenv(config["neo4j"]["password_env"]))
        )
        self.embedding_fn = LLMFactory.get_embedding_fn()

    def close(self):
        self.driver.close()

    def setup_db_indexes(self):
        constraints = [
            "CREATE CONSTRAINT activity_id IF NOT EXISTS FOR (a:Activity) REQUIRE a.id IS UNIQUE;",
            "CREATE CONSTRAINT skill_name IF NOT EXISTS FOR (s:SoftSkill) REQUIRE s.name IS UNIQUE;",
            "CREATE CONSTRAINT region_name IF NOT EXISTS FOR (r:Region) REQUIRE r.name IS UNIQUE;",
            "CREATE CONSTRAINT timeframe_name IF NOT EXISTS FOR (t:Timeframe) REQUIRE t.name IS UNIQUE;",
        ]

        vector_indices = [
            """
            CREATE VECTOR INDEX `index_title_only` IF NOT EXISTS
            FOR (a:Activity) ON (a.embedding_title_only)
            OPTIONS {indexConfig: {`vector.dimensions`: 1024, `vector.similarity_function`: 'cosine'}};
            """,
            """
            CREATE VECTOR INDEX `index_title_desc` IF NOT EXISTS
            FOR (a:Activity) ON (a.embedding_title_desc)
            OPTIONS {indexConfig: {`vector.dimensions`: 1024, `vector.similarity_function`: 'cosine'}};
            """
        ]

        with self.driver.session() as session:
            for query in (constraints + vector_indices):
                session.run(query)

    def indexing(self, data: list[Activity]):
        batch_data = self._prepare_batch_data(data)

        cypher_query = """
            UNWIND $batch AS row

            // 1. Create central Activity node with clean text + two embeddings
            MERGE (a:Activity {id: row.id})
            SET a.title_only = row.title_only,
                a.title_desc = row.title_desc,
                a.embedding_title_only = row.emb_title_only,
                a.embedding_title_desc = row.emb_title_desc

            // 2. Connect to Region node
            WITH a, row WHERE row.region IS NOT NULL
            MERGE (r:Region {name: row.region})
            MERGE (a)-[:LOCATED_IN]->(r)

            // 3. Connect to Timeframe node
            WITH a, row WHERE row.timeframe IS NOT NULL
            MERGE (t:Timeframe {name: row.timeframe})
            MERGE (a)-[:HAS_TIMEFRAME]->(t)

            // 4. Connect to SoftSkill nodes
            WITH a, row
            UNWIND row.soft_skills AS skill_name
            MERGE (s:SoftSkill {name: skill_name})
            MERGE (a)-[:REQUIRES_SKILL]->(s)
            """

        with self.driver.session() as session:
            session.run(cypher_query, batch=batch_data)

    def _prepare_batch_data(self, items: list[Activity]):
        titles = [item.text_variations[InformationTier.TITLE_ONLY] for item in items]
        title_descs = [item.text_variations[InformationTier.TITLE_DESC] for item in items]

        title_embeddings = self.embedding_fn(titles)
        title_desc_embeddings = self.embedding_fn(title_descs)

        batch_data = []
        for idx, item in enumerate(items):
            batch_data.append({
                "id": item.id,
                "title_only": titles[idx],
                "title_desc": title_descs[idx],
                "emb_title_only": title_embeddings[idx],
                "emb_title_desc": title_desc_embeddings[idx],
                "soft_skills": item.soft_skills or [],
                "region": item.metadata.region,
                "timeframe": item.metadata.timeFrame
            })

        return batch_data

    def query_graph(self, query: Query, top_k: int = 5) -> list[RetrievalResult]:
        use_desc = query.options.informationTier in (
            InformationTier.TITLE_DESC,
            InformationTier.MaT_TITLE_DESC
        )
        index_name = "index_title_desc" if use_desc else "index_title_only"

        include_mat = query.options.useMaT
        include_skills = query.options.useESCOSkills

        neo4j_results = []

        for variant, query_text in query.text_variants.items():
            query_vector = self.embedding_fn(query_text)

            cypher = """
                CALL db.index.vector.queryNodes($index_name, $top_k, $query_vector)
                YIELD node AS a, score

                // Graph Traversal 1: Metadata (Region + Timeframe)
                OPTIONAL MATCH (a)-[:LOCATED_IN]->(r:Region) WHERE $include_mat = true
                OPTIONAL MATCH (a)-[:HAS_TIMEFRAME]->(t:Timeframe) WHERE $include_mat = true

                // Graph Traversal 2: Soft Skills
                OPTIONAL MATCH (a)-[:REQUIRES_SKILL]->(s:SoftSkill) WHERE $include_skills = true

                RETURN 
                    a.id AS id,
                    a.title_only AS title_only,
                    a.title_desc AS title_desc,
                    r.name AS region,
                    t.name AS timeframe,
                    collect(DISTINCT s.name) AS skills,
                    score
                ORDER BY score DESC
                """

            with self.driver.session() as session:
                result = session.run(
                    cypher,
                    index_name=index_name,
                    top_k=top_k,
                    query_vector=query_vector,
                    include_mat=include_mat,
                    include_skills=include_skills
                )

                variation_res = []
                for rec in result:
                    base_text = rec["title_desc"] if use_desc else rec["title_only"]

                    if include_mat and (rec["region"] or rec["timeframe"]):
                        doc_text = f"Metadata: [Region: {rec['region'] or 'N/A'}] [Timeframe: {rec['timeframe'] or 'N/A'}]\n{base_text}"
                    else:
                        doc_text = base_text

                    variation_res.append((
                        rec["id"],
                        str(doc_text),
                        rec["score"],
                        rec["skills"] if include_skills else []
                    ))

                neo4j_results.append(variation_res)

        return RetrievalResult.from_neo4j_results(neo4j_results, list(query.text_variants.keys()))

