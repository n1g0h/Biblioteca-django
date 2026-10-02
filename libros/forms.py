from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from .models import PerfilUsuario

User = get_user_model()


class RegistroUsuarioForm(UserCreationForm):
    nombre = forms.CharField(
        max_length=150,
        label="Nombre Completo",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan Pérez'})
    )
    email = forms.EmailField(
        required=True,
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'})
    )
    dni = forms.CharField(
        max_length=20,
        label="DNI / Cédula",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345678-9'})
    )
    telefono = forms.CharField(
        max_length=20,
        required=False,
        label="Teléfono",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('nombre', 'email', 'dni', 'telefono')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['password1', 'password2']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya se encuentra registrado. Intenta iniciar sesión.")
        return email

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if PerfilUsuario.objects.filter(dni=dni).exists():
            raise ValidationError("Este DNI / Cédula ya está registrado.")
        return dni

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email']
        user.username = email
        user.email = email
        user.first_name = self.cleaned_data['nombre']

        if commit:
            user.save()

        return user


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••'
        })
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data