from django.contrib import admin
from django.urls import path,include
from splitter import views

urlpatterns = [
    path('',views.HomePage,name = "home"),
    path('admin123/', admin.site.urls),
    path('splitter/',include('splitter.urls')),
]
