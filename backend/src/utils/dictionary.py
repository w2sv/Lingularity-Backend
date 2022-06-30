from typing import Dict


def items_reversed(d: Dict) -> Dict:
    return {v: k for k, v in d.items()}