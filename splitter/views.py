from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ExpenseGroup
from .forms import GroupCreateForm, AddMemberForm
# Add this import at top
from .forms import SignUpForm
from django.contrib.auth import login

@login_required  # remove this decorator — signup must be accessible WITHOUT login
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login after signup
            messages.success(request, f"Welcome, {user.username}! Your account was created.")
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'splitter/signup.html', {'form': form})
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account was created.")
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'splitter/signup.html', {'form': form})
# Add this import at top
from django.db.models import Sum
import json
from .utils import simplify_debts
# Add this import
from .tasks import send_balance_reminder

@login_required
def send_reminder(request, group_id, user_id):
    """Manual trigger - lets group creator send a one-off reminder"""
    group = get_object_or_404(ExpenseGroup, id=group_id, created_by=request.user)
    from django.contrib.auth.models import User
    from .utils import simplify_debts

    target_user = get_object_or_404(User, id=user_id)
    transactions = simplify_debts(group)

    amount = next((t['amount'] for t in transactions if t['from_user'] == target_user.id), None)

    if amount:
        send_balance_reminder.delay(target_user.email, target_user.username, group.name, amount)
        messages.success(request, f"Reminder sent to {target_user.username}!")
    else:
        messages.info(request, f"{target_user.username} has no pending balance.")

    return redirect('group_detail', group_id=group.id)

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(ExpenseGroup, id=group_id, members=request.user)
    members = group.members.all()
    expenses = group.expenses.all().order_by('-created_at')
    add_member_form = AddMemberForm()

    # --- Chart Data Prep ---
    # 1. Contribution pie chart: total paid by each member
    contribution_data = []
    for member in members:
        total_paid = expenses.filter(paid_by=member).aggregate(Sum('amount'))['amount__sum'] or 0
        contribution_data.append({'name': member.username, 'amount': float(total_paid)})

    # 2. Net balance bar chart: uses same logic as simplify_debts but raw balances
    balances = {}
    for member in members:
        balances[member.username] = 0.0

    for expense in expenses:
        balances[expense.paid_by.username] += float(expense.amount)
        for split in expense.splits.all():
            balances[split.user.username] -= float(split.amount_owed)

    balance_data = [{'name': k, 'balance': round(v, 2)} for k, v in balances.items()]

    return render(request, 'splitter/group_detail.html', {
        'group': group,
        'members': members,
        'expenses': expenses,
        'add_member_form': add_member_form,
        'contribution_data_json': json.dumps(contribution_data),
        'balance_data_json': json.dumps(balance_data),
    })
@login_required
def dashboard(request):
    user_groups = ExpenseGroup.objects.filter(members=request.user)
    return render(request, 'splitter/dashboard.html', {'groups': user_groups})


@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupCreateForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            group.members.add(request.user)
            messages.success(request, f"Group '{group.name}' created successfully!")
            return redirect('group_detail', group_id=group.id)
    else:
        form = GroupCreateForm()
    return render(request, 'splitter/create_group.html', {'form': form})


@login_required
def group_detail(request, group_id):
    group = get_object_or_404(ExpenseGroup, id=group_id, members=request.user)
    members = group.members.all()
    expenses = group.expenses.all().order_by('-created_at')
    add_member_form = AddMemberForm()
    return render(request, 'splitter/group_detail.html', {
        'group': group,
        'members': members,
        'expenses': expenses,
        'add_member_form': add_member_form,
    })


@login_required
def add_member(request, group_id):
    group = get_object_or_404(ExpenseGroup, id=group_id, created_by=request.user)
    if request.method == 'POST':
        form = AddMemberForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['username_or_email']
            if user in group.members.all():
                messages.warning(request, f"{user.username} is already in this group.")
            else:
                group.members.add(user)
                messages.success(request, f"{user.username} added to the group!")
        else:
            messages.error(request, "User not found.")
    return redirect('group_detail', group_id=group.id)

# Add these imports at top
from .models import Expense, ExpenseSplit
from .forms import ExpenseForm
from .utils import calculate_splits, simplify_debts
import json


@login_required
def add_expense(request, group_id):
    group = get_object_or_404(ExpenseGroup, id=group_id, members=request.user)
    members = group.members.all()

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            split_type = form.cleaned_data['split_type']
            custom_data = {}

            # Parse custom/percentage values from POST data
            if split_type in ['PERCENTAGE', 'CUSTOM']:
                for member in members:
                    field_name = f'split_{member.id}'
                    value = request.POST.get(field_name)
                    if value:
                        custom_data[member.id] = float(value)

            expense = form.save(commit=False)
            expense.group = group
            expense.paid_by = request.user
            expense.save()

            try:
                splits = calculate_splits(expense, split_type, members, custom_data)
                for split in splits:
                    ExpenseSplit.objects.create(
                        expense=expense,
                        user_id=split['user_id'],
                        amount_owed=split['amount_owed']
                    )
                messages.success(request, "Expense added and split successfully!")
                return redirect('group_detail', group_id=group.id)
            except ValueError as e:
                expense.delete()  # rollback if split calculation fails
                messages.error(request, str(e))
    else:
        form = ExpenseForm()

    return render(request, 'splitter/add_expense.html', {
        'form': form,
        'group': group,
        'members': members,
    })


@login_required
def view_balances(request, group_id):
    group = get_object_or_404(ExpenseGroup, id=group_id, members=request.user)
    transactions = simplify_debts(group)

    # Attach actual User objects for display in template
    from django.contrib.auth.models import User
    enriched = []
    for t in transactions:
        enriched.append({
            'from_user': User.objects.get(id=t['from_user']),
            'to_user': User.objects.get(id=t['to_user']),
            'amount': t['amount'],
        })

    return render(request, 'splitter/balances.html', {
        'group': group,
        'transactions': enriched,
    })
@login_required
def remove_member(request, group_id, user_id):
    group = get_object_or_404(ExpenseGroup, id=group_id, created_by=request.user)
    if str(request.user.id) == str(user_id):
        messages.error(request, "You can't remove yourself.")
    else:
        group.members.remove(user_id)
        messages.success(request, "Member removed.")
    return redirect('group_detail', group_id=group.id)

