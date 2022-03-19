from django.db import connection
from django.db.models import Count, Case, When
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from rest_framework import status

from django.urls import reverse
from django.contrib.auth.models import User
from django.test.utils import CaptureQueriesContext

from store.models import Book, UserBookRelations
from store.serializers import BooksSerializer

import json




class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.book_1 = Book.objects.create(name='Test book 1', price=25, author_name='Author 1', owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2 Author 1', price=55, author_name='Author 3')
        self.book_3 = Book.objects.create(name='Test book 3', price=55, author_name='Author 2')

    def test_get(self):
        url = reverse('book-list')
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)
            self.assertEqual(2, len(queries))
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelations__like=True, then=1))),
            annotated_bookmarks=Count(Case(When(userbookrelations__in_bookmarks=True, then=1)))
        ).order_by('id')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_one_object(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        response = self.client.get(url)
        serializer_data = {
            'id': self.book_1.id,
            'name': 'Test book 1',
            'price': '25.00',
            'author_name': 'Author 1',
            'annotated_likes': 0,
            'annotated_bookmarks': 0,
            'owner_name': self.user.username,
            'readers': []
        }
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        print(serializer_data)
        print('------------')
        print(response.data)
        self.assertEqual(serializer_data, response.data)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 55})
        books = Book.objects.filter(id__in=[self.book_2.id, self.book_3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelations__like=True, then=1))),
            annotated_bookmarks=Count(Case(When(userbookrelations__in_bookmarks=True, then=1)))
        )
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})
        books = Book.objects.filter(id__in=[self.book_1.id, self.book_2.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelations__like=True, then=1))),
            annotated_bookmarks=Count(Case(When(userbookrelations__in_bookmarks=True, then=1)))
        )
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'author_name'})
        books = Book.objects.filter(id__in=[self.book_1.id, self.book_3.id, self.book_2.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelations__like=True, then=1))),
            annotated_bookmarks=Count(Case(When(userbookrelations__in_bookmarks=True, then=1)))
        ).order_by('author_name')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-list')
        data = {
            "name": "Postgresql",
            "price": 500.50,
            "author_name": "Patric Python"
            }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 225,
            "author_name": self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(225, self.book_1.price)

    def test_delete(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, Book.objects.all().count())

    def test_update_not_owner(self):
        self.user2 = User.objects.create(username='test_user2')
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 225,
            "author_name": self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(25, self.book_1.price)

    def test_delete_not_owner(self):
        self.user2 = User.objects.create(username='test_user2')
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user2)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(3, Book.objects.all().count())

    def test_update_staff(self):
        self.user_staff = User.objects.create(username='test_user_staff', is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 225,
            "author_name": self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user_staff)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(225, self.book_1.price)


class UserBookRelationsApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.book_1 = Book.objects.create(name='Test book 1', price=25, author_name='Author 1', owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2 Author 1', price=55, author_name='Author 3')
        self.book_3 = Book.objects.create(name='Test book 3', price=45, author_name='Author 2')

    def test_like_and_bookmarks(self):
        url = reverse('userbookrelations-detail', args=(self.book_1.id,))
        data = {
            "like": True,
            "in_bookmarks": True
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        relation = UserBookRelations.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.like)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelations-detail', args=(self.book_1.id,))
        data = {
            "rate": 5
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        relation = UserBookRelations.objects.get(user=self.user, book=self.book_1)
        self.assertEqual(5, relation.rate)

    def test_incorrect_rate(self):
        url = reverse('userbookrelations-detail', args=(self.book_1.id,))
        data = {
            "rate": 6
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual({'rate': [ErrorDetail(string='"6" is not a valid choice.', code='invalid_choice')]}, response.data)





