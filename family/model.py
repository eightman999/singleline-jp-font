"""Unstroked, auditable glyph source model on the project's 24-unit grid."""
from dataclasses import dataclass, field


@dataclass
class Glyph:
    text: str
    paths: list
    advance: int = 1000
    width_factor: float = 1.0
    filled: bool = False
    source: str = "project-authored"
    status: str = "design-draft"
    category: str = "symbol"
    notes: dict = field(default_factory=dict)


def glyph_name(text):
    return "u" + "_".join(f"{ord(c):04X}" for c in text)
