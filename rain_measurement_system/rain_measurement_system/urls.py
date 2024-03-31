"""
URL configuration for rain_measurement_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from rain_measurement_system_app import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("", views.index, name="index"),
    path('admin/', admin.site.urls),
    path("login/", views.login, name="login"),
    path("otp_auth/", views.otp_auth, name="otp_auth"),
    path("control_panel/", views.control_panel, name="control_panel"),
    path(
        "control_panel/profile/change_password/",
        views.change_password,
        name="change_password",
    ),
    path("signout/", views.signout, name="signout"),
    path("control_panel/profile/", views.profile, name="profile"),
    path("control_panel/logs/", views.logs, name="logs"),
    path(
        "control_panel/database_from_mysql/",
        views.database_from_mysql,
        name="database_from_mysql",
    ),
    path("control_panel/device_info/", views.device_info, name="device_info"),
    path("control_panel/settings/", views.settings, name="settings"),
    path(
        "water_sensor_data/",
        views.water_sensor_data,
        name="water_sensor_data",
    ),
    path(
        "rain_sensor_data/",
        views.rain_sensor_data,
        name="rain_sensor_data",
    ),
    path("rain_gauge_data/", views.rain_gauge_data, name="rain_gauge_data"),
    path("control_panel/database_from_mysql/live_chart",
         views.live_chart, name="live_chart"),
  path("water_sensor_text_data/",
         views.water_sensor_text_data, name="water_sensor_text_data"),
  path("rain_sensor_text_data/",
         views.rain_sensor_text_data, name="rain_sensor_text_data"),
  path("water_notification_text_data/",
         views.water_notification_text_data, name="water_notification_text_data"),
]
