from django.urls import path
from .views import (
    UsuarioListView, 
    UsuarioCreateView, 
    UsuarioUpdateView,
    CursoListView,
    CursoCreateView,
    CursoUpdateView,
    InscripcionListView,
    InscripcionCreateView,
    InscripcionUpdateView,
    SignUpView,
    DashboardView,
    ReporteDocenteView,
    ReporteEstudianteView,
    MisCursosView,
    DetalleCursoDocenteView,
    InscribirseView,
    SolicitarBajaView,
    GestionSolicitudesBajaView,
    AprobarBajaView,
    RechazarBajaView,
    EditarNotasAsistenciaView,
    CategoriaUpdateView,
    CategoriaDeleteView,
    GestionAdminView,
    CategoriaListView,
    CategoriaCreateView,
    SeleccionarMembresiaView,
    EditarMembresiaEstudianteView,
    ReporteIngresosCursoView,
    ReporteIngresosCategoriaView,
    ReporteGananciasMensualesView,
    ReporteTopEstudiantesPorCategoriaView,

)

urlpatterns = [
  
    # CRUD Usuarios (basado en User + Perfil)
    path('usuarios/', UsuarioListView.as_view(), name='usuario_list'),
    path('usuarios/nuevo/', UsuarioCreateView.as_view(), name='usuario_new'),
    path('usuarios/<int:pk>/editar/', UsuarioUpdateView.as_view(), name='usuario_edit'),

    # CRUD Cursos
    path('cursos/', CursoListView.as_view(), name='curso_list'),
    path('cursos/nuevo/', CursoCreateView.as_view(), name='curso_new'),
    path('cursos/<int:pk>/editar/', CursoUpdateView.as_view(), name='curso_edit'),

    # CRUD Inscripciones
    path('inscripciones/', InscripcionListView.as_view(), name='inscripcion_list'),
    path('inscripciones/nuevo/', InscripcionCreateView.as_view(), name='inscripcion_new'),
    path('inscripciones/<int:pk>/editar/', InscripcionUpdateView.as_view(), name='inscripcion_edit'),

    # Signup
    path('signup/', SignUpView.as_view(), name='signup'),

    # Dashboard y reportes
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('reporte/docente/', ReporteDocenteView.as_view(), name='reporte_docente'),
    path('reporte/estudiante/', ReporteEstudianteView.as_view(), name='reporte_estudiante'),
    
    path('mis-cursos/', MisCursosView.as_view(), name='mis_cursos'),
    
    path('reporte-curso/<int:pk>/', DetalleCursoDocenteView.as_view(), name='reporte_docente_detalle'),
    
    path('cursos/<int:curso_id>/inscribirse/', InscribirseView.as_view(), name='inscribirse'),

    path('solicitar-baja/<int:pk>/', SolicitarBajaView.as_view(), name='solicitar_baja'),
    
    path('solicitudes-baja/', GestionSolicitudesBajaView.as_view(), name='solicitudes_baja'),
    path('solicitudes-baja/aprobar/<int:pk>/', AprobarBajaView.as_view(), name='aprobar_baja'),
    path('solicitudes-baja/rechazar/<int:pk>/', RechazarBajaView.as_view(), name='rechazar_baja'),

    path('editar-notas-asistencia/<int:pk>/', EditarNotasAsistenciaView.as_view(), name='editar_notas_asistencia'),
    
    path('categorias/editar/<int:pk>/', CategoriaUpdateView.as_view(), name='categoria_edit'),
    path('categorias/eliminar/<int:pk>/', CategoriaDeleteView.as_view(), name='categoria_delete'),
    path('categorias/nueva/', CategoriaCreateView.as_view(), name='categoria_create'),
    path('categorias/', CategoriaListView.as_view(), name='categoria_list'),

    
    path('admin-panel/', GestionAdminView.as_view(), name='gestion_admin'),
    
    path('seleccionar-membresia/', SeleccionarMembresiaView.as_view(), name='seleccionar_membresia'),

    path('usuarios/<int:pk>/editar-membresia/', EditarMembresiaEstudianteView.as_view(), name='editar_membresia_estudiante'),

    path('mis-cursos/<int:pk>/editar-notas-asistencia/', EditarNotasAsistenciaView.as_view(), name='editar_notas_asistencia'),

    path('reporte/ingresos-curso/', ReporteIngresosCursoView.as_view(), name='reporte_ingresos_curso'),

    path('reporte/ingresos-categoria/', ReporteIngresosCategoriaView.as_view(), name='reporte_ingresos_categoria'),

    path('reporte/ganancias-mensuales/', ReporteGananciasMensualesView.as_view(), name='reporte_ganancias_mensuales'),

    path('reporte/top-estudiantes/', ReporteTopEstudiantesPorCategoriaView.as_view(), name='reporte_top_estudiantes_categoria'),

]

