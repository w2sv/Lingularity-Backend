from typing import Dict


def reversed(d: Dict) -> Dict:
    return {v: k for k, v in d.items()}