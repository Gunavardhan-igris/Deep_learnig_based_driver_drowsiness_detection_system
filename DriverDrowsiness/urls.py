from django.contrib import admin
from django.urls import path
from DriverDrowsiness import views as mainView
from users import views as usr
from admins import views as admins

urlpatterns = [
    path('admin/', admin.site.urls),

    # Main Pages
    path("", mainView.index, name='index'),
    path("index/", mainView.index, name="index"),
    path("logout/", mainView.logout, name="logout"),
    path("AutoistLogin/", mainView.AutoistLogin, name="AutoistLogin"),
    path("AdminLogin/", mainView.AdminLogin, name="AdminLogin"),
    path("AutoistRegister/", mainView.AutoistRegister, name="AutoistRegister"),
    path("ForgotPassword/", usr.ForgotPassword, name="ForgotPassword"),

    # Driver Side
    path("DriverRegisterActions/", usr.DriverRegisterActions, name="DriverRegisterActions"),
    path("AutoistLoginCheck/", usr.AutoistLoginCheck, name="AutoistLoginCheck"),
    path("AutoistHome/", usr.AutoistHome, name="AutoistHome"),
    path(
    "StartDetection/",
    usr.StartDetection,
    name="StartDetection"
), 
    path("DetectFatigueDriver/", usr.DetectFatigueDriver, name="DetectFatigueDriver"),
    path("StartTraining/", usr.StartTraining, name="StartTraining"),
    path("Autoisthistory/", usr.Autoisthistory, name="Autoisthistory"),

    # Admin Side
    path("AdminLoginCheck/", admins.AdminLoginCheck, name="AdminLoginCheck"),
    path("AdminHome/", admins.AdminHome, name="AdminHome"),
    path(
    "OwnerProfile/",
    admins.OwnerProfile,
    name="OwnerProfile"
),
    path("ViewRegisteredAutoists/", admins.ViewRegisteredAutoists, name="ViewRegisteredAutoists"),
    path("AdminActivaAutoists/", admins.AdminActivaAutoists, name="AdminActivaAutoists"),
    path("AdmindeActivaAutoists/", admins.AdmindeActivaAutoists, name="AdmindeActivaAutoists"),
    path("AdminDeleteAutoists/", admins.AdminDeleteAutoists, name="AdminDeleteAutoists"),
    path("AdminViewFatigueHistory/", admins.AdminViewFatigueHistory, name="AdminViewFatigueHistory"),
]
