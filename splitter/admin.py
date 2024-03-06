from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,group,group_members,transaction,debt,final_transactions

admin.site.register(User, UserAdmin)
admin.site.register(group)
admin.site.register(group_members)
admin.site.register(transaction)
admin.site.register(debt)
admin.site.register(final_transactions)
