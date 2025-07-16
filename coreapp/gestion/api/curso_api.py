from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from ..models import Curso, Trimestre
from ..serializers.curso_serializer import CursoSerializer
from datetime import datetime

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def cursos_api(request):
    if request.method == 'GET':
        cursos = Curso.objects.all()

        categoria_id = request.GET.get('categoria')
        modalidad = request.GET.get('modalidad')
        membresia = request.GET.get('membresia')

        if categoria_id:
            cursos = cursos.filter(categoria__id=categoria_id)
        if modalidad:
            cursos = cursos.filter(modalidad__iexact=modalidad)
        if membresia:
            cursos = [curso for curso in cursos if curso.membresia_requerida == membresia]

        serializer = CursoSerializer(cursos, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CursoSerializer(data=request.data)
        if serializer.is_valid():
            curso = serializer.save()

            # Asignar trimestre automáticamente según fecha_inicio
            fecha_str = request.data.get('fecha_inicio')
            if fecha_str:
                fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                trimestre = Trimestre.objects.filter(
                    fecha_inicio__lte=fecha_obj,
                    fecha_fin__gte=fecha_obj
                ).first()
                if trimestre:
                    curso.trimestre = trimestre
                    curso.save()

            return Response(CursoSerializer(curso).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)