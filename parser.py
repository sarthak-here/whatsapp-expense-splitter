"""parser.py - WhatsApp chat parser (Android format)."""
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
]

def _parse_dt(date_str: str, time_str: str) -> Optional[datetime]:
    combined = f"{date_str.strip()} {time_str.strip()}"
    for fmt in _DATE_FMTS:
        try:
            return datetime.strptime(combined, fmt)
        except ValueError:
            continue
    return None

_SYSTEM_KW = ("end-to-end encrypted", "created group", "left", "added you",
               "security code", "changed the subject", "null")

def _is_system(sender: str, content: str) -> bool:
    if not sender or sender.lower() in ("", "you"):
        return True
    return any(kw in content.lower() for kw in _SYSTEM_KW)

def parse_whatsapp_chat(content: str) -> List[ChatMessage]:
    """Parse Android WhatsApp export into ChatMessage list."""
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    pattern = re.compile(
        r"(\d{1,2}/\d{1,2}/\d{2,4}),\s+"
        r"(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AaPp][Mm])?)\s*[-\u2013]\s*"
        r"([^:]+?):\s+(.*?)(?=\d{1,2}/\d{1,2}/\d{2,4}|$)",
        re.DOTALL,
    )
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
    """Return unique sender names."""
    return {m.sender for m in messages if m.sender}
