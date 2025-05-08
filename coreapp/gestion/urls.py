# gestion/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Usuarios
    path('usuarios/',            views.UsuarioListView.as_view(),   name='usuario_list'),
    path('usuarios/nuevo/',      views.UsuarioCreateView.as_view(), name='usuario_new'),
    path('usuarios/<int:pk>/editar/', views.UsuarioUpdateView.as_view(), name='usuario_edit'),

    # Cursos
    path('cursos/',              views.CursoListView.as_view(),     name='curso_list'),
    path('cursos/nuevo/',        views.CursoCreateView.as_view(),   name='curso_new'),
    path('cursos/<int:pk>/editar/', views.CursoUpdateView.as_view(),   name='curso_edit'),

    # Inscripciones
    path('inscripciones/',       views.InscripcionListView.as_view(),   name='inscripcion_list'),
    path('inscripciones/nuevo/', views.InscripcionCreateView.as_view(), name='inscripcion_new'),
    path('inscripciones/<int:pk>/editar/', views.InscripcionUpdateView.as_view(), name='inscripcion_edit'),
]
