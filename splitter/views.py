from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout,authenticate
from django.http import HttpResponseRedirect,HttpResponse
from splitter.forms import UserForm,GroupForm
from splitter.models import User,group,group_members,transaction,debt,final_transactions
from django.template.loader import render_to_string
from django.db.models import Q
from django.contrib import messages

def HomePage(request):
    if(request.user.is_authenticated):
        return final_settlements(request)
    else:
        return render(request,'splitter/index.html',{})


def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        if(User.objects.filter(username=username).exists()):
            messages.error(request, "Username already exists, try to signin or choose different username")
            return HttpResponseRedirect(reverse('home'))
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()
            messages.error(request,'Account successfully created! Try logging now')
            return HttpResponseRedirect(reverse('home'))

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('home'))

            else:
                return HttpResponse("Account not active")
        else:
            messages.error(request, "Invalid Details")
            return HttpResponseRedirect(reverse('home'))



def add_group(request):
    if request.method == "POST":
        group_name = request.POST.get('group_name')
        new_group = group(creater=request.user,name=group_name)
        new_group.save()
        member = group_members(group=new_group,member=request.user)
        member.save()
        return HttpResponseRedirect(reverse('splitter:group_list'))
    return render(request,'splitter/group_list.html',{'form':form})


"""
Display all the groups in which user is a member.
Filter objects from group_members model.
"""
def group_list(request):
    groups = group_members.objects.filter(member=request.user)
    groups_list = [x.group for x in groups]
    length = False
    if(len(groups_list) == 0):
        length = True
    print(len(groups_list))
    return render(request,'splitter/group_list.html',{'groups_list':groups_list,'length':length})



"""
Display all the details of the group.
group name, Creator, number of members, All the transaction made in the group.
"""
def group_details(request,pk):
    groups = get_object_or_404(group,pk=pk)
    creator = False
    if request.user == groups.creater:
        creator = True
    members = group_members.objects.filter(group=groups)
    members_list = [x.member for x in members]
    members_count = len(members_list)
    transactions = transaction.objects.filter(group=groups)
    return render(request,'splitter/group_detail.html',{'groups':groups,
                                                        'members_list':members_list,
                                                        'transactions':transactions,
                                                        'members_count':members_count,
                                                        'creator':creator})

def add_member(request,pk,id):
    in_group = get_object_or_404(group,pk=pk)
    member = get_object_or_404(User,id=id)
    group_member = group_members(group=in_group,member=member)
    group_member.save()
    return HttpResponseRedirect(reverse('splitter:list_members',kwargs={'pk':pk}))

def list_members(request,pk):
    groups = get_object_or_404(group,pk=pk)
    query = request.GET.get("q", None)
    members = group_members.objects.filter(group=groups)
    members_list = [x.member for x in members]
    qs = User.objects.all()
    if query is not None:
        qs = qs.filter(
                Q(username__icontains=query)
                )
    qs_one = []
    for x in qs:
        if x in members_list:
            pass
        else:
            qs_one.append(x)

    context = {
        "members_list": qs_one,
        "groups":groups
    }
    template = "splitter/members_list.html"
    return render(request, template, context)


def transaction_details(request,pk):
    transactions = get_object_or_404(transaction,pk=pk)
    members = group_members.objects.filter(group=transactions.group)
    all_group_members = [x.member for x in members]
    transaction_splitters = transactions.splitters.all()
    transaction_splitters_username = [x.username for x in transaction_splitters]
    return render(request,'splitter/transaction_details.html',{'transaction':transactions,'transaction_splitters_username':transaction_splitters_username,'all_group_members':all_group_members,'transaction_splitters':transaction_splitters})

def create_transaction(request,pk):
    groups = get_object_or_404(group,pk=pk)
    if request.method == "POST":
        try:
            reason = request.POST.get('reason')
            amount = request.POST.get('amount')
            transaction_members = request.POST.getlist('splitter')
            splitters = User.objects.filter(username__in = transaction_members)
            obj = transaction(group = groups,amount=amount,reason=reason,payer=request.user)
            obj.save()
            obj.splitters.add(*splitters)
            for x in splitters:
                if x == request.user:
                    pass
                else:
                    debt_obj = debt(group = groups,transaction=obj,sender=x,receiver=request.user,amount=int(amount)/len(splitters))
                    debt_obj.save()
                    if_user_sender = final_transactions.objects.filter(sender=request.user,receiver=x)
                    if_user_receiver = final_transactions.objects.filter(sender=x,receiver=request.user)
                    if len(if_user_receiver) == 0 and len(if_user_sender) == 0:
                        final_obj = final_transactions(sender=x,receiver=request.user,final_amount=int(amount)/len(splitters))
                        final_obj.save()
                    else:
                        if len(if_user_receiver) == 1 and len(if_user_sender) == 0:
                            final_objs = final_transactions.objects.get(sender=x,receiver=request.user)
                            final_objs.final_amount += int(amount)/len(splitters)
                            final_objs.save()
                        else:
                            final_objs = final_transactions.objects.get(sender=request.user,receiver=x)
                            final_objs.final_amount -= int(amount)/len(splitters)
                            final_objs.save()
            return HttpResponseRedirect(reverse('splitter:group_detail',kwargs={'pk':pk}))
        except:
            messages.error(request, "Details do not match the specified data type. (Hint: amount should be integer)")
            return HttpResponseRedirect(reverse('splitter:group_detail',kwargs={'pk':pk}))

