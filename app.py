"""app.py - WhatsApp Expense Splitter. Run: streamlit run app.py"""
import io
import streamlit as st
import pandas as pd

from parser import parse_whatsapp_chat, extract_members
from expense_extractor import extract_expenses
from calculator import compute_balances, simplify_debts
from upi import build_upi_link, qr_code_url, format_inr

st.set_page_config(page_title="WA Expense Splitter", page_icon="💸", layout="wide")

with st.sidebar:
    st.title("💸 WA Expense Splitter")
    st.caption("No API. No sign-up. Just paste your chat.")
    st.divider()
    st.subheader("Upload Chat")
    uploaded = st.file_uploader("Choose .txt file", type=["txt"])
    use_sample = st.checkbox("Use sample chat (Goa trip)", value=not bool(uploaded))

chat_text = ""
if uploaded:
    chat_text = uploaded.read().decode("utf-8", errors="replace")
elif use_sample:
    try:
        with open("sample_chat.txt", encoding="utf-8") as f:
            chat_text = f.read()
    except FileNotFoundError:
        st.error("sample_chat.txt not found.")

if not chat_text:
    st.title("💸 WhatsApp Expense Splitter")
    st.info("Upload a WhatsApp chat export or enable sample chat in sidebar.")
    st.stop()

messages = parse_whatsapp_chat(chat_text)
members  = extract_members(messages)
expenses = extract_expenses(messages, members)

st.title("💸 Expense Splitter")
st.caption(f"{len(messages):,} messages | {len(members)} members | {len(expenses)} expenses detected")

c1, c2, c3, c4 = st.columns(4)
total = sum(e.amount for e in expenses)
c1.metric("Total Spent", format_inr(total))
c2.metric("Members", len(members))
c3.metric("Expenses Found", len(expenses))
c4.metric("Per Head", format_inr(total / len(members) if members else 0))
st.divider()
