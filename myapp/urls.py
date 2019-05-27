from django.conf.urls import url, include
from myapp import views

urlpatterns = [
    url(r'add_book$', views.add_book),
    url(r'show_books$', views.show_books),
    url(r'getBookNum/(?P<book_name>\w+)$', views.get_book_num),
]
