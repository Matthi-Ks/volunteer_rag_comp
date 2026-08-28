from typing import Dict, Tuple
from models.enums import RagPipeline, InformationTier
from models.query import QueryOptions
from pipelines.fusion_rag.fusion_rag import FusionRag
from pipelines.graph_rag.graph_rag import GraphRag
from pipelines.hybrid_rag.hybrid_rag import HybridRag
from knowledge_bases.vector_store import VectorStore
from knowledge_bases.graph_store import GraphStore
from pipelines.rag_base import RagBase


class PipelineFactory:
    _vector_store: VectorStore | None = None
    _graph_store: GraphStore | None = None
    _pipeline_cache: Dict[Tuple, RagBase] = {}

    @classmethod
    def _get_stores(cls) -> Tuple[VectorStore, GraphStore]:
        """Lazy-loads and reuses singleton vector and graph store instances."""
        if cls._vector_store is None:
            cls._vector_store = VectorStore()
        if cls._graph_store is None:
            cls._graph_store = GraphStore()
        return cls._vector_store, cls._graph_store

    @classmethod
    def create_pipeline(cls, options: QueryOptions) -> RagBase:
        """
        Instantiates or retrieves a cached pipeline tailored to the provided QueryOptions.
        Caching pipelines avoids re-initializing embeddings/models unnecessarily.
        """
        cache_key = (
            options.pipeline,
            options.informationTier,
            options.useMaT,
            options.useESCOSkills
        )

        if cache_key in cls._pipeline_cache:
            return cls._pipeline_cache[cache_key]

        vector_store, graph_store = cls._get_stores()

        # Build pipeline instance based on pipeline enum
        if options.pipeline == RagPipeline.HYBRID:
            pipeline = HybridRag(
                vectorStore=vector_store,
                graphStore=graph_store,
            )
        elif options.pipeline == RagPipeline.GRAPH:
            pipeline = GraphRag(
                vectorStore=vector_store,
                graphStore=graph_store,
            )
        elif options.pipeline == RagPipeline.FUSION:
            pipeline = FusionRag(
                vectorStore=vector_store,
                graphStore=graph_store,
            )
        else:
            raise ValueError(f"Unsupported pipeline type: {options.pipeline}")

        cls._pipeline_cache[cache_key] = pipeline
        return pipeline

    @classmethod
    def clear_cache(cls):
        """Clears cached pipeline instances if memory cleanup is required."""
        cls._pipeline_cache.clear()