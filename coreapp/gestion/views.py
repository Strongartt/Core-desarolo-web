# gestion/views.py
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, TemplateView, DeleteView
from .models import Curso, Inscripcion, CategoriaCurso
from .forms import CursoForm, InscripcionForm, SignUpForm,UserPerfilForm, CategoriaCursoForm
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils import timezone


class AdministradorRolRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_superuser or (
            user.is_authenticated and
            hasattr(user, 'perfil') and
            user.perfil.rol.codigo == 'ADMIN'
        )


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


class InscribirseView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return hasattr(self.request.user, 'perfil') and self.request.user.perfil.rol.codigo == 'EST'

    def post(self, request, curso_id):
        curso = get_object_or_404(Curso, pk=curso_id)

        ya_inscrito = Inscripcion.objects.filter(curso=curso, usuario=request.user).exists()
        if ya_inscrito:
            messages.error(request, "Ya estás inscrito en este curso.")
        elif Inscripcion.objects.filter(curso=curso).count() >= curso.cupo:
            messages.error(request, "El curso ya no tiene cupos disponibles.")
        else:
            Inscripcion.objects.create(curso=curso, usuario=request.user, estado="INSCRITO")
            messages.success(request, "Te has inscrito correctamente.")

        return redirect('curso_list')


# —— Registro de nuevos usuarios “normales” ——
class SignUpView(CreateView):
    form_class    = SignUpForm
    template_name = 'registration/signup.html'
    success_url   = reverse_lazy('login')


# —— Reportes según rol ——
class ReporteDocenteView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'gestion/reporte_docente.html'

    def test_func(self):
        user = self.request.user
        return user.is_superuser or (
            hasattr(user, 'perfil') and user.perfil.rol.codigo == 'DOC'
        )


class ReporteEstudianteView(LoginRequiredMixin, TemplateView):
    template_name = 'gestion/reporte_estudiante.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hoy = timezone.now().date()

        datos = []
        inscripciones = Inscripcion.objects.filter(usuario=self.request.user).select_related('curso')
        for ins in inscripciones:
            curso = ins.curso
            datos.append({
                'id': ins.id,
                'nombre': curso.nombre,
                'modalidad': curso.modalidad,
                'fecha_inscripcion': ins.fecha_inscripcion,
                'estado_inscripcion': "Inscrito" if ins.estado.upper() == "INSCRITO" else "Dado de baja",
                'estado_curso': "En curso" if curso.fecha_fin >= hoy else "Finalizado",
                'solicitud_baja': ins.solicitud_baja
            })

        ctx['inscripciones'] = datos
        return ctx

class SolicitarBajaView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return hasattr(self.request.user, 'perfil') and self.request.user.perfil.rol.codigo == 'EST'

    def post(self, request, pk):
        inscripcion = get_object_or_404(Inscripcion, id=pk, usuario=request.user)
        if inscripcion.solicitud_baja == 'NINGUNA' and inscripcion.estado.upper() == 'INSCRITO':
            inscripcion.solicitud_baja = 'PENDIENTE'
            inscripcion.save()
            messages.success(request, "Solicitud de baja enviada.")
        else:
            messages.warning(request, "No puedes enviar esta solicitud.")
        return redirect('reporte_estudiante')



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
                estado_list = list(estados)
                estado_mas_frecuente = max(set(estado_list), key=estado_list.count)
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
    
class GestionSolicitudesBajaView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'gestion/solicitudes_baja_docente.html'

    def test_func(self):
        return hasattr(self.request.user, 'perfil') and self.request.user.perfil.rol.codigo == 'DOC'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        perfil = self.request.user.perfil
        solicitudes = Inscripcion.objects.filter(
            curso__docente=perfil,
            solicitud_baja='PENDIENTE'
        ).select_related('curso', 'usuario')

        ctx['solicitudes'] = solicitudes
        return ctx
   
class AprobarBajaView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return hasattr(self.request.user, 'perfil') and self.request.user.perfil.rol.codigo == 'DOC'

    def post(self, request, pk):
        ins = get_object_or_404(Inscripcion, id=pk, curso__docente=request.user.perfil)
        ins.solicitud_baja = 'APROBADA'
        ins.estado = 'BAJA'
        ins.save()
        messages.success(request, "Baja aprobada.")
        return redirect('solicitudes_baja')


class RechazarBajaView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return hasattr(self.request.user, 'perfil') and self.request.user.perfil.rol.codigo == 'DOC'

    def post(self, request, pk):
        ins = get_object_or_404(Inscripcion, id=pk, curso__docente=request.user.perfil)
        ins.solicitud_baja = 'RECHAZADA'
        ins.save()
        messages.info(request, "Solicitud de baja rechazada.")
        return redirect('solicitudes_baja')


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return reverse_lazy('gestion_admin')
        perfil = getattr(user, 'perfil', None)
        if perfil and perfil.rol.codigo == 'DOC':
            return reverse_lazy('curso_list')
        return reverse_lazy('dashboard')


class EditarNotasAsistenciaView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'gestion/editar_notas_asistencia.html'

    def test_func(self):
        user = self.request.user
        return hasattr(user, 'perfil') and user.perfil.rol.codigo == 'DOC'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        curso_id = self.kwargs.get('pk')
        perfil = self.request.user.perfil

        curso = get_object_or_404(Curso, id=curso_id, docente=perfil)
        inscripciones = Inscripcion.objects.filter(curso=curso).select_related('usuario')

        ctx['curso'] = curso
        ctx['inscripciones'] = inscripciones
        return ctx

    def post(self, request, *args, **kwargs):
        perfil = request.user.perfil
        curso_id = self.kwargs.get('pk')
        curso = get_object_or_404(Curso, id=curso_id, docente=perfil)

        for inscripcion in Inscripcion.objects.filter(curso=curso):
            nota_key = f'nota_{inscripcion.id}'
            asistencia_key = f'asistencia_{inscripcion.id}'

            try:
                nota = request.POST.get(nota_key)
                asistencia = request.POST.get(asistencia_key)

                if nota:
                    inscripcion.nota_final = float(nota)
                if asistencia:
                    inscripcion.asistencia_total = int(asistencia)

                inscripcion.save()
            except ValueError:
                pass  # Puedes agregar mensajes si deseas manejar errores específicos

        messages.success(request, "Notas y asistencia actualizadas.")
        return redirect('editar_notas_asistencia', pk=curso.id)
    
class CategoriaCreateView(LoginRequiredMixin, AdministradorRolRequiredMixin, CreateView):
    model = CategoriaCurso
    form_class = CategoriaCursoForm
    template_name = 'gestion/categoria_form.html'
    success_url = reverse_lazy('categoria_list')    

class CategoriaUpdateView(LoginRequiredMixin, AdministradorRolRequiredMixin, UpdateView):
    model = CategoriaCurso
    form_class = CategoriaCursoForm
    template_name = 'gestion/categoria_form.html'
    success_url = reverse_lazy('categoria_list')
    
class CategoriaDeleteView(LoginRequiredMixin, AdministradorRolRequiredMixin, DeleteView):
    model = CategoriaCurso
    template_name = 'gestion/categoria_confirm_delete.html'
    success_url = reverse_lazy('categoria_list')

class GestionAdminView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'gestion/gestion_admin.html'

    def test_func(self):
        return self.request.user.is_superuser

class CategoriaListView(LoginRequiredMixin, AdministradorRolRequiredMixin, ListView):
    model = CategoriaCurso
    template_name = 'gestion/categoria_list.html'
    context_object_name = 'categorias'
