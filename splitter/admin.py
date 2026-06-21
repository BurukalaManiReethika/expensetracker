from django.contrib import admin
from .models import ExpenseGroup, Expense, ExpenseSplit, Settlement

admin.site.register(ExpenseGroup)
admin.site.register(Expense)
admin.site.register(ExpenseSplit)
admin.site.register(Settlement)
