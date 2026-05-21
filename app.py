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

tab1, tab2, tab3 = st.tabs(["Settle Up", "Expenses", "Balances"])

with tab1:
    balances    = compute_balances(expenses)
    settlements = simplify_debts(balances)
    if not settlements:
        st.success("Everyone is settled up!")
    for s in settlements:
        st.markdown(f"**{s.debtor}** owes **{s.creditor}** — {format_inr(s.amount)}")
        st.divider()

with tab2:
    rows = [{"Payer": e.payer, "Amount (INR)": e.amount, "Description": e.description,
             "Per Head": e.per_head()} for e in expenses]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

with tab3:
    rows = [{"Member": p, "Balance": b,
             "Status": "Gets back" if b > 0 else ("Owes" if b < 0 else "Settled")}
            for p, b in sorted(compute_balances(expenses).items(), key=lambda x: -x[1])]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

with st.sidebar:
    st.divider()
    st.subheader("UPI IDs (optional)")
    st.caption("Enter UPI IDs to generate pay links")
    if expenses:
        top = max(expenses, key=lambda e: e.amount)
        st.divider()
        st.metric("Biggest Expense", format_inr(top.amount), f"by {top.payer}")
    st.divider()
    st.caption("Tip: more descriptive messages = better detection")

def avatar(name: str) -> str:
    """Return 1-2 char initials."""
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper() if name else "??"
