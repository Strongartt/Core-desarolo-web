# gestion/forms.py
from django import forms
from .models import Usuario, Curso, Inscripcion
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Rol, Perfil

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'email', 'password', 'rol']
        widgets = {
            'password': forms.PasswordInput(),
            'rol': forms.Select(),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email.endswith('@midominio.com'):
            raise forms.ValidationError("El correo debe terminar en @midominio.com")
        return email

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nombre', 'modalidad', 'fecha_inicio', 'fecha_fin', 'cupo']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin':    forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('fecha_fin') < cleaned.get('fecha_inicio'):
            raise forms.ValidationError("La fecha de fin no puede ser anterior a la de inicio")
        return cleaned

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
            raise forms.ValidationError(f"Estado no válido. Debe ser uno de: {', '.join(validos)}")
        return estado
class SignUpForm(UserCreationForm):
    email      = forms.EmailField(label="Correo electrónico", required=True)
    first_name = forms.CharField(label="Nombre", max_length=100)
    last_name  = forms.CharField(label="Apellido", max_length=100)
    rol        = forms.ModelChoiceField(
        queryset=Rol.objects.exclude(codigo='ADMIN'),
        label="Rol",
        help_text="Elige Docente o Estudiante"
    )

    class Meta:
        model = User
        fields = (
            "username",    # aquí pueden poner su usuario, o bien configuramos para que sea email
            "email",
            "first_name",
            "last_name",
            "rol",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email      = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name  = self.cleaned_data["last_name"]
        if commit:
            user.save()
            # Creamos el Perfil Django → tu modelo Perfil
            Perfil.objects.create(user=user, rol=self.cleaned_data["rol"])
        return user