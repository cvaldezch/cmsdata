#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from .models import *

class logininForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput(render_value=False))

class signupForm(forms.Form):
    """ por algun motivo no funciona """
    class Meta:
        model = User
        fields = ['username', 'password']
        widget = {
            'password' : forms.PasswordInput(render_value=False),
        }

################
class addSupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
    

class addDocumentInForm(forms.ModelForm):
    class Meta:
        model = DocumentIn
        exclude = {'status', 'flag'}

class addDocumentInDetailsForm(forms.ModelForm):
    class Meta:
        model = DetDocumentIn