# gestion/views.py
from urllib import request
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, TemplateView, DeleteView
from .models import Curso, Inscripcion, CategoriaCurso, Perfil, Trimestre
from .forms import CursoForm, InscripcionForm, SignUpForm,UserPerfilForm, CategoriaCursoForm, SeleccionarMembresiaForm, ActualizarMembresiaUsuarioForm
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum, F, FloatField, ExpressionWrapper
from django.db.models.functions import TruncMonth
from .services.inscripcion_service import procesar_inscripcion, actualizar_notas_asistencia
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from collections import Counter
from datetime import date




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
        return user.is_superuser or (
            user.is_authenticated and 
            hasattr(user, 'perfil') and 
            user.perfil.rol.codigo in ['ADMIN', 'DOC']
        )


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
        usuario = request.user
        return procesar_inscripcion(request, curso, usuario)


# —— Registro de nuevos usuarios “normales” ——
class SignUpView(CreateView):
    form_class    = SignUpForm
    template_name = 'registration/signup.html'
    success_url   = reverse_lazy('login')


# —— Reportes según rol ——


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
        if user.is_superuser:
            return True  
        return hasattr(user, 'perfil') and user.perfil.rol.codigo == 'DOC'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        hoy = timezone.now().date()

        # Si es superusuario, ver todos los cursos
        if user.is_superuser:
            cursos_docente = Curso.objects.all()
        else:
            perfil = user.perfil
            cursos_docente = Curso.objects.filter(docente=perfil)

        datos = []
        for curso in cursos_docente:
            inscripciones = Inscripcion.objects.filter(curso=curso)
            total = inscripciones.count()

            if total > 0:
                notas = [i.nota_final for i in inscripciones if i.nota_final is not None]
                promedio_nota = round(sum(notas) / len(notas), 2) if notas else "—"

                asistencias = [i.asistencia_total for i in inscripciones if i.asistencia_total is not None]
                promedio_asistencia = round(sum(asistencias) / len(asistencias), 2) if asistencias else "—"
            else:
                promedio_nota = "—"
                promedio_asistencia = "—"

            datos.append({
                'nombre': curso.nombre,
                'categoria': curso.categoria.nombre if curso.categoria else "Con categoría",
                'modalidad': curso.modalidad,
                'fecha_inicio': curso.fecha_inicio,
                'fecha_fin': curso.fecha_fin,
                'inscritos': total,
                'promedio_nota': promedio_nota,
                'promedio_asistencia': promedio_asistencia,
            })

        ctx['datos'] = datos
        ctx['today'] = hoy
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
            return reverse_lazy('dashboard')
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
        return actualizar_notas_asistencia(request, curso_id, perfil)
    
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
    
class SeleccionarMembresiaView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Perfil
    form_class = SeleccionarMembresiaForm
    template_name = 'gestion/seleccionar_membresia.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        return self.request.user.perfil

    def form_valid(self, form):
        perfil = form.save(commit=False)
        plan = form.cleaned_data['plan_membresia']

        hoy = timezone.now().date()
        perfil.plan_membresia = plan
        perfil.fecha_inicio_membresia = hoy
        perfil.fecha_fin_membresia = hoy + timedelta(days=30)

        perfil.save()
        messages.success(self.request, f"Tu membresawaía '{plan.nombre}' está activa hasta el {perfil.fecha_fin_membresia}.")
        return super().form_valid(form)

    def test_func(self):
        return hasattr(self.request.user, 'perfil') and self.request.user.perfil.rol.codigo == 'EST'
    
class EditarMembresiaEstudianteView(LoginRequiredMixin, AdministradorRolRequiredMixin, UpdateView):
    model = Perfil
    form_class = ActualizarMembresiaUsuarioForm
    template_name = 'gestion/editar_membresia_estudiante.html'
    success_url = reverse_lazy('usuario_list')

    def get_queryset(self):
        return Perfil.objects.filter(rol__codigo='EST')
    
class ReporteIngresosCursoView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'gestion/reporte_ingresos_curso.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cursos = Curso.objects.all()

        datos = []
        for curso in cursos:
            inscritos = curso.inscripcion_set.count()
            precio = curso.precio
            total = round(inscritos * precio, 2)

            datos.append({
                'nombre': curso.nombre,
                'inscritos': inscritos,
                'precio': precio,
                'total': total,
            })

        ctx['datos'] = datos
        return ctx
    
class ReporteIngresosCategoriaView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'gestion/reporte_ingresos_categoria.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        categorias = CategoriaCurso.objects.all()

        datos = []
        for categoria in categorias:
            cursos = Curso.objects.filter(categoria=categoria)
            total_cursos = cursos.count()

            total_inscritos = 0
            total_ingresos = 0.0

            for curso in cursos:
                inscritos = curso.inscripcion_set.count()
                ingresos = inscritos * float(curso.precio)
                total_inscritos += inscritos
                total_ingresos += ingresos

            datos.append({
                'nombre': categoria.nombre,
                'total_cursos': total_cursos,
                'total_inscritos': total_inscritos,
                'total_ingresos': round(total_ingresos, 2),
            })

        ctx['datos'] = datos
        return ctx


    
