from django import forms


class LogsForm(forms.Form):
    date_from = forms.DateField(
        label="Data od",
        widget=forms.DateInput(attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"],
    )
    date_to = forms.DateField(
        label="Data do",
        widget=forms.DateInput(attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"],
    )


class Datafrommuysqlform(forms.Form):
    MODELS_CHOICES = [
        ("rain_sensor", "Czujnik Deszczu"),
        ("water_sensor", "Czujnik Wody"),
        ("rain_gauge", "Zbiornik wody po opadach"),
    ]

    model = forms.ChoiceField(
        label="Czujnik",
        choices=MODELS_CHOICES
        )
    date_from = forms.DateField(
        label="Data od",
        widget=forms.DateInput(attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"]
        )
    
    date_to = forms.DateField(
        label="Data do",
        widget=forms.DateInput(attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"]
        )


LAST_DAYS_CHOICES = [
    (1, 'Ostatni dzień'),
    (7, 'Ostatnie 7 dni'),
    (30, 'Ostatnie 30 dni'),
]


class EmailScheduleForm(forms.Form):
    last_days = forms.ChoiceField(
        label='Ilość ostatnich dni',
        choices=LAST_DAYS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )




class SensorSelectionFormGraph(forms.Form):
    SENSOR_CHOICES = (
        ('water_sensor', 'Czujnik wody'),
        ('rain_sensor', 'Czujnik deszczu'),
        ('rain_gauge', 'Zbiornik wody po opadach'),
    )

    sensor_type = forms.ChoiceField(
        label='Wybierz rodzaj czujnika:',
        choices=SENSOR_CHOICES,
    )

class EnableOTPForm(forms.Form):
    enable_otp = forms.BooleanField(label='Włącz lub wyłącz autoryzację dwuetapową', required=False)
