from django.contrib import admin
from myapp.models import Book


# Register your models here.

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('add_time', 'book_name')
