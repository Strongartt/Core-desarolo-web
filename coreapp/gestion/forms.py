import re

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Curso, Inscripcion, Rol, Perfil, CategoriaCurso, PlanMembresia


class UserPerfilForm(forms.ModelForm):
    rol = forms.ModelChoiceField(queryset=Rol.objects.exclude(codigo='ADMIN'), label="Rol")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super().save(commit)
        perfil, created = Perfil.objects.get_or_create(user=user)
        perfil.rol = self.cleaned_data['rol']
        if commit:
            perfil.save()
        return user

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nombre', 'modalidad', 'fecha_inicio', 'fecha_fin', 'cupo', 'categoria', 'precio']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned = super().clean()
        fi = cleaned.get('fecha_inicio')
        ff = cleaned.get('fecha_fin')
        precio = cleaned.get('precio')

        if fi and ff and ff < fi:
            raise ValidationError("La fecha de fin no puede ser anterior a la de inicio")

        if precio is not None and precio > 50:
            raise ValidationError("El precio del curso no puede ser mayor a $50")

        return cleaned


class CategoriaCursoForm(forms.ModelForm):
    class Meta:
        model = CategoriaCurso
        fields = ['nombre']

class InscripcionForm(forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = ['usuario', 'curso', 'estado']
        widgets = {
            'usuario': forms.Select(),
            'curso':   forms.Select(),
        }

    def clean_estado(self):
        estado = self.cleaned_data['estado']
        validos = ['Inscrito', 'Aprobado', 'Reprobado', 'Retirado']
        if estado not in validos:
            raise ValidationError(f"Estado no válido. Debe ser uno de: {', '.join(validos)}")
        return estado


class SignUpForm(UserCreationForm):
    username   = forms.EmailField(label="Correo electrónico (será tu usuario)")
    first_name = forms.CharField(label="Nombre",   max_length=100)
    last_name  = forms.CharField(label="Apellido", max_length=100)
    rol        = forms.ModelChoiceField(
        queryset=Rol.objects.exclude(codigo='ADMIN'),
        label="Rol",
        help_text="Elige Docente o Estudiante"
    )
    password1  = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput,
        help_text="Mínimo 8 caracteres, una mayúscula, una minúscula y un carácter especial"
    )
    password2  = forms.CharField(
        label="Confirmar contraseña",
        strip=False,
        widget=forms.PasswordInput,
    )

    class Meta:
        model  = User
        fields = ["username", "first_name", "last_name", "rol", "password1", "password2"]

    def clean_username(self):
        email = self.cleaned_data["username"]
        if "@" not in email or not email.endswith(".com"):
            raise ValidationError("El correo debe ser válido y terminar en .com")
        if User.objects.filter(username=email).exists():
            raise ValidationError("Este correo ya está registrado")
        return email

    def clean_first_name(self):
        nombre = self.cleaned_data["first_name"]
        if re.search(r"\d", nombre):
            raise ValidationError("El nombre no puede contener números")
        return nombre

    def clean_last_name(self):
        apellido = self.cleaned_data["last_name"]
        if re.search(r"\d", apellido):
            raise ValidationError("El apellido no puede contener números")
        return apellido

    def clean_password2(self):
        pw1 = self.cleaned_data.get("password1")
        pw2 = self.cleaned_data.get("password2")
        if pw1 and pw2:
            if pw1 != pw2:
                raise ValidationError("Las contraseñas no coinciden")
            if len(pw1) < 8:
                raise ValidationError("La contraseña debe tener al menos 8 caracteres")
            if not re.search(r"[A-Z]", pw1):
                raise ValidationError("Debe incluir al menos una letra mayúscula")
            if not re.search(r"[a-z]", pw1):
                raise ValidationError("Debe incluir al menos una letra minúscula")
            if not re.search(r"[^A-Za-z0-9]", pw1):
                raise ValidationError("Debe incluir al menos un carácter especial")
            if pw1.isdigit():
                raise ValidationError("La contraseña no puede ser solo números")
        return pw2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username   = self.cleaned_data["username"]
        user.email      = self.cleaned_data["username"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name  = self.cleaned_data["last_name"]
        if commit:
            user.save()
            # Crea el perfil si no existe (evita duplicados)
            perfil, created = Perfil.objects.get_or_create(user=user)
            perfil.rol = self.cleaned_data["rol"]
            perfil.save()
        return user

class SeleccionarMembresiaForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['plan_membresia']
        labels = {
            'plan_membresia': 'Selecciona tu plan de membresía'
        }
        
class ActualizarMembresiaUsuarioForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['plan_membresia', 'fecha_inicio_membresia', 'fecha_fin_membresia']
        labels = {
            'plan_membresia': 'Membresía Asignada',
            'fecha_inicio_membresia': 'Fecha de inicio',
            'fecha_fin_membresia': 'Fecha de finalización'
        }
        widgets = {
            'fecha_inicio_membresia': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin_membresia': forms.DateInput(attrs={'type': 'date'}),
        }        