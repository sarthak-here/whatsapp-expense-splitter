import pytest
from backend.parser import parse_whatsapp_chat, extract_members
from backend.extractor import (
    extract_expenses,
    _extract_amount,
    normalize_amount,
    filter_by_members,
    deduplicate_expenses,
    Expense,
)
from datetime import datetime

EXPENSE_CHAT = """\
25/04/2024, 10:15 am - Rahul: I paid 4800 for the cab booking.
25/04/2024, 12:55 pm - Priya: Paid 2100 for lunch for everyone
25/04/2024, 03:45 pm - Rahul: Hotel ka advance 5000 maine pay kiya
25/04/2024, 09:15 pm - Aakash: will pay later
25/04/2024, 09:20 pm - Aakash: who paid for dinner?
"""


class TestAmountExtraction:
    def test_plain_number(self):
        assert _extract_amount("paid 500 for dinner") == 500.0

    def test_rupee_symbol(self):
        assert _extract_amount("₹1200 for hotel") == 1200.0

    def test_rs_prefix(self):
        assert _extract_amount("rs 750 cab fare") == 750.0

    def test_with_commas(self):
        assert _extract_amount("paid rs 1,200") == 1200.0

    def test_no_amount(self):
        assert _extract_amount("no numbers here at all") is None

    def test_amount_below_threshold(self):
        # amounts < 1 should be ignored
        assert _extract_amount("0.5 something") is None


class TestNormalizeAmount:
    def test_2k(self):
        assert normalize_amount("2k") == "2000"

    def test_1_5k(self):
        assert normalize_amount("1.5k") == "1500"

    def test_plain_number(self):
        assert normalize_amount("500") == "500"

    def test_strips_commas(self):
        assert normalize_amount("1,500") == "1500"

    def test_uppercase_k(self):
        assert normalize_amount("2K") == "2000"


class TestExtractExpenses:
    def setup_method(self):
        self.msgs = parse_whatsapp_chat(EXPENSE_CHAT)
        self.members = extract_members(self.msgs)
        self.expenses = extract_expenses(self.msgs, self.members)

    def test_at_least_two_found(self):
        # "will pay" and "who paid" should be blacklisted
        assert len(self.expenses) >= 2

    def test_blacklist_future_tense(self):
        phrasing = "25/04/2024, 10:00 am - Alice: will pay 500 later\n"
        msgs = parse_whatsapp_chat(phrasing)
        members = extract_members(msgs)
        exps = extract_expenses(msgs, members)
        assert len(exps) == 0

    def test_rahul_is_a_payer(self):
        payers = {e.payer for e in self.expenses}
        assert "Rahul" in payers

    def test_per_head_divides_correctly(self):
        # 3 members, 4800 -> 1600 per head
        members = {"Rahul", "Priya", "Aakash"}
        exp = Expense(payer="Rahul", amount=4800, description="Cab", participants=list(members))
        assert exp.per_head() == 1600.0

    def test_per_head_single_participant(self):
        exp = Expense(payer="Rahul", amount=500, description="test", participants=["Rahul"])
        assert exp.per_head() == 500.0


class TestFilterByMembers:
    def test_keeps_matching(self):
        exps = [
            Expense("Alice", 100, "lunch", ["Alice", "Bob"]),
            Expense("Bob", 200, "cab",   ["Alice", "Bob"]),
        ]
        filtered = filter_by_members(exps, {"Alice"})
        assert len(filtered) == 1
        assert filtered[0].payer == "Alice"

    def test_empty_keep_set(self):
        exps = [Expense("Alice", 100, "test", ["Alice"])]
        assert filter_by_members(exps, set()) == []


class TestDeduplicateExpenses:
    def test_removes_near_duplicate(self):
        t1 = datetime(2024, 4, 25, 10, 0, 0)
        t2 = datetime(2024, 4, 25, 10, 0, 15)  # 15 sec apart
        exps = [
            Expense("Rahul", 500, "dinner", timestamp=t1),
            Expense("Rahul", 500, "dinner", timestamp=t2),
        ]
        result = deduplicate_expenses(exps, tolerance_sec=30)
        assert len(result) == 1

    def test_keeps_different_amounts(self):
        t1 = datetime(2024, 4, 25, 10, 0, 0)
        t2 = datetime(2024, 4, 25, 10, 0, 5)
        exps = [
            Expense("Rahul", 500, "a", timestamp=t1),
            Expense("Rahul", 600, "b", timestamp=t2),
        ]
        result = deduplicate_expenses(exps)
        assert len(result) == 2
