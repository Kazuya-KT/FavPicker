from django.db import models
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator 
# Create your models here.


class InputForm(forms.Form):
    input_val = models.PositiveIntegerField(default=20, validators=[MinValueValidator(1), MaxValueValidator(100)])

    #取得時に使用したJsonをユーザー毎のdbへ登録するモデルは可能であれば後々作成