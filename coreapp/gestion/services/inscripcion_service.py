from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from ..models import Inscripcion, Curso
from .estrategia_service import get_strategy_for_plan

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

    plan = perfil.get_plan_actual()
    estrategia = get_strategy_for_plan(plan)
    es_valido, mensaje = estrategia.validar(usuario, curso, plan)

    if not es_valido:
        messages.error(request, mensaje)
        return redirect('curso_list')

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
            pass

    messages.success(request, "Notas y asistencia actualizadas.")
    return redirect('editar_notas_asistencia', pk=curso.id)
