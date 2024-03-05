from django.contrib.auth import authenticate
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.http import JsonResponse
from datetime import datetime, timedelta

from .models import CustomUser
from .serializers import CustomUserSerializer

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Usar AllowAny solo para la acción 'create'
        if self.action == 'create':
            self.permission_classes = [AllowAny]

        return super().get_permissions()

    def perform_create(self, serializer):
        # Guarda el nuevo usuario
        user = serializer.save()

        # Genera un token para el usuario
        refresh = RefreshToken.for_user(user)

        # Agrega el token a la respuesta
        response_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()




class ObtainTokenView(APIView):
    def post(self, request):
        dni = request.data.get('dni')
        password = request.data.get('password')

        user = authenticate(request, dni=dni, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'id': user.id,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCurrentUser(request):
    user = request.user

    # Utiliza tu propio serializador para CustomUser
    user_serializer = CustomUserSerializer(user)

    user_data = {
        'id': user.id,
        'dni': user.dni,
        'apel_nomb': user.apel_nomb,
        'tipo_usuarioapp': user.tipo_usuarioapp,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'date_joined': user.date_joined,
        # Agrega otros campos según tu modelo de usuario
    }

    return JsonResponse(user_data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_usuario(request, dni):
    try:
        usuario = CustomUser.objects.get(dni=dni)
    except CustomUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    usuario.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actualizar_usuario(request, dni):
    try:
        usuario = CustomUser.objects.get(dni=dni)
    except CustomUser.DoesNotExist:
        return Response({'error': 'El usuario no existe'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        # Elimina la contraseña de los datos de la solicitud si está presente
        if 'password' in request.data:
            del request.data['password']

        serializer = CustomUserSerializer(usuario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from .models import CustomUser
from .serializers import CustomUserSerializer

class UserByDniAPIView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        dni = self.kwargs.get('dni')
        try:
            user = CustomUser.objects.get(dni=dni)
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Empresa
from .serializers import EmpresaSerializer

class EmpresaListCreateAPIView(APIView):
    def get(self, request):
        empresas = Empresa.objects.all()
        serializer = EmpresaSerializer(empresas, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EmpresaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import generics
from .models import TipoEnvio
from .serializers import TipoEnvioSerializer

class TipoEnvioListCreate(generics.ListCreateAPIView):
    queryset = TipoEnvio.objects.all()
    serializer_class = TipoEnvioSerializer


from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Responsable
from .serializers import ResponsableSerializer

@api_view(['GET', 'POST'])
def responsable_list(request):
    if request.method == 'GET':
        responsables = Responsable.objects.all()
        serializer = ResponsableSerializer(responsables, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ResponsableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def responsable_detail(request, pk):
    try:
        responsable = Responsable.objects.get(pk=pk)
    except Responsable.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ResponsableSerializer(responsable)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ResponsableSerializer(responsable, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        responsable.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Planilla
from .serializers import PlanillaSerializer

class PlanillaAPIView(APIView):
    def get(self, request):
        planillas = Planilla.objects.all()
        serializer = PlanillaSerializer(planillas, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PlanillaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        planilla = Planilla.objects.get(idplanilla=id)
        serializer = PlanillaSerializer(planilla, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        planilla = Planilla.objects.get(idplanilla=id)
        planilla.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Emisor
from .serializers import EmisorSerializer

class EmisorListCreateAPIView(APIView):
    def get(self, request):
        emisor = Emisor.objects.all()
        serializer = EmisorSerializer(emisor, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EmisorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Especie
from .serializers import EspecieSerializer

class EspecieListCreateAPIView(APIView):
    def get(self, request):
        especie = Especie.objects.all()
        serializer = EspecieSerializer(especie, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EspecieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Turno
from .serializers import TurnoSerializer

class TurnoListCreateAPIView(APIView):
    def get(self, request):
        turno = Turno.objects.all()
        serializer = TurnoSerializer(turno, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TurnoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Consumidor
from .serializers import ConsumidorSerializer

class ConsumidorListCreateAPIView(APIView):
    def get(self, request):
        consumidor = Consumidor.objects.all()
        serializer = ConsumidorSerializer(consumidor, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ConsumidorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#----------------------------------------------
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .models import Registro
from .serializers import RegistroSerializer

class DiaAPIView(APIView):
    def post(self, request):
        # Verificar si hay un día abierto
        if Registro.objects.filter(estado='Abierto').exists():
            return Response({"message": "Ya hay un día abierto."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener la fecha y hora actual en formato YYYYMMdd y HH:MM:SS
        fecha_actual = datetime.now().strftime('%Y%m%d')
        hora_actual = datetime.now().strftime('%H:%M:%S')

        # Crear el registro para abrir el día
        serializer = RegistroSerializer(data={
            'FechaAbierto': fecha_actual,
            'HoraAbierto': hora_actual,
            'estado': 'Abierto'
        })

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        # Obtener la fecha y hora actual en formato YYYYMMdd y HH:MM:SS
        fecha_actual = datetime.now().strftime('%Y%m%d')
        hora_actual = datetime.now().strftime('%H:%M:%S')

        # Verificar si hay un día abierto
        registro_abierto = Registro.objects.filter(estado='Abierto').first()
        if not registro_abierto:
            return Response({"error": "No hay día abierto para cerrar"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Actualizar el registro para cerrar el día
        registro_abierto.FechaCerrado = fecha_actual
        registro_abierto.HoraCerrado = hora_actual
        registro_abierto.estado = 'Cerrado'
        registro_abierto.save()

        serializer = RegistroSerializer(registro_abierto)
        return Response(serializer.data)

# ------------------------------------------------------------------------------------
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import transaction
from .models import ImportarAsistencia, ImportarAsistenciaDetalle, Registro
from .serializers import ImportarAsistenciaSerializer, ImportarAsistenciaDetalleSerializer

from datetime import datetime

@api_view(['POST'])
def importar_asistencia_Post(request):
    if request.method == 'POST':
        try:
            # Obtener el último estado del registro
            ultimo_registro = Registro.objects.latest('FechaAbierto')

            # Verificar si el último estado del registro está abierto
            if ultimo_registro.estado != 'Abierto':
                return Response({"error": "No hay registro abierto para importar asistencia."},
                                status=status.HTTP_400_BAD_REQUEST)

            idcodigogeneral = request.data.get('idcodigogeneral')

            # Verificar si el trabajador ya fue importado en este registro abierto
            existing_worker = ImportarAsistenciaDetalle.objects.filter(
                idcodigogeneral=idcodigogeneral,
                importar_asistencia__id=ultimo_registro.pk
            )
            if existing_worker.exists():
                return Response({"error": "Este trabajador ya ha sido importado en este registro abierto."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Crear la instancia de ImportarAsistencia
            importar_asistencia_data = {
                'idempresa': request.data.get('idempresa'),
                'tipo_envio': request.data.get('tipo_envio'),
                'idresponsable': request.data.get('idresponsable'),
                'idplanilla': request.data.get('idplanilla'),
                'idemisor': request.data.get('idemisor'),
                'idturno': request.data.get('idturno'),
                'fecha': ultimo_registro.FechaAbierto,
                'idsucursal': request.data.get('idsucursal'),
                'idespecie': request.data.get('idespecie')  # Asegúrate de agregar el campo idespecie
            }
            importar_asistencia_serializer = ImportarAsistenciaSerializer(data=importar_asistencia_data)
            importar_asistencia_serializer.is_valid(raise_exception=True)
            importar_asistencia = importar_asistencia_serializer.save()

            # Crear las instancias de ImportarAsistenciaDetalle
            detalle_data = request.data.get('detalle', [])
            for detalle_item in detalle_data:
                detalle_item['importar_asistencia'] = importar_asistencia.pk
                detalle_serializer = ImportarAsistenciaDetalleSerializer(data=detalle_item)
                detalle_serializer.is_valid(raise_exception=True)
                detalle_serializer.save()

            return Response(importar_asistencia_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



#------------------------------------------------------------------------------
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ImportarAsistenciaDetalle, Registro
from .serializers import AsistenciaSerializer, AsistenciaDetalleSerializer
from datetime import datetime

class MerluzasistenciaUpdateByCodigoGeneralView(APIView):
    def put(self, request, idcodigogeneral, idlabor):
        try:
            # Obtener la fecha actual
            fecha_actual = datetime.now().strftime("%Y%m%d")
            
            # Verificar si hay un día abierto
            registro_abierto = Registro.objects.filter(estado='Abierto').order_by('-FechaAbierto').first()
            if not registro_abierto:
                return Response({"error": "No hay día abierto para actualizar la asistencia."}, status=status.HTTP_400_BAD_REQUEST)
                
            # Buscar el registro de ImportarAsistenciaDetalle por idcodigogeneral e idlabor en el día abierto más cercano
            asistencia_detalle = ImportarAsistenciaDetalle.objects.filter(
                idcodigogeneral=idcodigogeneral, 
                idlabor=idlabor, 
                importar_asistencia__fecha=registro_abierto.FechaAbierto
            ).first()
            
            # Verificar si se encontró un registro para actualizar
            if not asistencia_detalle:
                return Response({"error": "No se encontró el registro de ImportarAsistenciaDetalle para actualizar en el día abierto más cercano."}, status=status.HTTP_404_NOT_FOUND)
            
            # Actualizar la cantidad si existe en los datos de la solicitud
            if 'cantidad' in request.data:
                asistencia_detalle.cantidad = request.data['cantidad']
                asistencia_detalle.save()
                
                # Obtener la asistencia actualizada
                asistencia = asistencia_detalle.importar_asistencia
                
                # Serializar la asistencia y sus detalles
                serializer = AsistenciaSerializer(asistencia)
                data = serializer.data
                detalles = AsistenciaDetalleSerializer(asistencia.detalle.all(), many=True).data
                data['detalle'] = detalles
                
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "La cantidad no se proporcionó en los datos de la solicitud"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def importar_asistencia_list(request):
    try:
        importar_asistencias = ImportarAsistencia.objects.all()
        data = []
        for importar_asistencia in importar_asistencias:
            serializer = ImportarAsistenciaSerializer(importar_asistencia)
            detalle_serializer = ImportarAsistenciaDetalleSerializer(importar_asistencia.detalle.all(), many=True)
            importar_asistencia_data = serializer.data
            importar_asistencia_data['detalle'] = detalle_serializer.data
            data.append(importar_asistencia_data)
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
# ------------------------------------------------------------------------------------
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ImportarAsistencia, Registro
from .serializers import AsistenciaSerializer, AsistenciaDetalleSerializer
from datetime import datetime
from datetime import timedelta
from django.db.models import Q


class POTAAsistenciaUpdateByCodigoGeneralView(APIView):
    def get(self, request, codigo_general=None):
        try:
            # Verificar si el día está abierto
            registro_abierto = Registro.objects.filter(estado='Abierto').first()
            if not registro_abierto:
                return Response({"error": "El día está cerrado, no se pueden obtener datos de asistencia."},
                                status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener la fecha de cierre del registro abierto
            fecha_cierre = registro_abierto.FechaCerrado
            
            # Calcular la fecha mínima y máxima para el rango de búsqueda
            fecha_inicio = registro_abierto.FechaAbierto
            fecha_fin = fecha_cierre if fecha_cierre else datetime.now().strftime('%Y%m%d')
            
            # Filtrar los trabajadores importados en el rango de fechas
            importar_asistencias = ImportarAsistencia.objects.filter(
                fecha__range=(fecha_inicio, fecha_fin)
            )
            
            # Serializar los datos de asistencia y sus detalles
            data = []
            for importar_asistencia in importar_asistencias:
                asistencia_data = ImportarAsistenciaSerializer(importar_asistencia).data
                detalles = ImportarAsistenciaDetalleSerializer(importar_asistencia.detalle.all(), many=True).data
                asistencia_data['detalle'] = detalles
                data.append(asistencia_data)
            
            return Response(data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, idcodigogeneral):
        try:
            # Verificar si el día está abierto
            registro_abierto = Registro.objects.filter(estado='Abierto').first()
            if not registro_abierto:
                return Response({"error": "El día está cerrado, no se pueden actualizar los datos de asistencia."},
                                status=status.HTTP_400_BAD_REQUEST)
            
            # Filtrar el ImportarAsistenciaDetalle basado en la fecha de apertura del registro más reciente y el idcodigogeneral
            asistencia_detalle = ImportarAsistenciaDetalle.objects.filter(
                Q(importar_asistencia__fecha__gte=registro_abierto.FechaAbierto) &
                Q(idcodigogeneral=idcodigogeneral)
            ).first()
            
            # Verificar si se encontró el registro de asistencia
            if not asistencia_detalle:
                return Response({"error": "No se encontró el registro de ImportarAsistenciaDetalle con idcodigogeneral proporcionado o no pertenece al día abierto actual."},
                                status=status.HTTP_404_NOT_FOUND)
            
            # Actualizar la cantidad si existe en los datos de la solicitud
            if 'cantidad' in request.data:
                asistencia_detalle.cantidad = request.data['cantidad']
                asistencia_detalle.save()
                
                # Obtener la asistencia actualizada
                asistencia = asistencia_detalle.importar_asistencia
                
                # Serializar la asistencia y sus detalles
                serializer = AsistenciaSerializer(asistencia)
                data = serializer.data
                detalles = AsistenciaDetalleSerializer(asistencia.detalle.all(), many=True).data
                data['detalle'] = detalles
                
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "La cantidad no se proporcionó en los datos de la solicitud"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#---------------------------------------------------
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Registro, ImportarAsistencia
from .serializers import ImportarAsistenciaSerializer

@api_view(['GET'])
def ingresos_del_dia_actual(request, idcodigogeneral=None):
    try:
        # Obtener el registro abierto actual
        registro_abierto = Registro.objects.filter(estado='Abierto').first()
        if not registro_abierto:
            return Response({"error": "No hay registro abierto para el día actual."},
                            status=status.HTTP_404_NOT_FOUND)

        # Obtener la fecha de apertura y cierre del registro abierto
        fecha_apertura = registro_abierto.FechaAbierto
        fecha_cierre = registro_abierto.FechaCerrado
        
        # Si la fecha de cierre no está establecida, usar la fecha actual
        if not fecha_cierre:
            fecha_cierre = timezone.now().strftime('%Y%m%d')

        # Filtrar los registros de ImportarAsistencia dentro del rango de fechas del registro abierto
        importar_asistencias = ImportarAsistencia.objects.filter(
            fecha__range=(fecha_apertura, fecha_cierre)
        )

        # Si se proporciona idcodigogeneral, filtrar por ese valor
        if idcodigogeneral:
            # Filtrar los registros por idcodigogeneral
            importar_asistencias = importar_asistencias.filter(detalle__idcodigogeneral=idcodigogeneral)

            # Verificar si hay registros asociados con el idcodigogeneral proporcionado
            if not importar_asistencias.exists():
                return Response({"error": f"No se encontraron registros para el idcodigogeneral {idcodigogeneral}."},
                                status=status.HTTP_404_NOT_FOUND)

        # Serializar los datos y sus detalles
        data = []
        existing_ids = set()  # Conjunto para almacenar IDs ya agregados
        for importar_asistencia in importar_asistencias:
            asistencia_data = ImportarAsistenciaSerializer(importar_asistencia).data
            detalles = []
            for detalle in importar_asistencia.detalle.all():
                detalle_data = {
                    "item": detalle.item,
                    "idcodigogeneral": detalle.idcodigogeneral,
                    "idactividad": detalle.idactividad,
                    "idlabor": detalle.idlabor,
                    "idconsumidor": detalle.idconsumidor,
                    "cantidad": detalle.cantidad
                }
                detalles.append(detalle_data)
            # Verificar si el ID de la asistencia ya está presente en existing_ids
            if asistencia_data['id'] not in existing_ids:
                asistencia_data['detalle'] = detalles
                data.append(asistencia_data)
                existing_ids.add(asistencia_data['id'])  # Agregar el ID a existing_ids
        
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


#----------------------------------------------------------------
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import ImportarAsistencia
from .serializers import ImportarAsistenciaSerializer
from .models import Registro

@api_view(['GET'])
def importaciones_por_fecha(request, fecha_abierto):
    try:
        # Obtener el registro para la fecha proporcionada
        registro = Registro.objects.filter(FechaAbierto=fecha_abierto).first()
        
        if not registro:
            return Response({"error": "No hay registro para la fecha proporcionada."},
                            status=status.HTTP_404_NOT_FOUND)

        # Obtener la fecha de apertura y cierre del registro
        fecha_apertura = registro.FechaAbierto
        fecha_cierre = registro.FechaCerrado
        
        # Filtrar los registros de ImportarAsistencia dentro del rango de fechas del registro
        importar_asistencias = ImportarAsistencia.objects.filter(
            fecha__range=(fecha_apertura, fecha_cierre)
        )

        # Serializar los datos y sus detalles
        data = []
        existing_ids = set()  # Conjunto para almacenar IDs ya agregados
        for importar_asistencia in importar_asistencias:
            asistencia_data = ImportarAsistenciaSerializer(importar_asistencia).data
            detalles = []
            for detalle in importar_asistencia.detalle.all():
                detalle_data = {
                    "item": detalle.item,
                    "idcodigogeneral": detalle.idcodigogeneral,
                    "idactividad": detalle.idactividad,
                    "idlabor": detalle.idlabor,
                    "idconsumidor": detalle.idconsumidor,
                    "cantidad": detalle.cantidad
                }
                detalles.append(detalle_data)
            # Verificar si el ID de la asistencia ya está presente en existing_ids
            if asistencia_data['id'] not in existing_ids:
                asistencia_data['detalle'] = detalles
                data.append(asistencia_data)
                existing_ids.add(asistencia_data['id'])  # Agregar el ID a existing_ids
        
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#------------------------------------------
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Registro
from .serializers import RegistroSerializer

@api_view(['GET'])
def registros_lista(request):
    try:
        registros = Registro.objects.all()
        serializer = RegistroSerializer(registros, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# views.py
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_tipos_usuarios(request):
    tipo_usuarioapp = [choice[1] for choice in CustomUser.TipoUsuario.choices]
    return JsonResponse({'tipos_usuarios': tipo_usuarioapp})