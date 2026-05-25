# WhatsApp Expense Splitter

> Split group expenses straight from a WhatsApp chat export. No API. No sign-up.

## The Problem

You went on a trip. Everyone paid for different things.
Now nobody knows who owes who. Splitwise exists but nobody used it during the trip.
This fixes that retroactively — export the chat, upload it, done.

## Features

- Upload any WhatsApp `.txt` export (Android + iOS)
- Smart expense detection — English + Hinglish patterns
- Debt simplification (minimise total transactions)
- UPI deeplinks so people can pay directly in GPay / PhonePe / Paytm
- CSV export and WhatsApp-ready settlement summary

## Quick Start

```bash
pip install -r requirements.txt
streamlit run frontend/app.py
```

## How to Export a WhatsApp Chat

**Android:** Open group → Three dots → More → Export Chat → Without Media

**iOS:** Open group → Group name → Export Chat → Without Media

## Detected Patterns

| Type | Example |
|------|---------|
| English | `"I paid 500 for dinner"` |
| Hinglish | `"petrol ka 800 maine diya"` |
| Third-person | `"Rahul ne 350 diye"` |
| Context noun | `"zomato 650"` |

## Project Structure

```
backend/
  parser.py        WhatsApp .txt parser (Android + iOS)
  extractor.py     Regex-based expense and payer detector
  calculator.py    Net balance computation + debt simplification
  upi.py           UPI deeplink builder + INR formatter

frontend/
  app.py           Streamlit UI

tests/
  test_parser.py
  test_extractor.py
  test_calculator.py

data/
  sample_chat.txt  Goa trip demo (3 members, ~₹28k)
```

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

## Contributing

PRs welcome. Areas that could use work:

- Partial split detection ("only Rahul and me for this one")
- PDF/HTML settlement export
- Telegram group support
- Multi-currency (USD, EUR)

## License

MIT

---

*Built because every trip ends in a "bhai kitna diya?" moment.*
