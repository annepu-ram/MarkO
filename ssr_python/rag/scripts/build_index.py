"""Build the RAG index from source documents.

Usage:
    cd ssr_python
    python -m rag.scripts.build_index
"""
import sys
import os
import time

# Ensure ssr_python is on the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from rag.indexing.index_builder import IndexBuilder


def main():
    print("=" * 60)
    print("RAG Index Builder")
    print("=" * 60)

    builder = IndexBuilder()

    # Check staleness
    if not builder.is_stale():
        print("Index is up-to-date. Use --force to rebuild anyway.")
        if "--force" not in sys.argv:
            return

    start = time.time()
    result = builder.build()
    elapsed = time.time() - start

    print(f"\nDone in {elapsed:.1f}s")
    print(f"  Chunks: {result['chunk_count']}")
    print(f"  Hash:   {result['source_hash'][:16]}...")


if __name__ == "__main__":
    main()
