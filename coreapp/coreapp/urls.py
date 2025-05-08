from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 1) Login en la raíz
    path(
        '',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login'
    ),

    # 2) Logout por POST, redirige a '/'
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='/'),
        name='logout'
    ),

    # 3) Admin de Django
    path('admin/', admin.site.urls),

    # 4) Resto de URLs de auth (p.ej. cambio de contraseña)
    path('accounts/', include('django.contrib.auth.urls')),

    # 5) Rutas de tu app de gestión
    path('', include('gestion.urls')),
]
