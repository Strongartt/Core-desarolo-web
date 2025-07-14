from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from ..models import Curso
from ..serializers.curso_serializer import CursoSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def cursos_api(request):
    if request.method == 'GET':
        cursos = Curso.objects.all()

        # Filtros desde query params
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
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
