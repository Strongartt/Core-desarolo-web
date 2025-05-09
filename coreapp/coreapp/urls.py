from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from gestion.views import SignUpView, CustomLoginView
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

urlpatterns = [
    # “/” → login
    path('', RedirectView.as_view(url='accounts/login/', permanent=False)),

    # admin de Django
    path('admin/', admin.site.urls),

    # signup para usuarios normales
    path('signup/', SignUpView.as_view(), name='signup'),

    # LOGIN personalizado
    path('accounts/login/',
         CustomLoginView.as_view(),
         name='login'),

    # LOGOUT básico
    path('accounts/logout/',
         LogoutView.as_view(next_page=reverse_lazy('login')),
         name='logout'),

    # resto de tus urls de negocio
    path('', include('gestion.urls')),
]
