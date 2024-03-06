from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class group(models.Model):
    creater = models.ForeignKey(User,on_delete=models.CASCADE,related_name="creater")
    name = models.CharField(max_length=250)
    members = models.ManyToManyField(User,through="group_members")

    def __str__(self):
        return self.name

class group_members(models.Model):
    group = models.ForeignKey(group, on_delete = models.CASCADE, related_name = "group_name")
    member = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "grouo_member")

    def __str__(self):
        return self.member.username + ' in group ' + self.group.name

    class Meta:
        unique_together = ('group','member')

class transaction(models.Model):
    group = models.ForeignKey(group, on_delete = models.CASCADE, related_name = 'group_transaction')
    amount = models.IntegerField()
    reason = models.CharField(max_length = 250)
    created_at = models.DateTimeField(auto_now=True)
    payer = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'transaction_payer')
    splitters = models.ManyToManyField(User, related_name = "transaction_members")

    def __str__(self):
        return self.reason + ' in group ' + self.group.name


class debt(models.Model):
    group = models.ForeignKey(group,on_delete = models.CASCADE, related_name = 'group_debts')
    transaction = models.ForeignKey(transaction, on_delete = models.CASCADE, related_name = 'transactions_debt')
    sender = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'transaction_sender')
    receiver = models.ForeignKey(User, on_delete= models.CASCADE, related_name = 'transaction_receiver')
    amount = models.IntegerField()

    def __str__(self):
        return self.sender.username + ' pay to ' + self.receiver.username + ' in group ' + self.group.name

class final_transactions(models.Model):
    sender = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'final_transaction_sender')
    receiver = models.ForeignKey(User, on_delete= models.CASCADE, related_name = 'final_transaction_receiver')
    final_amount = models.IntegerField()

    def __str__(self):
        return self.sender.username + ' gives amount ' + str(self.final_amount) + ' to ' +self.receiver.username
