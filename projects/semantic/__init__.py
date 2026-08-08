"""Provider-independent Semantic Layer contracts and services.

The layer ranks and returns candidates only.  It never makes business or
Runtime decisions.
"""

from .service import (
    SELECTION_STRATEGY,
    SemanticContext,
    SemanticSource,
    build_semantic_context,
)

__all__ = [
    "SELECTION_STRATEGY",
    "SemanticContext",
    "SemanticSource",
    "build_semantic_context",
]
