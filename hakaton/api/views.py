from django.contrib.auth import get_user_model
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissionsOrAnonReadOnly, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
import secrets
import string
from .models import NewsItem, Source, Tag, ApiUser, UserNewSubscription
from .serializer import NewsSerializer, TagSerializer, SourceSerializer, UserSerializer, \
    UserRegistrationSerializer, UserNewSubscriptionSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    http_method_names = ["get", "post"]
    serializer_class = TagSerializer


class SourceItemViewSet(viewsets.ModelViewSet):
    queryset = Source.objects.all()
    http_method_names = ["get"]
    serializer_class = SourceSerializer


class UserNewSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = UserNewSubscription.objects.all()
    http_method = ['post', 'get', 'delete']
    serializer_class = UserNewSubscriptionSerializer


class ApiUserItemViewSet(viewsets.ModelViewSet):
    queryset = ApiUser.objects.all()
    serializer_class = UserSerializer
    http_method_names = ["get", "put", "patch"]

    def update(self, request, *args, **kwargs):
        user_id = request.query_params.get('id')
        telegram_chat_id = request.query_params.get('telegram_chat_id')

        if not user_id or not telegram_chat_id:
            return Response(
                {"error": "Параметры 'id' и 'telegram_chat_id' обязательны"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = ApiUser.objects.get(id=user_id)
        except ApiUser.DoesNotExist:
            return Response(
                {"error": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        user.telegram_chat_id = telegram_chat_id
        user.save()

        return Response(
            {"id": user.id, "telegram_chat_id": user.telegram_chat_id},
            status=status.HTTP_200_OK
        )


class NewsItemViewSet(viewsets.ModelViewSet):
    queryset = NewsItem.objects.all()
    http_method_names = ["get", 'post']
    serializer_class = NewsSerializer


from rest_framework.views import APIView


class NewsFilterAPIView(APIView):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    queryset = NewsItem.objects.all()
    serializer_class = NewsSerializer

    def get_queryset(self):
        return self.queryset.prefetch_related('tags', 'author')

    def get(self, request):
        filter_param = request.query_params.get('filter', '')
        search_query = request.query_params.get('search', '')
        user_id = request.query_params.get('user_id')

        queryset = self.get_queryset()

        if filter_param:
            filter_tags = [tag.strip() for tag in filter_param.split(',') if tag.strip()]
            for tag_name in filter_tags:
                queryset = queryset.filter(tags__name__icontains=tag_name)

        if search_query:
            if search_query[0] == '_':
                queryset = Tag.objects.all().filter(name__icontains=search_query[1:])
                serializer = TagSerializer(queryset, many=True)

                return Response(serializer.data)
            else:
                queryset = queryset.filter(title__icontains=search_query)

        if user_id:
            try:
                queryset = queryset.filter(author_id=int(user_id))
            except ValueError:
                return Response(
                    {"error": "Invalid user_id format"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        queryset = queryset.distinct().order_by('-created_at')

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        print(ApiUser.objects.all().get(pk=int(request.data['author'])).can_write)
        if ApiUser.objects.all().get(pk=int(request.data['author'])).can_write:

            serializer = NewsSerializer(
                data=request.data,
                context={'request': request}
            )
            #
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            #
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "username": request.user.username,
            "email": request.user.email,
        })


class UserRegistrationAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    queryset = get_user_model().objects.none()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        print(serializer.data)
        return Response({
            "user": serializer.data["username"],
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class id_userAPIView(APIView):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    queryset = NewsItem.objects.all()

    def get(self, request):
        username = request.query_params.get('username')
        queryset = ApiUser.objects.all().get(username=username)

        return Response({"id": queryset.id})


class subs_userAPIView(APIView):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    queryset = ApiUser.objects.all()

    def get(self, request):
        queryset = ApiUser.objects.all().filter(subscribed=True)
        data = [i.telegram_chat_id for i in queryset]
        return Response(data)


from rest_framework.response import Response
from rest_framework import status
from .models import ApiUser, NewsItem


class checklikeAPIView(APIView):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    queryset = UserNewSubscription.objects.all()

    def delete(self, request):
        user_id = request.query_params.get('user_id')
        news_id = request.query_params.get('id')

        if not user_id or not news_id:
            return Response(
                {"error": "Параметры user_id и id обязательны"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = ApiUser.objects.get(pk=int(user_id))
            news = NewsItem.objects.get(pk=int(news_id))

            subscription = UserNewSubscription.objects.filter(
                user=user,
                new=news
            ).first()

            if not subscription:
                return Response(
                    {"error": "Подписка не найдена"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Удаляем подписку
            subscription.delete()
            return Response(
                {"message": "Подписка успешно удалена"},
                status=status.HTTP_204_NO_CONTENT
            )

        except (ApiUser.DoesNotExist, NewsItem.DoesNotExist):
            return Response(
                {"error": "Пользователь или новость не найдены"},
                status=status.HTTP_404_NOT_FOUND
            )

        except ValueError:
            return Response(
                {"error": "Некорректный формат ID"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request):
        user_id = request.query_params.get('user_id')
        id = request.query_params.get('id')
        return Response(self.queryset.filter(user=ApiUser.objects.all().get(pk=int(user_id)),
                                             new=NewsItem.objects.all().get(pk=int(id))).exists())


class tg_userAPIView(APIView):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    queryset = NewsItem.objects.all()

    def get(self, request):

        tg = request.query_params.get('tg')
        queryset = ApiUser.objects.all().get(telegram_chat_id=tg)

        return Response({"id": queryset.id, 'tg': queryset.telegram_chat_id})

    def put(self, request):
        user_id = request.query_params.get('id')
        telegram_chat_id = request.query_params.get('telegram_chat_id')

        if not user_id or not telegram_chat_id:
            return Response(
                {"error": "Параметры 'id' и 'telegram_chat_id' обязательны"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = ApiUser.objects.get(id=user_id)
            user.telegram_chat_id = telegram_chat_id
            user.save()
            return Response(
                {"id": user.id, "telegram_chat_id": user.telegram_chat_id},
                status=status.HTTP_200_OK
            )
        except ApiUser.DoesNotExist:
            return Response(
                {"error": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return Response(
                {"error": "Некорректный ID пользователя"},
                status=status.HTTP_400_BAD_REQUEST
            )
