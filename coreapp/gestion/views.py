# gestion/views.py
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView
from .models import Usuario, Curso, Inscripcion
from .forms import UsuarioForm, CursoForm, InscripcionForm

# Mixin que permite solo a superusuarios (o modifica test_func para tu rol Admin)
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

# ---- Usuarios ----

class UsuarioListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Usuario
    template_name = 'gestion/usuario_list.html'
    context_object_name = 'usuarios'

class UsuarioCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'gestion/usuario_form.html'
    success_url = reverse_lazy('usuario_list')

class UsuarioUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'gestion/usuario_form.html'
    success_url = reverse_lazy('usuario_list')

# ---- Cursos ----

class CursoListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Curso
    template_name = 'gestion/curso_list.html'
    context_object_name = 'cursos'

class CursoCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Curso
    form_class = CursoForm
    template_name = 'gestion/curso_form.html'
    success_url = reverse_lazy('curso_list')

class CursoUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Curso
    form_class = CursoForm
    template_name = 'gestion/curso_form.html'
    success_url = reverse_lazy('curso_list')

# ---- Inscripciones ----

class InscripcionListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Inscripcion
    template_name = 'gestion/inscripcion_list.html'
    context_object_name = 'inscripciones'

class InscripcionCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Inscripcion
    form_class = InscripcionForm
    template_name = 'gestion/inscripcion_form.html'
    success_url = reverse_lazy('inscripcion_list')

class InscripcionUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Inscripcion
    form_class = InscripcionForm
    template_name = 'gestion/inscripcion_form.html'
    success_url = reverse_lazy('inscripcion_list')
