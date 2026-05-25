"""UPI deeplink builder, QR code URL generator, and INR formatter."""
import re
from urllib.parse import quote
from typing import Optional


# UPI handles for the major apps — useful for autocomplete suggestions
KNOWN_UPI_HANDLES = [
    "@ybl",         # PhonePe
    "@oksbi",       # GPay (SBI)
    "@okhdfcbank",  # GPay (HDFC)
    "@paytm",       # Paytm
    "@ibl",         # ICICI
    "@upi",         # BHIM
    "@apl",         # Amazon Pay
]


def build_upi_link(vpa: str, payee_name: str, amount: float, note: str = "Group expense") -> str:
    """Build a upi:// deeplink compatible with GPay, PhonePe, Paytm, and BHIM."""
    return (
        f"upi://pay?pa={vpa}"
        f"&pn={quote(payee_name)}"
        f"&am={amount:.2f}"
        f"&cu=INR"
        f"&tn={quote(note)}"
    )


def qr_code_url(upi_link: str, size: int = 200) -> str:
    """Return a QR code image URL via api.qrserver.com (no API key needed)."""
    return (
        f"https://api.qrserver.com/v1/create-qr-code/"
        f"?size={size}x{size}&data={quote(upi_link, safe='')}"
    )


def format_inr(amount: float) -> str:
    """Format a float as an Indian Rupee string, e.g. 1,23,456.78 -> ₹1,23,456.78"""
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
    """Build a WhatsApp-ready payment request message."""
    return (
        f"Hey {creditor}! Sending you {format_inr(amount)} "
        f"for the group expenses. Please share your UPI ID."
    )


def validate_vpa(vpa: str) -> bool:
    """Return True if the VPA looks valid (localpart@provider)."""
    return bool(re.match(r"^[\w.\-+]+@[\w]+$", vpa.strip()))
