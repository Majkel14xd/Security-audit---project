from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .models import *
from .forms import *
from django.http import HttpResponse
from .tasks import *
from django.http import JsonResponse
from django.db import connection
from django.core.mail import send_mail
from django.db.models import *
from datetime import *
from .forms import EmailScheduleForm, EnableOTPForm
from django_otp import user_has_device
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.urls import reverse
from base64 import b32encode
import qrcode
from io import BytesIO
import base64
import pyotp
def index(request):
    if request.user.is_authenticated:
        return redirect("control_panel")
    else:
        return render(request, "index/index.html")

def login(request):
    status_otp = request.session.pop("status_otp", None)
    if request.user.is_authenticated:
        return redirect("control_panel")
    if request.user.is_authenticated and status_otp == 'yes':
        return redirect("control_panel")
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(
            request,
            username=username,
            password=password,
        )
        if user is not None:
            otp_enabled = user_has_device(user)
            if otp_enabled:
                auth_login(request, user)
                return redirect("otp_auth")
            else:
                auth_login(request, user)
                request.session["welcome_message"] = f"Witaj {user.username}!"
                return redirect("control_panel")
        else:
            msg = "Błąd logowania, nieprawidłowy login lub hasło"
            form = AuthenticationForm(request.POST)
            return render(request, "login/login.html", {"form": form, "msg": msg})
    else:
        form = AuthenticationForm()
        return render(request, "login/login.html", {"form": form})


def control_panel(request):
    status_otp = request.session.pop("status_otp", None)
    if request.user.is_authenticated and status_otp == 'no':
        return redirect("otp_auth")
    if not request.user.is_authenticated:
        return redirect("login")
    
    welcome_message = request.session.pop("welcome_message", None)

    context = {
        "welcome_message": welcome_message,
    }
    return render(request, "control_panel/control_panel.html", context)


def change_password(request):
    if not request.user.is_authenticated:
        return redirect("login")
    status_otp = request.session.pop("status_otp", None)
    if request.user.is_authenticated and status_otp == 'no':
        return redirect("otp_auth")
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, ("Hasło zostało zakutalizowane!"))
            return redirect("change_password")
        else:
            messages.error(request, ("Bład w aktualizowaniu hasła."))
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "change_password/change_password.html", {"form": form})


def signout(request):
    logout(request)
    return redirect("index")


def profile(request):
    if not request.user.is_authenticated:
        return redirect("login")
    status_otp = request.session.pop("status_otp", None)
    if request.user.is_authenticated and status_otp == 'no':
        return redirect("otp_auth")
    user = request.user
    otp_enabled = user_has_device(user)
    username = user.username
    email = user.email
    first_name = user.first_name
    last_name = user.last_name
    date_joined = user.date_joined
    last_login = user.last_login
    id_num = user.id
    context = {
        'username': username,
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'date_joined': date_joined,
        'last_login': last_login,
        'id_num': id_num,
        'otp_enabled': otp_enabled,
    }
    return render(request, "profile/profile.html", context)


def logs(request):
    if not request.user.is_authenticated:
        return redirect("login")
    status_otp = request.session.pop("status_otp", None)
    if request.user.is_authenticated and status_otp == 'no':
        return redirect("otp_auth")

    logs = None
    msg_data_empty = ""
    if request.method == "POST":
        form = LogsForm(request.POST)
        if form.is_valid():
            date_from = form.cleaned_data["date_from"]
            date_to = form.cleaned_data["date_to"]
            logs = Logs.objects.filter(
                data_zdarzenia__range=(date_from, date_to))
            if not logs:
                msg_data_empty = "Brak danych albo nie uzupełniona dobrze data szukania"
    else:
        form = LogsForm()
    context = {
        "form": form,
        "logs": logs,
        "msg_data_empty": msg_data_empty,
    }
    return render(request, "logs/logs.html", context)