def update_transaction(request,pk,id):
    groups = get_object_or_404(group,pk=pk)
    members_list = group_members.objects.filter(group=groups)
    members = [x.member for x in members_list]
    prev_transaction = get_object_or_404(transaction,id=id)
    prev_amount = prev_transaction.amount
    prev_reason = prev_transaction.reason
    prev_splitters = prev_transaction.splitters.all()
    prev_splitters_usernames = [x.username for x in prev_splitters]
    if request.method == "POST":
        new_reason = request.POST.get('reason')
        new_amount = request.POST.get('amount')
        new_transaction_members = request.POST.getlist('splitter')
        new_splitters = User.objects.filter(username__in = new_transaction_members)
        obj = transaction(group = groups,amount=new_amount,reason=new_reason,payer=request.user)
        obj.save()
        obj.splitters.add(*new_splitters)
        for x in prev_splitters:
            if x == request.user:
                pass
            else:
                if_user_sender_prev = final_transactions.objects.filter(sender=request.user,receiver=x)
                if_user_receiver_prev = final_transactions.objects.filter(sender=x,receiver=request.user)
                if len(if_user_receiver_prev) == 1 and len(if_user_sender_prev) == 0:
                    final_objs = final_transactions.objects.get(sender=x,receiver=request.user)
                    final_objs.final_amount -= int(prev_amount)/len(prev_splitters)
                    final_objs.save()
                else:
                    final_objs = final_transactions.objects.get(sender=request.user,receiver=x)
                    final_objs.final_amount += int(prev_amount)/len(prev_splitters)
                    final_objs.save()
        for x in new_splitters:
            if x == request.user:
                pass
            else:
                debt_obj = debt(room = rooms,transaction=obj,sender=x,receiver=request.user,amount=int(new_amount)/len(new_splitters))
                debt_obj.save()
                if_user_sender = final_transactions.objects.filter(sender=request.user,receiver=x)
                if_user_receiver = final_transactions.objects.filter(sender=x,receiver=request.user)
                if len(if_user_receiver) == 0 and len(if_user_sender) == 0:
                    final_obj = final_transactions(sender=x,receiver=request.user,final_amount=int(new_amount)/len(new_splitters))
                    final_obj.save()
                else:
                    if len(if_user_receiver) == 1 and len(if_user_sender) == 0:
                        final_objs = final_transactions.objects.get(sender=x,receiver=request.user)
                        final_objs.final_amount += int(new_amount)/len(new_splitters)
                        final_objs.save()
                    else:
                        final_objs = final_transactions.objects.get(sender=request.user,receiver=x)
                        final_objs.final_amount -= int(new_amount)/len(new_splitters)
                        final_objs.save()
        prev_transaction.delete()
        return HttpResponseRedirect(reverse('splitter:room_detail',kwargs={'pk':pk}))
    return HttpResponseRedirect(reverse('splitter:room_detail',kwargs={'pk':pk}))

def my_debts(request):
    income = debt.objects.filter(receiver=request.user)
    expense = debt.objects.filter(sender=request.user)
    query = request.GET.get("q", None)
    if query is not None:
        income = income.filter(
                Q(sender__username__icontains=query) |
                Q(transaction__reason__icontains=query) |
                Q(room__name__icontains=query)
                )
        expense = expense.filter(
                Q(receiver__username__icontains=query) |
                Q(transaction__reason__icontains=query) |
                Q(room__name__icontains=query)
                )
    return render(request,'splitter/my_debts.html',{'incomes':income,'expenses':expense})

def final_settlements(request):
    user_sender = final_transactions.objects.filter(sender = request.user)
    user_receiver = final_transactions.objects.filter(receiver = request.user)
    user_sender_positive = []
    user_sender_negative = []
    user_receiver_positive = []
    user_receiver_negative = []
    noincome = False
    noexpense = False
    for obj in user_sender:
        if(obj.final_amount > 0):
            user_sender_positive.append(obj)
        if(obj.final_amount < 0):
            obj.final_amount = abs(obj.final_amount)
            user_sender_negative.append(obj)
    for obj in user_receiver:
        if(obj.final_amount > 0):
            user_receiver_positive.append(obj)
        if(obj.final_amount < 0):
            obj.final_amount = abs(obj.final_amount)
            user_receiver_negative.append(obj)
    if len(user_receiver_positive) == 0 and len(user_sender_negative) == 0:
        noincome = True
    if len(user_sender_positive) == 0 and len(user_receiver_negative) == 0:
        noexpense = True
    return render(request,'splitter/final_settlements.html',{'user_sender_positive':user_sender_positive,
       'user_sender_negative':user_sender_negative,
        'user_receiver_positive':user_receiver_positive,
            'user_receiver_negative':user_receiver_negative,
                'noincome':noincome,
                    'noexpense':noexpense})

def delete_debt(request,pk):
    if request.method == "POST":
        obj = get_object_or_404(debt,pk=pk)
        if_user_sender = final_transactions.objects.filter(sender=request.user,receiver=obj.sender)
        if_user_receiver = final_transactions.objects.filter(sender=obj.sender,receiver=request.user)
        if len(if_user_receiver) == 1 and len(if_user_sender) == 0:
            final_objs = final_transactions.objects.get(sender=obj.sender,receiver=request.user)
            final_objs.final_amount -= obj.amount
            final_objs.save()
        else:
            final_objs = final_transactions.objects.get(sender=request.user,receiver=obj.sender)
            final_objs.final_amount += obj.amount
            final_objs.save()
        obj.delete()
        return HttpResponseRedirect(reverse('splitter:my_debts'))
    return HttpResponseRedirect(reverse('splitter:my_debts'))
