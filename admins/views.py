from django.shortcuts import render, redirect
from django.contrib import messages

from admins.models import AdminModel
from users.models import DriverRegistrationModel, FattigueInfoModel


# ===========================
# ADMIN LOGIN
# ===========================

def AdminLoginCheck(request):

    if request.method == "POST":

        username = request.POST.get("loginid")
        password = request.POST.get("pswd")

        try:
            admin = AdminModel.objects.get(
                username=username,
                password=password
            )

            request.session["admin_id"] = admin.id
            request.session["admin_username"] = admin.username

            return redirect("AdminHome")

        except AdminModel.DoesNotExist:
            messages.error(request, "Invalid Username or Password")

    return render(request, "AdminLogin.html")


# ===========================
# ADMIN DASHBOARD
# ===========================

def AdminHome(request):

    if "admin_id" not in request.session:
        return redirect("AdminLogin")

    total_drivers = DriverRegistrationModel.objects.count()

    active_drivers = DriverRegistrationModel.objects.filter(
        status="activated"
    ).count()

    blocked_drivers = DriverRegistrationModel.objects.filter(
        status="waiting"
    ).count()

    fatigue_cases = FattigueInfoModel.objects.count()

    context = {
        "total_drivers": total_drivers,
        "active_drivers": active_drivers,
        "blocked_drivers": blocked_drivers,
        "fatigue_cases": fatigue_cases,
        "admin_username": request.session.get("admin_username"),
    }

    return render(request, "admins/AdminHome.html", context)


# ===========================
# VIEW REGISTERED DRIVERS
# ===========================

from django.db.models import Q



def ViewRegisteredAutoists(request):

    search = request.GET.get("search", "")
    status = request.GET.get("status", "")

    data = DriverRegistrationModel.objects.all()

    if search:
        data = data.filter(
            Q(name__icontains=search) |
            Q(vehiclenumber__icontains=search) |
            Q(city__icontains=search)
        )

    if status:
        data = data.filter(status=status)

    return render(
        request,
        "admins/ViewRegisterAutoists.html",
        {
            "data": data,
            "search": search,
            "status": status
        },
    )


# ===========================
# ACTIVATE DRIVER
# ===========================

def AdminActivaAutoists(request):

    id = request.GET.get("uid")

    DriverRegistrationModel.objects.filter(
        id=id
    ).update(status="activated")

    return redirect("ViewRegisteredAutoists")


# ===========================
# BLOCK DRIVER
# ===========================

def AdmindeActivaAutoists(request):

    id = request.GET.get("uid")

    DriverRegistrationModel.objects.filter(
        id=id
    ).update(status="waiting")

    return redirect("ViewRegisteredAutoists")


# ===========================
# DELETE DRIVER
# ===========================

def AdminDeleteAutoists(request):

    id = request.GET.get("uid")

    DriverRegistrationModel.objects.filter(
        id=id
    ).delete()

    return redirect("ViewRegisteredAutoists")


# ===========================
# FATIGUE HISTORY
# ===========================

def AdminViewFatigueHistory(request):

    data = FattigueInfoModel.objects.all()

    return render(
        request,
        "admins/ViewAutoistsHistory.html",
        {"data": data},
    )


# ===========================
# OWNER PROFILE
# ===========================

def OwnerProfile(request):

    if "admin_id" not in request.session:
        return redirect("AdminLogin")

    admin = AdminModel.objects.get(
        id=request.session["admin_id"]
    )

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if password != confirm:

            messages.error(request, "Passwords do not match.")

        else:

            admin.username = username
            admin.password = password
            admin.save()

            request.session["admin_username"] = username

            messages.success(
                request,
                "Owner Profile Updated Successfully."
            )

            return redirect("OwnerProfile")

    return render(
        request,
        "admins/OwnerProfile.html",
        {
            "admin": admin
        }
    )