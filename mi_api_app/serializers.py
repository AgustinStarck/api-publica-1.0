# mi_api_app/serializers.py
from rest_framework import serializers
from .models import noticias

class NoticiasSerializer(serializers.ModelSerializer):
    class Meta:
        model = noticias
        fields = ['id', 'titulo', 'descripcion', 'site_icon', 'link', 'fecha']
        read_only_fields = ['id', 'fecha']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Formatear la fecha para que sea más legible
        representation['fecha'] = instance.fecha.strftime('%Y-%m-%d %H:%M:%S')
        return representation