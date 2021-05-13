
from django import forms
#from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError


def check_count(value):
    if value < 0 or value > 3000:
        raise ValidationError("0~3000の範囲で入力してください")

'''
class InputCount(forms.Form):
    count = forms.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3000)])
'''

class InputCount(forms.Form):
    count = forms.IntegerField(max_value=3000, min_value=1, validators=[check_count])