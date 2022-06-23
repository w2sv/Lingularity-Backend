from typing import Dict


def reversed(d: Dict) -> Dict:
    return dict(map(reversed, d.items()))  # type: ignore