from pathlib import Path  # noqa: I001


ROOT = Path(__file__).resolve().parents[1]


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_factory_protocol_has_all_semantic_layers_and_invariants() -> None:
    protocol = text("docs/architecture/FACTORY_PROTOCOL_ARCHITECTURE_CONSTITUTION.md")
    for required in (
        "L0",
        "L1",
        "L2",
        "L3",
        "L4",
        "Factory Packet",
        "FFS",
        "Zoning",
        "Cognitive Processing",
        "Artifact Contract",
        "Publication Resolution",
    ):
        assert required in protocol
    assert "FFS SHALL NOT proxy payload data" in protocol
    assert "Cognitive Processing SHALL NOT be placed inside the AI Kernel" in protocol


def test_canonical_diagram_set_covers_factory_protocol_and_separation() -> None:
    index = text("docs/architecture/diagrams/README.md")
    factory = text(
        "docs/architecture/diagrams/13-factory-protocol/13_FACTORY_PROTOCOL.md"
    )
    kernel = text("docs/architecture/diagrams/07-ai-kernel/07_AI_KERNEL.md")
    assert "13 Factory Protocol" in index
    assert "FactoryIP is the complete L0-L4 semantic stack" in factory
    assert "not Cognitive Processing or inferred Node" in factory
    assert "separate pre-admission capability" in kernel
