"""routes/rag.py — RAG debug and management endpoints."""
import json
from flask import Blueprint, jsonify, request

rag_bp = Blueprint("rag", __name__, url_prefix="/api/rag")


@rag_bp.route("/status", methods=["GET"])
def status():
    """Check index status and staleness."""
    from rag.indexing.index_builder import IndexBuilder
    from rag.config import config

    builder = IndexBuilder()
    stale = builder.is_stale()
    meta_path = config.data_dir / "index_meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    return jsonify({"stale": stale, **meta})


@rag_bp.route("/rebuild-index", methods=["POST"])
def rebuild():
    """Rebuild the RAG index from source documents."""
    from rag.indexing.index_builder import IndexBuilder

    builder = IndexBuilder()
    result = builder.build()
    return jsonify(result)


@rag_bp.route("/search", methods=["POST"])
def debug_search():
    """Debug endpoint: test retrieval without generation."""
    from rag.retrieval.hybrid import HybridSearch
    from rag.agent.query_analyzer import QueryAnalyzer

    data = request.json
    if not data or "query" not in data:
        return jsonify({"error": "Missing 'query' in request body"}), 400

    search = HybridSearch()
    search.load()

    analyzer = QueryAnalyzer()
    intent = analyzer.analyze(data["query"])

    meta_filter = {}
    if intent.section_filter:
        meta_filter["section_type"] = intent.section_filter
    if intent.industry_filter:
        meta_filter["industry"] = intent.industry_filter
    if intent.style_filter:
        meta_filter["visual_style"] = intent.style_filter

    top_k = data.get("top_k", 5)
    results = search.search(data["query"], top_k=top_k, metadata_filter=meta_filter or None)

    return jsonify({
        "intent": {
            "action": intent.action,
            "section_filter": intent.section_filter,
            "industry_filter": intent.industry_filter,
            "style_filter": intent.style_filter,
            "component_filter": intent.component_filter,
            "sub_queries": intent.sub_queries,
        },
        "results": [
            {
                "id": r["id"],
                "source": r["source_file"],
                "doc_type": r["doc_type"],
                "metadata": r.get("metadata", {}),
                "preview": r["content"][:300],
                "token_count": r.get("token_count", 0),
            }
            for r in results
        ],
    })
