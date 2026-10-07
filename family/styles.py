"""Design-space definitions. Italian is upright reverse contrast, not italic."""
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Style:
    key: str
    label: str
    vertical: float
    horizontal: float
    serif: float = 0.0
    slant: float = 0.0
    scale: float = 1.0
    rise: float = 0.0
    weight: int = 400
    italic: bool = False


STYLES = {
    "singleline": Style("singleline", "Singleline", 20, 20, weight=300),
    "pc98-mincho": Style("pc98-mincho", "PC98 Mincho Inspired", 42, 15, serif=0.80),
    "gothic": Style("gothic", "Gothic", 36, 36),
    "italian": Style("italian", "Italian Reverse Contrast", 19, 58, serif=1.0),
    "serif": Style("serif", "Serif", 45, 20, serif=1.0),
    "italic": Style("italic", "Italic", 37, 19, serif=0.8, slant=-12, italic=True),
    "subscript": Style("subscript", "Subscript", 30, 30, scale=0.65, rise=-160),
    "superscript": Style("superscript", "Superscript", 30, 30, scale=0.65, rise=340),
}


def variable_style(base, weight=400, slant=0):
    """Variable weight changes both stem dimensions; negative slnt leans right."""
    factor = {200: 0.6, 400: 1.0, 700: 1.6}.get(weight)
    if factor is None:
        factor = 1 + (weight-400) * (0.002 if weight >= 400 else 0.002)
    return replace(base, vertical=base.vertical*factor,
                   horizontal=base.horizontal*factor, slant=slant, weight=weight)
