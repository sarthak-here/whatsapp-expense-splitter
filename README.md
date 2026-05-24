# WhatsApp Expense Splitter

> Split group expenses from your WhatsApp chat. No API. No sign-up.

## The Problem

You went on a trip. Everyone paid for different things.
Now nobody knows who owes who. Splitwise exists but nobody used it during the trip.
This fixes that retroactively - export the chat, upload it, done.

## Features

- Upload WhatsApp .txt export (Android + iOS)
- Smart expense detection - English + Hinglish
- Debt simplification algorithm (minimize transactions)
- UPI deeplinks to pay directly in GPay / PhonePe / Paytm

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## How to Export WhatsApp Chat

**Android:** Open group -> Three dots -> More -> Export Chat -> Without Media

**iOS:** Open group -> Group name -> Export Chat -> Without Media

## Detected Patterns

| Type | Example |
|------|---------|
| English | "I paid 500 for dinner" |
| Hinglish | "petrol ka 800 maine diya" |
| Third-person | "Rahul ne 350 diye" |
| Context noun | "zomato 650" |

## Project Structure

```
app.py                  Streamlit UI
parser.py               WhatsApp .txt parser
expense_extractor.py    Regex-based expense detector
calculator.py           Debt simplification algorithm
upi.py                  UPI deeplink + QR generator
sample_chat.txt         Sample Goa trip demo
```

## Contributing

PRs welcome! Potential improvements:
- Partial split detection ("only Rahul and me for this")
- PDF/HTML settlement export
- Telegram group support
- Multi-currency (USD, EUR)

## License

MIT

---
*Built because every trip ends in a 'bhai kitna diya?' moment.*
