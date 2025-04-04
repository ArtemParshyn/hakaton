from django.shortcuts import render
from rest_framework import viewsets

from django.http import HttpResponse, JsonResponse
from django.db.models import Func
from django.db import connection
from django.db import connection
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


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
