from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Inicio va al login de la app
    path('', RedirectView.as_view(url='accounts/login/', permanent=False)),
    
    # Panel de Django
    path('admin/', admin.site.urls),

    # Login/Logout etc. de la app
    path('accounts/', include('django.contrib.auth.urls')),

    # Tus vistas de negocio (usuarios, cursos, inscripciones)
    path('', include('gestion.urls')),
]