def database_from_mysql(request):
    if not request.user.is_authenticated:
        return redirect("login")
    status_otp = request.session.pop("status_otp", None)
    if request.user.is_authenticated and status_otp == 'no':
        return redirect("otp_auth")
    data = None
    message = ""
    if request.method == "POST":
        form = Datafrommuysqlform(request.POST)
        if form.is_valid():
            model = form.cleaned_data["model"]
            date_from = form.cleaned_data["date_from"]
            date_to = form.cleaned_data["date_to"]
            if model == "rain_gauge":
                data = RainGaugae.objects.filter(
                    data_odczytu__range=(date_from, date_to),
                )
            elif model == "rain_sensor":
                data = RainSensor.objects.filter(
                    data_odczytu__range=(date_from, date_to),
                )
            elif model == "water_sensor":
                data = WaterSensor.objects.filter(
                    data_odczytu__range=(date_from, date_to),
                )
            if not data:
                message = "Brak dostępnych danych w wybranym zakresie."

    else:
        form = Datafrommuysqlform()

    context = {
        "form": form,
        "data": data,
        "message": message,
    }

    return render(request, "database_from_mysql/database_from_mysql.html", context)


def device_info(request):
    if not request.user.is_authenticated:
        return redirect("login")
    status_otp = request.session.pop("status_otp", None)
    if request.user.is_authenticated and status_otp == 'no':
        return redirect("otp_auth")
    device_connected = "Brak informacji"
    latest_device_info = DeviceInfo.objects.latest('id')
    device_connected_status = device_is_connected()
    if device_connected_status is False:
        device_connected = "Rozłączono"
    if device_connected_status is True:
        device_connected = "Podłączono"
    context = {
        "latest_device_info": latest_device_info,
        "device_connected": device_connected,
    }
    return render(request, "device_info/device_info.html",context)


