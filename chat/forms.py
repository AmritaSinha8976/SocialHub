from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model  = Message
        fields = ['text']
        widgets = {'text': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type a message...',
            'autocomplete': 'off',
            'maxlength': 2000,
        })}
        labels = {'text': ''}
