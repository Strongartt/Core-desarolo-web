# gestion/views.py

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from .models import Usuario, Curso, Inscripcion
from .forms import UsuarioForm, CursoForm, InscripcionForm, SignUpForm
from django.shortcuts import redirect
from .models import Curso, Inscripcion
from django.contrib.auth.views import LoginView


# Permite sólo a super-usuarios
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


# —— CRUD Usuarios ——
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


# —— CRUD Cursos ——
# Cualquiera que esté autenticado puede listar cursos
class CursoListView(LoginRequiredMixin, ListView):
    model = Curso
    template_name = 'gestion/curso_list.html'
    context_object_name = 'cursos'


# Pero solo super-usuarios pueden crear o editar
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


# —— CRUD Inscripciones ——
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


# —— Registro de nuevos usuarios “normales” ——
class SignUpView(CreateView):
    form_class    = SignUpForm
    template_name = 'registration/signup.html'
    success_url   = reverse_lazy('login')


# —— Reportes según rol ——
class ReporteDocenteView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'gestion/reporte_docente.html'

    def test_func(self):
        # Asume que tu User siempre tiene perfil y rol con código 'DOC' para docentes
        return hasattr(self.request.user, 'perfil') and \
               self.request.user.perfil.rol.codigo == 'DOC'


class ReporteEstudianteView(LoginRequiredMixin, TemplateView):
    template_name = 'gestion/reporte_estudiante.html'


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'gestion/dashboard.html'

class ReporteDocenteView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'gestion/reporte_docente.html'
    def test_func(self):
        u = self.request.user
        # super‐usuario o perfil DOC
        return u.is_superuser or (hasattr(u, 'perfil') and u.perfil.rol.codigo == 'DOC')
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # todos los cursos + sus inscripciones
        ctx['cursos'] = Curso.objects.all()
        ctx['inscripciones'] = Inscripcion.objects.select_related('usuario','curso').all()
        return ctx

class ReporteEstudianteView(LoginRequiredMixin, TemplateView):
    template_name = 'gestion/reporte_estudiante.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # filtro por email del Usuario personalizado
        email = self.request.user.email
        ctx['inscripciones'] = Inscripcion.objects.filter(usuario__email=email).select_related('curso')
        return ctx
    
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        """
        Después del login, redirige según rol:
          - superuser → lista de usuarios
          - docente    → gestión de cursos
          - estudiante  → lista de inscripciones propias
        """
        user = self.request.user
        if user.is_superuser:
            return reverse_lazy('usuario_list')
        # asumimos que tienes un perfil con .rol.codigo
        perfil = getattr(user, 'perfil', None)
        if perfil and perfil.rol.codigo == 'DOC':
            return reverse_lazy('curso_list')
        return reverse_lazy('inscripcion_list')