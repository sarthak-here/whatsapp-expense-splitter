"""expense_extractor.py - Extract expenses from chat (English patterns)."""
import re
from dataclasses import dataclass, field
from typing import List, Optional, Set
from parser import ChatMessage

_AMOUNT_RE = re.compile(
    r"(?:₹\s*|rs\.?\s*|inr\s*)?(\d{1,6}(?:[,_]\d{3})*(?:\.\d{1,2})?)"
    r"(?:\s*(?:rs|\/\-|rupees?))?", re.IGNORECASE)

def _extract_amount(text: str) -> Optional[float]:
    for m in _AMOUNT_RE.finditer(text):
        raw = m.group(1).replace(",", "").replace("_", "")
        try:
            val = float(raw)
            if val >= 1:
                return val
        except ValueError:
            continue
    return None

_PATTERNS = [
    (re.compile(r"\b(i|me)\b.{0,15}paid\b", re.I), None, "paid"),
    (re.compile(r"\b(\w+)\b.{0,10}(?:paid|pay kiya|diya|de diya|bheja)\b", re.I), 1, "third"),
    (re.compile(r"\bsplit(?:ting)?\b.{0,30}(\d[\d,\.]*)", re.I), None, "split"),
    (re.compile(r"\b(?:i(?:'ll)?|me)\b.{0,10}cover(?:ed|ing)?\b", re.I), None, "covered"),
    (re.compile(
        r"\b(?:dinner|lunch|breakfast|hotel|petrol|cab|auto|ticket|bill|"
        r"groceries|food|movie|zomato|swiggy|uber|ola|snacks|chai)\b", re.I),
     None, "context"),
]

_BLACKLIST = re.compile(
    r"\b(will pay|will split|who paid|should i|let me know|remind|later|"
    r"aayega|dega|karega|baad mein|owe me)\b", re.I)

@dataclass
class Expense:
    payer: str
    amount: float
    description: str
    participants: List[str] = field(default_factory=list)
    timestamp: Optional[object] = None

    def per_head(self) -> float:
        n = len(self.participants)
        return round(self.amount / n, 2) if n > 1 else self.amount

_NOUNS = re.compile(
    r"\b(dinner|lunch|breakfast|hotel|petrol|cab|auto|ticket|bill|groceries|"
    r"food|movie|zomato|swiggy|uber|ola|snacks|chai|booze|party|trip)\b", re.I)

def _describe(text: str) -> str:
    m = _NOUNS.search(text)
    if m:
        return m.group(1).capitalize()
    clean = re.sub(r"\s+", " ", text).strip()
    return clean[:40] + ("..." if len(clean) > 40 else "")

def _fuzzy(candidate: str, members: Set[str]) -> Optional[str]:
    c = candidate.lower()
    for member in members:
        if member.lower().startswith(c) or c.startswith(member.lower()):
            return member
    return None

def extract_expenses(messages: List[ChatMessage], members: Set[str]) -> List[Expense]:
    """Detect expenses from parsed chat messages."""
    expenses = []
    for msg in messages:
        text = msg.content
        if _BLACKLIST.search(text):
            continue
        amount = _extract_amount(text)
        if amount is None:
            continue
        for pattern, pg, label in _PATTERNS:
            m = pattern.search(text)
            if not m:
                continue
            if pg is None:
                payer = msg.sender
            else:
                try:
                    cand = m.group(pg).strip()
                    payer = msg.sender if cand.lower() in ("i","me") else (_fuzzy(cand, members) or msg.sender)
                except IndexError:
                    payer = msg.sender
            expenses.append(Expense(payer=payer, amount=amount,
                description=_describe(text), participants=list(members), timestamp=msg.timestamp))
            break
    return expenses
