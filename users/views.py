from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse

from .forms import DriverRegistrationForm
from .models import DriverRegistrationModel, FattigueInfoModel
from users.utility.detections_remote import FatigueDetectionsRemote

import geocoder
import datetime
import json


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
    return render(request, "autoist/DetectionLoading.html")


# ---------------- Driver Home ---------------- #

def AutoistHome(request):
    return render(request, "autoist/AutoistHome.html")


# ---------------- Detection ---------------- #

def AnalyzeCameraFrame(request):
    if request.method != 'POST':
        return JsonResponse({"fatigue": False, "message": "Only POST is allowed."})

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"fatigue": False, "message": "Invalid payload."})

    image_data = payload.get('image_data')
    if not image_data:
        return JsonResponse({"fatigue": False, "message": "Image not found."})

    fatigue_result = FatigueDetectionsRemote().predict_from_base64(image_data)
    fatigue = fatigue_result.get("fatigue", False)

    if fatigue:
        user_name = request.session.get("loggeduser")
        login_user = request.session.get("loginid")
        email = request.session.get("email")
        vehiclenumber = request.session.get("vehiclenumber")

        g = geocoder.ip("me")
        location = g.latlng if g.ok else [None, None]

        FattigueInfoModel.objects.create(
            user_name=user_name,
            login_user=login_user,
            email=email,
            vehiclenumber=vehiclenumber,
            lattitude=location[0],
            longitude=location[1],
            fatigue="Fatigue",
            c_date=datetime.datetime.now(),
        )

    return JsonResponse({
        "fatigue": bool(fatigue),
        "drowsiness": fatigue_result.get("drowsiness", 0),
        "left_eye": fatigue_result.get("left_eye", "Unknown"),
        "right_eye": fatigue_result.get("right_eye", "Unknown"),
        "status": fatigue_result.get("status", "Eyes monitored")
    })


def DetectFatigueDriver(request):
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