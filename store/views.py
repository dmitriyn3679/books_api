from django.db.models import Count, Case, When
from django.shortcuts import render
from rest_framework.mixins import UpdateModelMixin, ListModelMixin

from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from .models import Book, UserBookRelations
from .permissions import IsOwnerOrStaffOrReadOnly
from .serializers import BooksSerializer, UserBookRelationsSerializer


class BooksViewSet(ModelViewSet):
    queryset = Book.objects.all().annotate(
        annotated_likes=Count(Case(When(userbookrelations__like=True, then=1))),
        annotated_bookmarks=Count(Case(When(userbookrelations__in_bookmarks=True, then=1)))
    ).select_related('owner').prefetch_related('readers')
    serializer_class = BooksSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    filter_fields = ['price', 'name']
    search_fields = ['name', 'author_name']
    ordering_fields = ['price', 'author_name']

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserBookRelationsView(UpdateModelMixin, GenericViewSet):
    queryset = UserBookRelations.objects.all()
    serializer_class = UserBookRelationsSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'book'

    def get_object(self):
        obj, create = UserBookRelations.objects.get_or_create(user=self.request.user, book_id=self.kwargs['book'])
        return obj


def auth(request):
    return render(request, 'oauth.html')