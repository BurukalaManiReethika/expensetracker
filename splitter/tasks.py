from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_balance_reminder(user_email, username, group_name, amount_owed):
    """Sends an email reminder to a user who owes money in a group"""
    subject = f"Reminder: You owe ₹{amount_owed} in '{group_name}'"
    message = (
        f"Hi {username},\n\n"
        f"This is a friendly reminder that you owe ₹{amount_owed} "
        f"in your group '{group_name}' on Expense Splitter.\n\n"
        f"Please settle up when you get a chance!\n\n"
        f"- Expense Splitter Team"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )


@shared_task
def check_and_send_all_reminders():
    """
    Periodic task: checks all groups, finds users with outstanding balances,
    and sends them reminder emails. Scheduled to run daily via Celery Beat.
    """
    from .models import ExpenseGroup
    from .utils import simplify_debts

    groups = ExpenseGroup.objects.all()
    sent_count = 0

    for group in groups:
        transactions = simplify_debts(group)
        for t in transactions:
            from django.contrib.auth.models import User
            debtor = User.objects.get(id=t['from_user'])
            if debtor.email:
                send_balance_reminder.delay(
                    debtor.email,
                    debtor.username,
                    group.name,
                    t['amount']
                )
                sent_count += 1

    return f"Sent {sent_count} reminder emails"
