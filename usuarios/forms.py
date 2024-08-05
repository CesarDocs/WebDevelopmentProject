import datetime
from django import forms
from django.contrib.auth.models import User
from .models import Perfil, Calificacion, Alumno, Maestro
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
import re


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']


####
          ##PERFIL##
####
class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido', 'email','telefono', 'tipo_usuario', 'fecha_nacimiento']

####
          ##LOGIN##
####
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label=("Nombre de usuario"),
        max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'})
    )
    password = forms.CharField(
        label=("Contraseña"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

####
          ##REGISTO DE PERFIL##
####
class RegistroPerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = [
            'primer_nombre', 'segundo_nombre', 'primer_apellido', 
            'segundo_apellido', 'email', 'telefono', 'tipo_usuario', 'fecha_nacimiento'
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento > datetime.date.today():
            raise forms.ValidationError("La fecha de nacimiento no puede ser en el futuro.")
        return fecha_nacimiento
    

class ContactoForm(forms.ModelForm):
    telefono = forms.CharField(max_length=10)
    email = forms.EmailField()
    password_actual = forms.CharField(widget=forms.PasswordInput(), required=True)

    class Meta:
        model = User
        fields = ['email']

    def clean(self):
        cleaned_data = super().clean()
        password_actual = cleaned_data.get('password_actual')

        if not self.instance.check_password(password_actual):
            raise forms.ValidationError('La contraseña actual es incorrecta.')

        return cleaned_data



class CambioContrasenaForm(forms.Form):
    password_actual = forms.CharField(widget=forms.PasswordInput(), required=True)
    nueva_password = forms.CharField(widget=forms.PasswordInput(), required=True)
    confirmar_password = forms.CharField(widget=forms.PasswordInput(), required=True)

    def clean_nueva_password(self):
        password = self.cleaned_data.get('nueva_password')
        if len(password) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("La contraseña debe tener al menos una letra mayúscula.")
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("La contraseña debe tener al menos una letra minúscula.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError("La contraseña debe tener al menos un carácter especial.")
        if re.search(r'(.)\1', password):
            raise forms.ValidationError("La contraseña no debe contener caracteres consecutivos repetidos.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password_actual = cleaned_data.get('password_actual')
        nueva_password = cleaned_data.get('nueva_password')
        confirmar_password = cleaned_data.get('confirmar_password')

        if nueva_password != confirmar_password:
            self.add_error('confirmar_password', "Las contraseñas no coinciden.")

        return cleaned_data
    

class RecuperacionContrasenaForm(forms.Form):
    username = forms.CharField(label='Nombre de usuario', max_length=150)
    nueva_password = forms.CharField(widget=forms.PasswordInput(), label='Nueva contraseña')
    confirmar_password = forms.CharField(widget=forms.PasswordInput(), label='Confirmar nueva contraseña')

    def clean_nueva_password(self):
        nueva_password = self.cleaned_data.get('nueva_password')
        
        # Validar longitud mínima de 8 caracteres
        if len(nueva_password) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        # Validar que contenga al menos una mayúscula
        if not re.search(r'[A-Z]', nueva_password):
            raise forms.ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        
        # Validar que contenga al menos una minúscula
        if not re.search(r'[a-z]', nueva_password):
            raise forms.ValidationError("La contraseña debe contener al menos una letra minúscula.")
        
        # Validar que contenga al menos un carácter especial
        if not re.search(r'[\W_]', nueva_password):
            raise forms.ValidationError("La contraseña debe contener al menos un carácter especial.")
        
        # Validar que no contenga números y letras consecutivas
        if re.search(r'(01|12|23|34|45|56|67|78|89|ab|bc|cd|de|ef|fg|gh|hi|ij|jk|kl|lm|mn|no|op|pq|qr|rs|st|tu|uv|vw|wx|xy|yz)', nueva_password.lower()):
            raise forms.ValidationError("La contraseña no debe contener números y letras consecutivas.")

        return nueva_password

    def clean(self):
        cleaned_data = super().clean()
        nueva_password = cleaned_data.get('nueva_password')
        confirmar_password = cleaned_data.get('confirmar_password')

        if nueva_password != confirmar_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data


class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['alumno', 'materia', 'calificacion1', 'calificacion2', 'calificacion3']