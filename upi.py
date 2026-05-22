\"\"\"upi.py - UPI deeplink and QR code generator. No API key needed.\"\"\"
import re
from urllib.parse import quote
from typing import Optional


def build_upi_link(vpa: str, payee_name: str, amount: float, note: str = "Group expense") -> str:
    \"\"\"Build a upi:// deeplink (opens GPay, PhonePe, Paytm, BHIM etc.).\"\"\"
    return (f"upi://pay?pa={vpa}&pn={quote(payee_name)}"
            f"&am={amount:.2f}&cu=INR&tn={quote(note)}")


def qr_code_url(upi_link: str, size: int = 200) -> str:
    \"\"\"Generate QR code image URL (free api.qrserver.com, no API key).\"\"\"
    return f"https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&data={quote(upi_link, safe='')}"


def format_inr(amount: float) -> str:
    \"\"\"Format float as Indian Rupee string with Indian comma style.\"\"\"
    amount = round(amount, 2)
    int_part = int(amount)
    dec = f"{amount:.2f}".split(".")[1]
    s = str(int_part)
    if len(s) <= 3:
        return f"₹{s}.{dec}"
    formatted = s[-3:]
    s = s[:-3]
    while s:
        formatted = s[-2:] + "," + formatted
        s = s[:-2]
    return f"₹{formatted}.{dec}"

def format_upi_message(debtor: str, creditor: str, amount: float) -> str:
    """Generate a WhatsApp-ready payment request message."""
    return (f"Hey {creditor}! Sending you {format_inr(amount)} "
            f"for the group expenses. Please share your UPI ID.")
