import json
import logging

from django.core import serializers
from django.http import JsonResponse
# from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from myapp.models import Book


# Create your views here.
@require_http_methods(["GET"])
def add_book(request):
    response = {}
    try:
        book = Book(book_name=request.GET.get('book_name'))
        book.save()
        response['msg'] = 'success'
        response['error_num'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error_num'] = 1

    return JsonResponse(response)


modify_record_logger = logging.getLogger("modify_record")


# @cache_page(60 * 1)
@require_http_methods(["GET"])
def show_books(request):
    response = {}
    for _ in range(1000):
        modify_record_logger.info("test")
    try:
        books = Book.objects.filter()
        response['list'] = json.loads(serializers.serialize("json", books))
        response['msg'] = 'success'
        response['error_num'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error_num'] = 1

    return JsonResponse(response)


def test_log():
    modify_record_logger.info("""
        teshshshifahsafnakjfnjdsajfkhdsajhfjsahfjhajhfdjahfjdsahjfd
        teshshshifahsafnakjfnjdsajfkhdsajhfjsahfjhajhfdjahfjdsahjfd
        teshshshifahsafnakjfnjdsajfkhdsajhfjsahfjhajhfdjahfjdsahjfd
        teshshshifahsafnakjfnjdsajfkhdsajhfjsahfjhajhfdjahfjdsahjfd
        teshshshifahsafnakjfnjdsajfkhdsajhfjsahfjhajhfdjahfjdsahjfd
        teshshshifahsafnakjfnjdsajfkhdsajhfjsahfjhajhfdjahfjdsahjfd
        teshshshifahsafnakjfnjdsajfkhdsajhfjsahfjhajhfdjahfjdsahjfd
        teshshshifahsafnakjfnjdsajfkhdsajhfjsahfjhajhfdjahfjdsahjfd
        teshshshifahsafnakjfnjdsajfkhdsajhfjsahfjhajhfdjahfjdsahjfd
        teshshshifahsafnakjfnjdsajfkhdsajhfjsahfjhajhfdjahfjdsahjfd
        """)
