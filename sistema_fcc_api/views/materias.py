from django.shortcuts import render
from django.db.models import *
from django.db import transaction
from sistema_fcc_api.serializers import *
from sistema_fcc_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.utils.html import strip_tags
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
import json

class MateriasAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        materias = Materias.objects.all().order_by("id")
        materias = MateriaSerializer(materias, many=True).data
        # Convertir los valores de dias_json de nuevo a un array
        for materia in materias:
            materia["dias_json"] = json.loads(materia["dias_json"])

        return Response(materias, 200)

class MateriasView(generics.CreateAPIView):
    def get(self, request, *args, **kwargs):
        materia = get_object_or_404(Materias, id=request.GET.get("id"))
        materia = MateriaSerializer(materia, many=False).data
        materia["dias_json"] = json.loads(materia["dias_json"])
        return Response(materia, 200)
    
    def post(self, request, *args, **kwargs):
        serializer = MateriaSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data

            # Validar si ya existe una materia con el mismo NRC
            existing_materia = Materias.objects.filter(nrc=validated_data['nrc']).first()
            if existing_materia:
                return Response({"message": "Materia with NRC {} already exists.".format(validated_data['nrc'])}, status=400)

            # Crear la instancia de Materia con todos los campos
            materia = Materias.objects.create(
                nrc=validated_data['nrc'],
                nombre=validated_data['nombre'],
                seccion=validated_data['seccion'],
                hora_inicio=validated_data['hora_inicio'],
                hora_fin=validated_data['hora_fin'],
                salon=validated_data['salon'],
                programa=validated_data['programa'],
                dias_json=json.dumps(validated_data['dias_json']),
            )

            return Response({"maestro_created_id": materia.id}, 201)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MateriasViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self, request, *args, **kwargs):
        materia = get_object_or_404(Materias, id=request.data["id"])
        materia.nrc = request.data["nrc"]
        materia.nombre = request.data["nombre"]
        materia.seccion = request.data["seccion"]
        materia.hora_inicio = request.data["hora_inicio"]
        materia.hora_fin = request.data["hora_fin"]
        materia.salon = request.data["salon"]
        materia.programa = request.data["programa"]
        materia.dias_json = json.dumps(request.data["dias_json"])
        materia.save()
        return Response(MateriaSerializer(materia, many=False).data, 200)
    
    def delete(self, request, *args, **kwargs):
        materia = get_object_or_404(Materias, id=request.GET.get("id"))
        try:
            materia.delete()
            return Response({"details":"Materia Eliminada"}, 200)
        except Exception as e:
            return Response({"details":"Error al eliminar la Materia"}, 400)
