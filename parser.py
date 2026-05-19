"""parser.py - WhatsApp chat parser. Supports Android + iOS export formats."""
import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Set


@dataclass
class ChatMessage:
    timestamp: Optional[datetime]
    sender: str
    content: str


_DATE_FMTS = [
    "%d/%m/%Y %H:%M", "%d/%m/%y %H:%M",
    "%d/%m/%Y %I:%M %p", "%d/%m/%y %I:%M %p",
    "%d/%m/%Y %H:%M:%S", "%d/%m/%y %H:%M:%S",
    "%d/%m/%Y %I:%M:%S %p", "%d/%m/%y %I:%M:%S %p",
    "%m/%d/%Y %I:%M %p", "%m/%d/%y %I:%M %p",
]

def _parse_dt(date_str: str, time_str: str) -> Optional[datetime]:
    combined = f"{date_str.strip()} {time_str.strip()}"
    for fmt in _DATE_FMTS:
        try:
            return datetime.strptime(combined, fmt)
        except ValueError:
            continue
    return None

def _detect_format(text: str) -> str:
    """Detect iOS vs Android export format."""
    if re.search(r'[\[\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}', text[:800]):
        return "ios"
    return "android"

_SYSTEM_KW = ("end-to-end encrypted", "created group", "left", "added you",
               "security code", "changed the subject", "null", "you were added")

def _is_system(sender: str, content: str) -> bool:
    if not sender or sender.lower() in ("", "you"):
        return True
    return any(kw in content.lower() for kw in _SYSTEM_KW)

def parse_whatsapp_chat(content: str) -> List[ChatMessage]:
    """Parse WhatsApp export (Android or iOS) into ChatMessage list."""
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    fmt = _detect_format(content)
    if fmt == "ios":
        pattern = re.compile(
            r"[\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*"
            r"(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AaPp][Mm])?)\]\s+"
            r"([^:]+?):\s+(.*?)(?=\[\d{1,2}/\d{1,2}/\d{2,4}|$)", re.DOTALL)
    else:
        pattern = re.compile(
            r"(\d{1,2}/\d{1,2}/\d{2,4}),\s+"
            r"(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AaPp][Mm])?)\s*[-\u2013]\s*"
            r"([^:]+?):\s+(.*?)(?=\d{1,2}/\d{1,2}/\d{2,4}|$)", re.DOTALL)
    messages = []
    for m in pattern.finditer(content):
        d, t, sender, body = m.groups()
        sender, body = sender.strip(), body.strip()
        if _is_system(sender, body):
            continue
        if body in ("<Media omitted>", "This message was deleted", ""):
            continue
        messages.append(ChatMessage(timestamp=_parse_dt(d, t), sender=sender, content=body))
    return messages

def extract_members(messages: List[ChatMessage]) -> Set[str]:
    return {m.sender for m in messages if m.sender}

def read_chat_file(filepath: str) -> str:
    """Read WhatsApp export with encoding fallback."""
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            with open(filepath, "r", encoding=enc, errors="replace") as f:
                return f.read()
        except OSError:
            raise
    raise UnicodeDecodeError("Could not decode file")

def get_date_range(messages: List[ChatMessage]):
    """Return (min_date, max_date) from parsed messages."""
    dated = [m.timestamp for m in messages if m.timestamp]
    if not dated:
        return None, None
    return min(dated), max(dated)

def messages_by_sender(messages: List[ChatMessage]) -> dict:
    """Group messages by sender: {name: [ChatMessage, ...]}."""
    result: dict = {}
    for msg in messages:
        result.setdefault(msg.sender, []).append(msg)
    return result
