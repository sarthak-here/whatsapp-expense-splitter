import pytest
from backend.extractor import Expense
from backend.calculator import (
    compute_balances,
    simplify_debts,
    validate_balances,
    settlement_summary,
    top_spender,
    full_settlement_pipeline,
)


def _exp(payer, amount, members):
    return Expense(payer=payer, amount=amount, description="test", participants=list(members))


class TestComputeBalances:
    def test_even_three_way_split(self):
        members = {"Alice", "Bob", "Charlie"}
        b = compute_balances([_exp("Alice", 300, members)])
        assert abs(b["Alice"] - 200) < 0.01   # paid 300, owes 100 -> net +200
        assert abs(b["Bob"]   + 100) < 0.01
        assert abs(b["Charlie"] + 100) < 0.01

    def test_two_equal_payers_cancel_out(self):
        members = {"Alice", "Bob"}
        exps = [_exp("Alice", 200, members), _exp("Bob", 200, members)]
        b = compute_balances(exps)
        assert abs(b.get("Alice", 0)) < 0.01
        assert abs(b.get("Bob",   0)) < 0.01

    def test_empty_list(self):
        assert compute_balances([]) == {}

    def test_skips_expense_with_no_participants(self):
        exp = Expense(payer="Alice", amount=100, description="test", participants=[])
        b = compute_balances([exp])
        assert b == {}


class TestSimplifyDebts:
    def test_one_owes_other(self):
        members = {"Alice", "Bob"}
        b = compute_balances([_exp("Alice", 200, members)])
        settlements = simplify_debts(b)
        assert len(settlements) == 1
        s = settlements[0]
        assert s.debtor == "Bob"
        assert s.creditor == "Alice"
        assert abs(s.amount - 100) < 0.01

    def test_everyone_settled(self):
        assert simplify_debts({"Alice": 0.0, "Bob": 0.0}) == []

    def test_three_way_transaction_count(self):
        # Alice and Bob each paid 300 for a 3-person group
        # Charlie owes both; greedy should produce at most 2 transactions
        members = {"Alice", "Bob", "Charlie"}
        exps = [_exp("Alice", 300, members), _exp("Bob", 300, members)]
        settlements = simplify_debts(compute_balances(exps))
        assert len(settlements) <= 2

    def test_settlement_amounts_are_positive(self):
        members = {"Alice", "Bob", "Charlie"}
        exps = [_exp("Alice", 600, members)]
        for s in simplify_debts(compute_balances(exps)):
            assert s.amount > 0


class TestValidateBalances:
    def test_valid_zero_sum(self):
        assert validate_balances({"Alice": 100, "Bob": -100}) is True

    def test_small_rounding_ok(self):
        assert validate_balances({"Alice": 100.5, "Bob": -100.4}) is True

    def test_large_discrepancy_raises(self):
        with pytest.raises(ValueError, match="Balance sheet error"):
            validate_balances({"Alice": 200, "Bob": -50})


class TestSettlementSummary:
    def test_keys_present(self):
        members = {"Alice", "Bob"}
        s = settlement_summary(simplify_debts(compute_balances([_exp("Alice", 200, members)])))
        assert "transactions" in s
        assert "total_money_moved" in s

    def test_counts_correctly(self):
        members = {"Alice", "Bob"}
        settlements = simplify_debts(compute_balances([_exp("Alice", 200, members)]))
        s = settlement_summary(settlements)
        assert s["transactions"] == 1
        assert abs(s["total_money_moved"] - 100) < 0.01

    def test_empty_settlements(self):
        s = settlement_summary([])
        assert s["transactions"] == 0
        assert s["total_money_moved"] == 0


class TestTopSpender:
    def test_single_payer(self):
        members = {"Alice", "Bob"}
        exps = [_exp("Alice", 500, members)]
        assert top_spender(exps) == "Alice"

    def test_highest_total_wins(self):
        members = {"Alice", "Bob", "Charlie"}
        exps = [
            _exp("Alice",   300, members),
            _exp("Bob",    1000, members),
            _exp("Alice",   200, members),  # Alice total: 500
        ]
        assert top_spender(exps) == "Bob"

    def test_empty_returns_na(self):
        assert top_spender([]) == "N/A"


class TestFullPipeline:
    def test_end_to_end(self):
        members = {"Alice", "Bob", "Charlie"}
        exps = [
            _exp("Alice", 900, members),
            _exp("Bob",   300, members),
        ]
        settlements = full_settlement_pipeline(exps)
        # Charlie owes money; total settled should equal total owed
        total = sum(s.amount for s in settlements)
        assert total > 0
