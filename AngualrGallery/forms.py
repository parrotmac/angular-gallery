# -*- coding: utf-8 -*-
from django import forms


class ImageForm(forms.Form):
    image_file = forms.FileField(
        label='Select image(s)'
    )