from collections import defaultdict
import heapq


def simplify_debts(group):
    """
    Calculates net balance for each user in the group,
    then minimizes the number of transactions needed to settle all debts.

    Logic:
    - Positive balance = should receive money
    - Negative balance = owes money
    - Match biggest debtor with biggest creditor repeatedly
    """
    balances = defaultdict(float)

    # Step 1: Calculate net balance per user from expenses
    for expense in group.expenses.all():
        balances[expense.paid_by_id] += float(expense.amount)
        for split in expense.splits.all():
            balances[split.user_id] -= float(split.amount_owed)

    # Step 2: Account for settlements already made
    for settlement in group.settlements.all():
        balances[settlement.paid_by_id] += float(settlement.amount)
        balances[settlement.paid_to_id] -= float(settlement.amount)

    # Step 3: Separate into creditors (max-heap) and debtors (max-heap)
    creditors = [(-amt, uid) for uid, amt in balances.items() if amt > 0.01]
    debtors = [(amt, uid) for uid, amt in balances.items() if amt < -0.01]

    heapq.heapify(creditors)
    heapq.heapify(debtors)

    transactions = []

    while creditors and debtors:
        credit_amt, creditor_id = heapq.heappop(creditors)
        debit_amt, debtor_id = heapq.heappop(debtors)

        credit_amt = -credit_amt
        settle_amt = min(credit_amt, -debit_amt)

        transactions.append({
            'from_user': debtor_id,
            'to_user': creditor_id,
            'amount': round(settle_amt, 2)
        })

        remaining_credit = credit_amt - settle_amt
        remaining_debit = debit_amt + settle_amt

        if remaining_credit > 0.01:
            heapq.heappush(creditors, (-remaining_credit, creditor_id))
        if remaining_debit < -0.01:
            heapq.heappush(debtors, (remaining_debit, debtor_id))

    return transactions


def calculate_splits(expense, split_type, members, custom_data=None):
    """
    Returns a list of dicts: [{'user_id': X, 'amount_owed': Y}, ...]

    custom_data formats:
    - PERCENTAGE: {user_id: percentage, ...}  e.g. {1: 50, 2: 30, 3: 20}
    - CUSTOM: {user_id: amount, ...}  e.g. {1: 200, 2: 150, 3: 150}
    """
    total = float(expense.amount)
    splits = []

    if split_type == 'EQUAL':
        per_head = round(total / len(members), 2)
        running_total = 0
        for i, member in enumerate(members):
            if i == len(members) - 1:
                amount = round(total - running_total, 2)
            else:
                amount = per_head
                running_total += amount
            splits.append({'user_id': member.id, 'amount_owed': amount})

    elif split_type == 'PERCENTAGE':
        if not custom_data:
            raise ValueError("Percentage data required")
        total_pct = sum(custom_data.values())
        if abs(total_pct - 100) > 0.01:
            raise ValueError(f"Percentages must sum to 100, got {total_pct}")
        for member in members:
            pct = custom_data.get(member.id, 0)
            amount = round(total * (pct / 100), 2)
            splits.append({'user_id': member.id, 'amount_owed': amount})

    elif split_type == 'CUSTOM':
        if not custom_data:
            raise ValueError("Custom amounts required")
        total_custom = sum(custom_data.values())
        if abs(total_custom - total) > 0.01:
            raise ValueError(f"Custom amounts ({total_custom}) must equal total ({total})")
        for member in members:
            amount = custom_data.get(member.id, 0)
            splits.append({'user_id': member.id, 'amount_owed': round(amount, 2)})

    else:
        raise ValueError("Invalid split type")

    return splits
