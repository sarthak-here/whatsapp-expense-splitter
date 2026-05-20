"""calculator.py - Debt simplification engine."""
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List
from expense_extractor import Expense


@dataclass
class Settlement:
    debtor: str
    creditor: str
    amount: float


def compute_balances(expenses: List[Expense]) -> Dict[str, float]:
    """Compute net balance per person. Positive = owed money, Negative = owes."""
    balance: Dict[str, float] = defaultdict(float)
    for exp in expenses:
        if not exp.participants:
            continue
        share = exp.amount / len(exp.participants)
        balance[exp.payer] += exp.amount
        for person in exp.participants:
            balance[person] -= share
    return {p: round(b, 2) for p, b in balance.items()}


def simplify_debts(balances: Dict[str, float]) -> List[Settlement]:
    """Greedy creditor-debtor matching to minimise transaction count."""
    creditors = sorted([(n, a) for n, a in balances.items() if a > 0.01], key=lambda x: -x[1])
    debtors   = sorted([(n, -a) for n, a in balances.items() if a < -0.01], key=lambda x: -x[1])
    creditors = [list(x) for x in creditors]
    debtors   = [list(x) for x in debtors]
    settlements, ci, di = [], 0, 0
    while ci < len(creditors) and di < len(debtors):
        transfer = min(creditors[ci][1], debtors[di][1])
        settlements.append(Settlement(
            debtor=debtors[di][0], creditor=creditors[ci][0], amount=round(transfer, 2)))
        creditors[ci][1] -= transfer
        debtors[di][1]   -= transfer
        if creditors[ci][1] < 0.01: ci += 1
        if debtors[di][1]   < 0.01: di += 1
    return settlements


def full_settlement_pipeline(expenses: List[Expense]) -> List[Settlement]:
    return simplify_debts(compute_balances(expenses))

def settlement_summary(settlements: List[Settlement]) -> dict:
    """Return transaction count and total money moved."""
    return {
        "transactions": len(settlements),
        "total_money_moved": round(sum(s.amount for s in settlements), 2),
    }

def validate_balances(balances: Dict[str, float]) -> bool:
    """Sanity check: sum of all balances must be ~zero."""
    total = sum(balances.values())
    if abs(total) > 1.0:
        raise ValueError(f"Balance sheet error: net={total:.2f}. Check for duplicate expenses.")
    return True