def settings(request):
    if not request.user.is_authenticated:
        return redirect("login")
    status_otp = request.session.pop("status_otp", None)
    if request.user.is_authenticated and status_otp == 'no':
        return redirect("otp_auth")
    message_sensor_delete = None
    message_logs_delete = None
    message_email = None
    message_device_info_delete = None
    message_otp_enable_again = None
    message_otp_disable = None
    message_otp_disable_again = None
    user = request.user
    email_user = user.email
    form = EmailScheduleForm()
    otp_enabled = user_has_device(user)
    initial = {'enable_otp': otp_enabled}
    otp_form = EnableOTPForm(initial=initial) 
    if request.method == 'POST':
        otp_form = EnableOTPForm(request.POST)
        if otp_form.is_valid():
            if otp_form.cleaned_data['enable_otp']:
                if not user_has_device(request.user):
                    device = TOTPDevice.objects.create(user=request.user)
                    device.save()
                    request.session["message_otp_enable"] = 'Autoryzacja dwuetapowa została włączona.'
                    device = TOTPDevice.objects.get(user=request.user)
                    secret_key = b32encode(device.bin_key).decode('utf-8')
                    otp_url = f'otpauth://totp/{request.user.username}?secret={secret_key}'
                    request.session['otp_url'] = otp_url
                    return redirect(reverse('otp_enable'))
                else:
                    message_otp_enable_again = 'Autoryzacja dwuetapowa jest już włączona.'
            else:
                if user_has_device(request.user):
                    request.user.staticdevice_set.all().delete()
                    request.user.totpdevice_set.all().delete()
                    message_otp_disable = 'Autoryzacja dwuetapowa została wyłączona.'
                else:
                    message_otp_disable_again = 'Autoryzacja dwuetapowa jest już wyłączona.'
        if 'sensors' in request.POST:
            RainGaugae.objects.all().delete()
            RainSensor.objects.all().delete()
            WaterSensor.objects.all().delete()
            message_sensor_delete = 'Pomyślnie usunięto dane z czujnikow.'
        if 'logs' in request.POST:
            Logs.objects.all().delete()
            message_logs_delete = 'Pomyślnie usunięto dane z logow.'
        if 'device_info' in request.POST:
            query_delete_device_info = "DELETE FROM rain_measurement_system.device_info WHERE ID NOT IN (SELECT MAX(ID) FROM rain_measurement_system.device_info); "
            with connection.cursor() as cursor:
                cursor.execute(query_delete_device_info)
            message_device_info_delete = 'Pomyślnie usunięto stare dane o urządzenia'
        if 'send_email' in request.POST:
            form = EmailScheduleForm(request.POST)
            if form.is_valid():
                last_days = int(form.cleaned_data['last_days'])
                water_sensor_query = f'''
                        SELECT AVG(Wartosc) AS Srednia_Wartosc
                            FROM rain_measurement_system.water_sensor
                            WHERE Data_odczytu >= DATE_SUB(CURDATE(), INTERVAL {last_days} DAY) 
                            '''
                rain_sensor_query = f'''
                        SELECT AVG(Wartosc) AS Srednia_Wartosc
                            FROM rain_measurement_system.rain_sensor
                            WHERE Data_odczytu >= DATE_SUB(CURDATE(), INTERVAL {last_days} DAY) 
                            '''
                rain_gaugae_query = f'''
                        SELECT AVG(Wartosc) AS Srednia_Wartosc
                            FROM rain_measurement_system.rain_gaugae
                            WHERE Data_odczytu >= DATE_SUB(CURDATE(), INTERVAL {last_days} DAY) 
                            '''
                with connection.cursor() as cursor:
                    cursor.execute(water_sensor_query)
                    water_sensor_query_result = cursor.fetchone()

                    cursor.execute(rain_sensor_query)
                    rain_sensor_query_result = cursor.fetchone()

                    cursor.execute(rain_gaugae_query)
                    rain_gaugae_query_result = cursor.fetchone()

                email_subject = f'Raport z ostatnich {last_days} dni '
                email_body = f'''
                Średnia wartość z czujnika wody z zostatnich {last_days} dni wynosi: {water_sensor_query_result[0]}
                Średnia wartość z czujnika deszczu z ostatnich {last_days} dni wynosi: {rain_sensor_query_result[0]}
                Średnia wartość z zbiornika wody z deszczu z ostatnich {last_days} dni wynosi: {rain_gaugae_query_result[0]}
                '''
                from_email = 'majkel114xdd@gmail.com'
                recipient_list = [email_user]
                send_mail(email_subject, email_body, from_email,
                          recipient_list)
                message_email = "Email wyslano"
            else:
                form = EmailScheduleForm(request.POST)
                otp_form = EnableOTPForm(request.POST)

        request.session['message_sensor_delete'] = message_sensor_delete
        request.session['message_logs_delete'] = message_logs_delete
        request.session['message_email'] = message_email
        request.session['message_device_info_delete'] = message_device_info_delete
        request.session['message_otp_enable_again'] = message_otp_enable_again
        request.session['message_otp_disable'] = message_otp_disable
        request.session['message_otp_disable_again'] = message_otp_disable_again
        return redirect("settings")

    message_sensor_delete = request.session.pop('message_sensor_delete', None)
    message_logs_delete = request.session.pop('message_logs_delete', None)
    message_email = request.session.pop('message_email', None)
    message_device_info_delete = request.session.pop(
        'message_device_info_delete', None)
    message_otp_enable_again = request.session.pop('message_otp_enable_again',None)
    message_otp_disable = request.session.pop('message_otp_disable',None)
    message_otp_disable_again = request.session.pop('message_otp_disable_again',None)
    context = {
        'message_sensor_delete': message_sensor_delete,
        'message_logs_delete': message_logs_delete,
        'message_email': message_email,
        'message_device_info_delete': message_device_info_delete,
        'email_user': email_user,
        'form': form,
        'otp_form': otp_form,
        'message_otp_enable_again': message_otp_enable_again,
        'message_otp_disable': message_otp_disable,
        'message_otp_disable_again': message_otp_disable_again
    }
    return render(request, 'settings/settings.html', context)


def water_sensor_data(request):
    if not request.user.is_authenticated:
        return redirect("login")
    status_otp = request.session.pop("status_otp", None)
    if request.user.is_authenticated and status_otp == 'no':
        return redirect("otp_auth")
    get_water_sensor_data = water_sensor_data_api()
    return JsonResponse({"get_water_sensor_data": get_water_sensor_data})


def rain_sensor_data(request):
    if not request.user.is_authenticated:
        return redirect("login")
    status_otp = request.session.pop("status_otp", None)
    if request.user.is_authenticated and status_otp == 'no':
        return redirect("otp_auth")
    get_rain_sensor_data = rain_sensor_data_api()
    return JsonResponse({"get_rain_sensor_data": get_rain_sensor_data})


def rain_gauge_data(request):
    if not request.user.is_authenticated:
        return redirect("login")
    status_otp = request.session.pop("status_otp", None)
    if request.user.is_authenticated and status_otp == 'no':
        return redirect("otp_auth")
    get_rain_gauge_data = rain_gauge_data_api()
    return JsonResponse({"get_rain_gauge_data": get_rain_gauge_data})

