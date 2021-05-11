from . import views as view
from django.urls import path
from django.contrib.auth import views



app_name = "favpicker"

urlpatterns = [
    path('main/', view.main_page, name="main_page"), # リダイレクト
    path('', views.LoginView.as_view(template_name="favpicker/login_top.html"),name='login'),
    path('logout/', views.LogoutView.as_view(template_name="favpicker/logout.html"), name='logout'),
    path('main/dl', view.pic_dl, name="pic_dl"),
]