from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name','phone_number','email']

        labels = {
            'name': "Имя",
            'phone_number': "Номер телефона",
            'email': 'Электронная почта'
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Имя контакта', 'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'XXX-XXX-XXXX', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'contact@example.com', 'class': 'form-input'}),
        }
    