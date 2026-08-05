from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages

from .forms import DriverRegistrationForm
from .models import DriverRegistrationModel, FattigueInfoModel

from users.utility.detections import FatigueDetections

import geocoder
import datetime


# ---------------- Driver Registration ---------------- #

def DriverRegisterActions(request):
    if request.method == 'POST':
        form = DriverRegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'You have been successfully registered')
            form = DriverRegistrationForm()
            return render(request, 'AutoistRegister.html', {'form': form})

        else:
            messages.error(request, 'Email or Mobile Already Exists')

    else:
        form = DriverRegistrationForm()

    return render(request, 'AutoistRegister.html', {'form': form})


# ---------------- Driver Login ---------------- #

def AutoistLoginCheck(request):

    if request.method == "POST":

        loginid = request.POST.get("loginid")
        pswd = request.POST.get("pswd")

        try:

            check = DriverRegistrationModel.objects.get(
                loginid=loginid,
                password=pswd
            )

            if check.status == "activated":

                request.session["id"] = check.id
                request.session["loggeduser"] = check.name
                request.session["loginid"] = check.loginid
                request.session["email"] = check.email
                request.session["vehiclenumber"] = check.vehiclenumber

                return render(request, "autoist/AutoistHome.html")

            else:
                messages.error(request, "Your account is not activated.")
                return render(request, "AutoistLogin.html")

        except DriverRegistrationModel.DoesNotExist:

            messages.error(request, "Invalid Login ID or Password")

    return render(request, "AutoistLogin.html")

# ---------------- Detection Loading ---------------- #

def StartDetection(request):

    return render(
        request,
        "autoist/DetectionLoading.html"
    )

# ---------------- Driver Home ---------------- #

def AutoistHome(request):
    return render(request, "autoist/AutoistHome.html")


# ---------------- Detection ---------------- #

def DetectFatigueDriver(request):

    obj = FatigueDetections()
    flag = obj.start_process()

    g = geocoder.ip("me")
    location = g.latlng if g.ok else [None, None]

    latitude = location[0]
    longitude = location[1]

    user_name = request.session.get("loggeduser")
    login_user = request.session.get("loginid")
    email = request.session.get("email")
    vehiclenumber = request.session.get("vehiclenumber")

    current_date = datetime.datetime.now()

    context = {

        "user_name": user_name,
        "login_user": login_user,
        "email": email,
        "vehiclenumber": vehiclenumber,
        "lattitude": latitude,
        "longitude": longitude,
        "fatigue": "No Fatigue",
        "c_date": current_date,

    }

    if flag:

        context["fatigue"] = "Fatigue"

        FattigueInfoModel.objects.create(

            user_name=user_name,
            login_user=login_user,
            email=email,
            vehiclenumber=vehiclenumber,
            lattitude=latitude,
            longitude=longitude,
            fatigue="Fatigue",
            c_date=current_date

        )

    return render(request, "autoist/DetectionImage.html", context)


# ---------------- Training ---------------- #

def StartTraining(request):

    from users.utility import model

    return render(request, "autoist/TrainingComplete.html")


# ---------------- Driver History ---------------- #

def Autoisthistory(request):

    logged_user = request.session.get("loginid")

    data = FattigueInfoModel.objects.filter(
        login_user=logged_user
    )

    return render(
        request,
        "autoist/FastAutoistHistory.html",
        {"data": data}
    )


# ---------------- Forgot Password ---------------- #

def ForgotPassword(request):

    if request.method == "POST":

        loginid = request.POST.get("loginid")
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:

            user = DriverRegistrationModel.objects.get(
                loginid=loginid,
                email=email
            )

            user.password = password
            user.save()

            messages.success(
                request,
                "Password updated successfully."
            )

            return redirect("AutoistLogin")

        except DriverRegistrationModel.DoesNotExist:

            messages.error(
                request,
                "Invalid Login ID or Email."
            )

    return render(request, "ForgotPassword.html")