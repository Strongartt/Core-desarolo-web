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
]