class ReporteTopEstudiantesPorCategoriaView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'gestion/reporte_top_estudiantes_categoria.html'

    def test_func(self):
        return self.request.user.is_superuser  # Solo admins pueden acceder

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        categorias = CategoriaCurso.objects.all()
        reporte = []

        for categoria in categorias:
            cursos = Curso.objects.filter(categoria=categoria)
            inscripciones = Inscripcion.objects.filter(curso__in=cursos, nota_final__isnull=False).select_related('usuario')
            top = sorted(inscripciones, key=lambda i: i.nota_final, reverse=True)[:3]
            reporte.append({
                'categoria': categoria.nombre,
                'top_estudiantes': [{
                    'nombre': f'{i.usuario.first_name} {i.usuario.last_name}',
                    'curso': i.curso.nombre,
                    'nota': i.nota_final
                } for i in top]
            })

        ctx['reporte'] = reporte
        return ctx

@login_required
def vista_filtrado_cursos_api(request):
    categorias = CategoriaCurso.objects.all()
    return render(request, 'gestion/cursos_api_view.html', {'categorias': categorias})



class ReporteInscripcionesPorTrimestreView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'gestion/reporte_inscripciones_trimestre.html'

    def test_func(self):
        return self.request.user.is_superuser  

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

    
        categoria_id = self.request.GET.get('categoria')
        modalidad = self.request.GET.get('modalidad')
        membresia = self.request.GET.get('membresia')

        cursos = Curso.objects.all()

        if categoria_id:
            cursos = cursos.filter(categoria_id=categoria_id)
        if modalidad:
            cursos = cursos.filter(modalidad=modalidad)
        if membresia:
            cursos = [c for c in cursos if c.membresia_requerida == membresia]

        anio_actual = date.today().year
        anio_anterior = anio_actual - 1
        trimestres = Trimestre.objects.filter(fecha_inicio__year=anio_anterior).order_by('fecha_inicio')

        resultados = []

        for trimestre in trimestres:
            cursos_en_trimestre = [c for c in cursos if c.trimestre_id == trimestre.id]
            inscripciones = Inscripcion.objects.filter(curso__in=cursos_en_trimestre).count()
            resultados.append({
                'nombre': trimestre.nombre,
                'inscripciones': inscripciones
            })

        # Proyección solo con trimestres que tienen inscripciones
        trimestres_con_inscripciones = [r for r in resultados if r['inscripciones'] > 0]
        ultimos = trimestres_con_inscripciones[-3:] if len(trimestres_con_inscripciones) >= 3 else trimestres_con_inscripciones
        proyeccion = round(sum(r['inscripciones'] for r in ultimos) / len(ultimos)) if ultimos else 0

        # Recomendación inteligente
        inscripciones_validas = Inscripcion.objects.select_related('curso', 'curso__categoria').filter(curso__in=cursos)
        categoria_counter = Counter()
        modalidad_counter = Counter()

        for i in inscripciones_validas:
            if i.curso.categoria:
                categoria_counter[i.curso.categoria.nombre] += 1
            modalidad_counter[i.curso.modalidad] += 1

        categoria_top = categoria_counter.most_common(1)[0][0] if categoria_counter else "desconocida"
        modalidad_top = modalidad_counter.most_common(1)[0][0] if modalidad_counter else "desconocida"

        if trimestres_con_inscripciones:
            trimestre_max = max(trimestres_con_inscripciones, key=lambda r: r['inscripciones'])
            index_trimestre = resultados.index(trimestre_max)
            ordinales = ["primer trimestre", "segundo trimestre", "tercer trimestre"]
            nombre_trimestre_recomendado = ordinales[index_trimestre] if index_trimestre < len(ordinales) else "trimestre más activo"

            recomendacion = (
                f"Se recomienda priorizar la creación de cursos en el {nombre_trimestre_recomendado}, "
                f"preferentemente de la categoría '{categoria_top}' y en modalidad '{modalidad_top}', "
                f"que han mostrado mayor interés por parte de los estudiantes."
            )
        else:
            recomendacion = "No hay suficientes datos para generar una recomendación."

        ctx['trimestres'] = trimestres
        ctx['cursos'] = cursos
        ctx['resultados'] = resultados
        ctx['proyeccion'] = proyeccion
        ctx['categorias'] = CategoriaCurso.objects.all()
        ctx['filtros'] = {
            'categoria': categoria_id,
            'modalidad': modalidad,
            'membresia': membresia
        }
        ctx['recomendacion'] = recomendacion

        return ctx

class ReporteGananciasMensualesView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'gestion/reporte_ganancias_mensuales.html'



    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        datos = (
            Inscripcion.objects
            .annotate(mes=TruncMonth('fecha_inscripcion'))
            .values('mes')
            .annotate(
                total_inscripciones=Count('id'),
                total_ganado=Sum(ExpressionWrapper(
                    F('curso__precio'),
                    output_field=FloatField()
                ))
            )
            .order_by('mes')
        )

        for d in datos:
            d['total_ganado'] = round(d['total_ganado'] or 0, 2)

        ctx['datos'] = datos
        return ctx