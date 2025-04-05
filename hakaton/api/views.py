from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import viewsets, status, filters, generics
from django.http import HttpResponse
from django.db import connection
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissionsOrAnonReadOnly, AllowAny, \
    IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import NewsItem, UserTagSubscription, Source, Tag, ApiUser
from .serializer import NewsSerializer, TagSerializer, SourceSerializer, UserTagSubscriptionSerializer, UserSerializer, \
    UserRegistrationSerializer


def call_test_function():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM test()")
        columns = [col[0] for col in cursor.description]  # Получаем названия колонок
        results = cursor.fetchall()

    # Преобразуем в список словарей (опционально)
    data = [dict(zip(columns, row)) for row in results]
    for i in data:
        print(i['lol'], i['lolx2'])
    return data


def index(request):
    # Способ 1: Использование Func в запросе
    call_test_function()
    return HttpResponse(f"Результат функции: {1}")
    # Или для JSON:
    # return JsonResponse({'result': result})


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]  # Требуется аутентификация

    def get(self, request):
        return Response({"message": "Вы авторизованы!"})


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    http_method_names = ["get"]
    serializer_class = TagSerializer


class SourceItemViewSet(viewsets.ModelViewSet):
    queryset = Source.objects.all()
    http_method_names = ["get"]
    serializer_class = SourceSerializer


class UserTagSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = UserTagSubscription.objects.all()
    http_method_names = ["get"]
    serializer_class = UserTagSubscriptionSerializer


class ApiUserItemViewSet(viewsets.ModelViewSet):
    queryset = ApiUser.objects.all()
    http_method_names = ["get"]
    serializer_class = UserSerializer


class NewsItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]  # Запись только для аутентифицированных
    queryset = NewsItem.objects.all()
    http_method_names = ["get", 'post']
    serializer_class = NewsSerializer


class NewsFilterAPIView(APIView):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    queryset = NewsItem.objects.all()  # Обязательно для DjangoModelPermissions

    def get_queryset(self):
        return self.queryset.all()  # Базовый запрос

    def get(self, request):
        # Получаем параметры
        filter_param = request.query_params.get('filter', '')
        user_id = request.query_params.get('user_id')

        # Начинаем с базового queryset
        queryset = self.get_queryset()

        # Фильтр по тегам (только если есть параметр filter)
        if filter_param:
            filter_values = [value.strip() for value in filter_param.split(',')]
            for tag in filter_values:
                queryset = queryset.filter(tags__name=tag)

        # Фильтр по пользователю (только если есть user_id)
        if user_id:
            print()
            try:
                queryset = queryset.filter(author_id=int(user_id))
            except ValueError:
                return Response(
                    {"error": "Invalid user_id format"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Всегда возвращаем результат, даже без фильтров
        serializer = NewsSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = NewsSerializer(
            data=request.data,
            context={'request': request}  # Передаём request в сериализатор
        )

        if serializer.is_valid():
            serializer.save()  # Автоматически вызовет метод create сериализатора
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "username": request.user.username,
            "email": request.user.email,
        })


class UserRegistrationAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]  # Разрешить доступ без аутентификации
    serializer_class = UserRegistrationSerializer
    queryset = get_user_model().objects.none()

    def post(self, request, *args, **kwargs):
        # Остальной код без изменений
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            "user": serializer.data.id,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class id_userAPIView(APIView):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    queryset = NewsItem.objects.all()  # Обязательно для DjangoModelPermissions

    def get(self, request):
        # Получаем параметры

        username = request.query_params.get('username')
        queryset = ApiUser.objects.all().get(username=username)

        return Response({"id": queryset.id})
