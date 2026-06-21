from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ExpenseGroup
from .forms import GroupCreateForm, AddMemberForm


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


@login_required
def remove_member(request, group_id, user_id):
    group = get_object_or_404(ExpenseGroup, id=group_id, created_by=request.user)
    if str(request.user.id) == str(user_id):
        messages.error(request, "You can't remove yourself.")
    else:
        group.members.remove(user_id)
        messages.success(request, "Member removed.")
    return redirect('group_detail', group_id=group.id)
