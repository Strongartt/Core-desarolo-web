# gestion/views.py
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from .models import Curso, Inscripcion
from .forms import CursoForm, InscripcionForm, SignUpForm
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from .forms import UserPerfilForm



class AdministradorRolRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.rol.codigo == 'ADMIN'

class AdminODocenteRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.rol.codigo in ['ADMIN', 'DOC']

class UsuarioListView(LoginRequiredMixin, AdministradorRolRequiredMixin, ListView):
    model = User
    template_name = 'gestion/usuario_list.html'
    context_object_name = 'usuarios'

class UsuarioCreateView(LoginRequiredMixin, AdministradorRolRequiredMixin, CreateView):
    model = User
    form_class = UserPerfilForm
    template_name = 'gestion/usuario_form.html'
    success_url = reverse_lazy('usuario_list')

class UsuarioUpdateView(LoginRequiredMixin, AdministradorRolRequiredMixin, UpdateView):
    model = User
    form_class = UserPerfilForm
    template_name = 'gestion/usuario_form.html'
    success_url = reverse_lazy('usuario_list')


# Permite sólo a super-usuarios
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


# —— CRUD Cursos ——
# Cualquiera que esté autenticado puede listar cursos
class CursoListView(LoginRequiredMixin, ListView):
    model = Curso
    template_name = 'gestion/curso_list.html'
    context_object_name = 'cursos'


class CursoCreateView(LoginRequiredMixin, AdminODocenteRequiredMixin, CreateView):
    model = Curso
    form_class = CursoForm
    template_name = 'gestion/curso_form.html'
    success_url = reverse_lazy('curso_list')

    def form_valid(self, form):
        perfil = getattr(self.request.user, 'perfil', None)
        if perfil and perfil.rol.codigo == 'DOC':
            form.instance.docente = perfil
        return super().form_valid(form)

class MisCursosView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Curso
    template_name = 'gestion/mis_cursos.html'
    context_object_name = 'cursos'

    def test_func(self):
        user = self.request.user
        return hasattr(user, 'perfil') and user.perfil.rol.codigo == 'DOC'

    def get_queryset(self):
        return Curso.objects.filter(docente__user=self.request.user)


class CursoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Curso
    form_class = CursoForm
    template_name = 'gestion/curso_form.html'
    success_url = reverse_lazy('mis_cursos')  # redirige a vista personal

    def test_func(self):
        user = self.request.user
        perfil = getattr(user, 'perfil', None)
        return perfil and self.get_object().docente == perfil


# —— CRUD Inscripciones ——
class InscripcionListView(LoginRequiredMixin, AdministradorRolRequiredMixin, ListView):
    model = Inscripcion
    template_name = 'gestion/inscripcion_list.html'
    context_object_name = 'inscripciones'


class InscripcionCreateView(LoginRequiredMixin, AdministradorRolRequiredMixin, CreateView):
    model = Inscripcion
    form_class = InscripcionForm
    template_name = 'gestion/inscripcion_form.html'
    success_url = reverse_lazy('inscripcion_list')


class InscripcionUpdateView(LoginRequiredMixin, AdministradorRolRequiredMixin, UpdateView):
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
        user = self.request.user
        return hasattr(user, 'perfil') and user.perfil.rol.codigo == 'DOC'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        perfil = self.request.user.perfil

        # Solo cursos asignados al docente logueado
        cursos_docente = Curso.objects.filter(docente=perfil)

        datos = []
        for curso in cursos_docente:
            inscripciones = Inscripcion.objects.filter(curso=curso)
            total = inscripciones.count()

            # Calcular estado medio si hay inscripciones
            if total > 0:
                estados = inscripciones.values_list('estado', flat=True)
                estado_mas_frecuente = max(set(estados), key=estados.count)
            else:
                estado_mas_frecuente = "Sin inscripciones"

            datos.append({
                'id': curso.id, 
                'nombre': curso.nombre,
                'inscritos': total,
                'estado_medio': estado_mas_frecuente
            })

        ctx['datos'] = datos
        return ctx

class DetalleCursoDocenteView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'gestion/reporte_docente_detalle.html'

    def test_func(self):
        user = self.request.user
        return hasattr(user, 'perfil') and user.perfil.rol.codigo == 'DOC'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        curso_id = self.kwargs['pk']
        perfil = self.request.user.perfil

        curso = Curso.objects.filter(id=curso_id, docente=perfil).first()
        if curso:
            inscripciones = Inscripcion.objects.filter(curso=curso).select_related('usuario')
            ctx['curso'] = curso
            ctx['inscripciones'] = inscripciones
        else:
            ctx['curso'] = None
            ctx['inscripciones'] = []
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
        return reverse_lazy('dashboard') 

