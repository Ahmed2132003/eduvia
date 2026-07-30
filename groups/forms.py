"""
groups/forms.py
================
Part 8 — رفع إثبات الدفع.
"""

from django import forms

from .models import PaymentProof


class PaymentProofForm(forms.ModelForm):
    class Meta:
        model = PaymentProof
        fields = ['receipt_image', 'transaction_reference']
        widgets = {
            'receipt_image': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
                'class': 'field-input',
            }),
            'transaction_reference': forms.TextInput(attrs={
                'placeholder': 'رقم العملية (اختياري)',
                'class': 'field-input',
            }),
        }
        labels = {
            'receipt_image': 'صورة إيصال الدفع',
            'transaction_reference': 'رقم العملية / المرجع',
        }