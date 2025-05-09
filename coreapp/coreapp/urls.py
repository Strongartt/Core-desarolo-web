# coreapp/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from gestion.views import SignUpView

urlpatterns = [
    # Al entrar en “/” redirijo al login
    path(
        '',
        RedirectView.as_view(url='accounts/login/', permanent=False),
    ),

    # Panel de administración de Django
    path('admin/', admin.site.urls),

    # Página para que usuarios “normales” puedan registrarse
    path('signup/', SignUpView.as_view(), name='signup'),

    # Login, logout, password_change, etc.
    path('accounts/', include('django.contrib.auth.urls')),

    # Ya todo lo relativo a usuarios, cursos e inscripciones
    path('', include('gestion.urls')),
]