def water_sensor_text_data(request):
    if not request.user.is_authenticated:
        return redirect("login")
    status_otp = request.session.pop("status_otp", None)
    if request.user.is_authenticated and status_otp == 'no':
        return redirect("otp_auth")
    get_water_sensor_text_data=water_sensor_text_data_api()
    return JsonResponse({"get_water_sensor_text_data": get_water_sensor_text_data})

def rain_sensor_text_data(request):
    if not request.user.is_authenticated:
        return redirect("login")
    status_otp = request.session.pop("status_otp", None)
    if request.user.is_authenticated and status_otp == 'no':
        return redirect("otp_auth")
    get_rain_sensor_text_data=rain_sensor_text_data_api()
    return JsonResponse({"get_rain_sensor_text_data": get_rain_sensor_text_data})

def water_notification_text_data(request):
    if not request.user.is_authenticated:
        return redirect("login")
    status_otp = request.session.pop("status_otp", None)
    if request.user.is_authenticated and status_otp == 'no':
        return redirect("otp_auth")
    get_water_notification_text_data=water_notification_data_api()
    return JsonResponse({"get_water_notification_text_data": get_water_notification_text_data})


def live_chart(request):
    if not request.user.is_authenticated:
        return redirect("login")
    status_otp = request.session.pop("status_otp", None)
    if request.user.is_authenticated and status_otp == 'no':
        return redirect("otp_auth")
    if request.method == 'POST':
        form = SensorSelectionFormGraph(request.POST)
        if form.is_valid():
            sensor_type = form.cleaned_data['sensor_type']
            return render(request, 'live_chart/live_chart.html', {'form': form,'sensor_type': sensor_type})
    else:
        form = SensorSelectionFormGraph()

    return render(request, 'live_chart/live_chart.html', {'form': form})

def otp_auth(request):
    user = request.user
    otp_enabled = user_has_device(user)
    status = 'no'
    request.session["status_otp"] = status
    if request.user.is_authenticated and not otp_enabled:
        return redirect("control_panel")
    if not request.user.is_authenticated and not otp_enabled:
        return redirect("login")
    if request.user.is_authenticated and otp_enabled and status == 'yes':
        return redirect("control_panel")
    if request.user.is_authenticated and otp_enabled and status == 'no':
        print(status)
        device = TOTPDevice.objects.get(user=request.user)
        secret_key = b32encode(device.bin_key).decode('utf-8')
        totp = pyotp.TOTP(secret_key)
        if request.method == "POST":
            print(status)
            form = OTPForm(request.POST)
            if form.is_valid():
                pin = form.cleaned_data["otp_pin"]
                if totp.verify(pin) == True:
                    request.session["welcome_message"] = f"Witaj {request.user.username}!"
                    status = 'yes'
                    request.session["status_otp"] = status
                    print(status)
                    return redirect("control_panel")
                  
                else:
                    status = 'no'
                    msg = "Błąd uwierzytelniania dwuskładnikowego, nieprawidłowy PIN"
                    return render(request, "otp_auth/otp_auth.html", {"form": form, "msg": msg})
        else:
            form = OTPForm()
        return render(request, 'otp_auth/otp_auth.html', {"form": form})

def otp_enable(request):
    status_otp = request.session.pop("status_otp", None)
    if request.user.is_authenticated and status_otp == 'no':
        return redirect("otp_auth")
    user = request.user
    otp_enabled = user_has_device(user)
    message = None
    if not request.user.is_authenticated:
        return redirect("control_panel")
    if request.user.is_authenticated:
        if otp_enabled:
            message_otp_enable = request.session.pop("message_otp_enable", None)
            otp_url = request.session.pop("otp_url", None)
            if otp_url:
                qr = qrcode.make(otp_url)
                qr_code_io = BytesIO()
                qr.save(qr_code_io)
                qr_code_io.seek(0)
                qr_code_base64 = base64.b64encode(qr_code_io.getvalue()).decode('utf-8') 
                context = {
                'otp_url': otp_url,
                'qr_code': f'data:image/png;base64,{qr_code_base64}',
                'message_otp_enable': message_otp_enable
            }
            else:
                context = {
                    'message': message,
                }
        else:
            return redirect("control_panel")
    return render(request, 'otp_enable/otp_enable.html', context)