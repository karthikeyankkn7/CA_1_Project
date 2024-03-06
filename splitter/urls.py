from django.urls import path
from splitter import views

app_name = 'splitter'

urlpatterns = [
    path('signup/',views.signup,name="signup"),
    path('login/',views.user_login,name="login"),
    path('logout/',views.user_logout,name="logout"),
    path('create_group/',views.add_group,name="add_group"),
    path('groups_list/',views.group_list,name="group_list"),
    path('groups_detail/<int:pk>',views.group_details,name="group_detail"),
    path('groups_detail/<int:pk>/create_transaction',views.create_transaction,name="create_transaction"),
    path('my_debts/',views.my_debts,name="my_debts"),
    path('settle_debt/<int:pk>',views.delete_debt,name="delete_debt"),
    path('members_list/<int:pk>/',views.list_members,name="list_members"),
    path('add_members/<int:pk>/add/<int:id>/',views.add_member,name="add_member"),
    path('<int:pk>/update_transaction/<int:id>/',views.update_transaction,name="update_transaction"),
    path('transaction_details/<int:pk>/',views.transaction_details,name="transaction_details"),
]
