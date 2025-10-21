import json, re
from typing import Any, Dict, List
from selectolax.parser import HTMLParser

def extract_jsonld(html: str) -> List[Dict[str, Any]]:
    tree = HTMLParser(html)
    blocks = []
    for node in tree.css('script[type="application/ld+json"]'):
        txt = node.text() or ""
        # Some sites chain multiple JSON objects; attempt robust parse
        candidates = _split_json_candidates(txt)
        for c in candidates:
            try:
                obj = json.loads(c)
                if isinstance(obj, dict):
                    blocks.append(obj)
                elif isinstance(obj, list):
                    blocks.extend([o for o in obj if isinstance(o, dict)])
            except Exception:
                continue
    return blocks

def _split_json_candidates(s: str) -> List[str]:
    # Try to recover multiple JSON objects glued together
    # naive bracket matching:
    res, depth, buf = [], 0, []
    for ch in s:
        buf.append(ch)
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                res.append("".join(buf))
                buf = []
    if buf and buf[0] == "{" and depth == 0:
        res.append("".join(buf))
    return res
