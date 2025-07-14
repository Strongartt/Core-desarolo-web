from rest_framework import serializers
from ..models import Curso

class CursoSerializer(serializers.ModelSerializer):
    cupos_disponibles = serializers.ReadOnlyField()
    membresia_requerida = serializers.ReadOnlyField()
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)

    class Meta:
        model = Curso
        fields = [
            'id',
            'nombre',
            'modalidad',
            'fecha_inicio',
            'fecha_fin',
            'precio',
            'cupos_disponibles',
            'membresia_requerida',
            'categoria',
            'categoria_nombre',
            'docente',
        ]
