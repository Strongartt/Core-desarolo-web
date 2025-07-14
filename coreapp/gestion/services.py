# gestion/services.py

from .models import Inscripcion, Curso
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from django.shortcuts import get_object_or_404


# ----- STRATEGY -----

class MembresiaStrategy:
    def validar(self, user, curso, plan):
        raise NotImplementedError("Debes implementar este método")


class GratuitaStrategy(MembresiaStrategy):
    def validar(self, user, curso, plan):
        # La gratuita solo permite cursos gratis
        if curso.precio > 0:
            return False, f"Tu plan '{plan.nombre}' solo permite cursos gratuitos."
        return True, ""


class BasicaStrategy(MembresiaStrategy):
    def validar(self, user, curso, plan):
        if curso.precio > plan.limite_precio_curso:
            return False, f"Tu plan '{plan.nombre}' solo permite cursos hasta ${plan.limite_precio_curso}."
        return True, ""


class PremiumStrategy(MembresiaStrategy):
    def validar(self, user, curso, plan):
        # Premium permite todos los cursos
        return True, ""


# ----- FACTORY -----

def get_strategy_for_plan(plan):
    nombre = plan.nombre.lower()
    if nombre == "gratuita":
        return GratuitaStrategy()
    elif nombre == "básica":
        return BasicaStrategy()
    elif nombre == "premium":
        return PremiumStrategy()
    else:
        # Por defecto, tratamos como gratuita si el plan no se reconoce
        return GratuitaStrategy()


# ----- FUNCIÓN PRINCIPAL DEL SERVICIO -----

def procesar_inscripcion(request, curso, usuario):
    perfil = usuario.perfil

    # Evitar duplicados
    if Inscripcion.objects.filter(curso=curso, usuario=usuario).exists():
        messages.error(request, "Ya estás inscrito en este curso.")
        return redirect('curso_list')

    # Validar cupo
    if Inscripcion.objects.filter(curso=curso).count() >= curso.cupo:
        messages.error(request, "El curso ya no tiene cupos disponibles.")
        return redirect('curso_list')

    # Obtener plan actual del usuario
    plan = perfil.get_plan_actual()

    # Obtener la estrategia adecuada según el plan
    estrategia = get_strategy_for_plan(plan)
    es_valido, mensaje = estrategia.validar(usuario, curso, plan)

    if not es_valido:
        messages.error(request, mensaje)
        return redirect('curso_list')

    # Crear inscripción
    Inscripcion.objects.create(curso=curso, usuario=usuario, estado="INSCRITO")
    messages.success(request, "Te has inscrito correctamente.")
    return redirect('curso_list')




def actualizar_notas_asistencia(request, curso_id, perfil):
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
            pass  # Puedes agregar mensajes de error si quieres

    messages.success(request, "Notas y asistencia actualizadas.")
    return redirect('editar_notas_asistencia', pk=curso.id)