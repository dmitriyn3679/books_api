from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Book, UserBookRelations


class BookReadersSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class BooksSerializer(ModelSerializer):
    annotated_likes = serializers.IntegerField(read_only=True)
    annotated_bookmarks = serializers.IntegerField(read_only=True)
    owner_name = serializers.CharField(source='owner.username', default='', read_only=True)
    readers = BookReadersSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'name', 'price', 'author_name', 'annotated_likes', 'annotated_bookmarks', 'owner_name',
                  'readers')


class UserBookRelationsSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelations
        fields = ('book', 'like', 'in_bookmarks', 'rate')