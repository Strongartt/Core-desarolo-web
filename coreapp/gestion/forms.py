# gestion/forms.py
from django import forms
from .models import Usuario, Curso, Inscripcion

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
