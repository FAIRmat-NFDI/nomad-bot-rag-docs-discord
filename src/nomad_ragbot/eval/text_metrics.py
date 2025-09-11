import re
from collections import Counter
_WS = re.compile(r"\s+")
_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
def normalize_text(s: str) -> str:
    if s is None: return ""
    s = s.lower()
    s = _PUNCT.sub(" ", s)
    s = _WS.sub(" ", s).strip()
    return s
def token_f1(pred: str, gold: str) -> float:
    p_tokens = normalize_text(pred).split()
    g_tokens = normalize_text(gold).split()
    if not p_tokens and not g_tokens: return 1.0
    if not p_tokens or not g_tokens: return 0.0
    p_counts = Counter(p_tokens)
    g_counts = Counter(g_tokens)
    overlap = sum((p_counts & g_counts).values())
    if overlap == 0: return 0.0
    precision = overlap / max(1, sum(p_counts.values()))
    recall = overlap / max(1, sum(g_counts.values()))
    if precision + recall == 0: return 0.0
    return 2 * precision * recall / (precision + recall)
def exact_match(pred: str, gold: str) -> float:
    return 1.0 if normalize_text(pred) == normalize_text(gold) else 0.0
def jaccard(pred: str, gold: str) -> float:
    p = set(normalize_text(pred).split())
    g = set(normalize_text(gold).split())
    if not p and not g: return 1.0
    if not p or not g: return 0.0
    inter = len(p & g)
    union = len(p | g)
    return inter / union if union else 0.0
def levenshtein_ratio(a: str, b: str) -> float:
    a = normalize_text(a); b = normalize_text(b)
    if a == b: return 1.0
    n, m = len(a), len(b)
    if n == 0 or m == 0: return 0.0
    dp = list(range(m + 1))
    for i in range(1, n + 1):
        prev = dp[0]; dp[0] = i
        for j in range(1, m + 1):
            tmp = dp[j]
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[j] = min(dp[j] + 1, dp[j - 1] + 1, prev + cost)
            prev = tmp
    dist = dp[m]; max_len = max(n, m)
    return 1.0 - dist / max_len
