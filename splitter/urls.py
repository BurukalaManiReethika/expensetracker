from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('group/create/', views.create_group, name='create_group'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('group/<int:group_id>/add-member/', views.add_member, name='add_member'),
    path('group/<int:group_id>/remove-member/<int:user_id>/', views.remove_member, name='remove_member'),
]
# Add this function alongside simplify_debts (from earlier)

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
            # last person absorbs rounding difference (avoids paisa mismatch)
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
    from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('group/create/', views.create_group, name='create_group'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('group/<int:group_id>/add-member/', views.add_member, name='add_member'),
    path('group/<int:group_id>/remove-member/<int:user_id>/', views.remove_member, name='remove_member'),
    path('group/<int:group_id>/add-expense/', views.add_expense, name='add_expense'),
    path('group/<int:group_id>/balances/', views.view_balances, name='view_balances'),
]
