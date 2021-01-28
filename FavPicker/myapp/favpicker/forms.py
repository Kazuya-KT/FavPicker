
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

class InputCount(forms.Form):
    count = forms.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3000)])