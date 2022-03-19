from django.db.models import Count, Case, When
from django.test import TestCase

from store.serializers import BooksSerializer
from store.models import Book, UserBookRelations
from django.contrib.auth.models import User


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        user1 = User.objects.create(username='test_user1', first_name='Test1', last_name='Name1')
        user2 = User.objects.create(username='test_user2', first_name='Test2', last_name='Name2')
        user3 = User.objects.create(username='test_user3', first_name='Test3', last_name='Name3')

        book_1 = Book.objects.create(name='Test book 1', price=25, author_name='Test Author 1', owner=user3)
        book_2 = Book.objects.create(name='Test book 2', price=55, author_name='Test Author 2')

        UserBookRelations.objects.create(user=user1, book=book_1, like=True, in_bookmarks=True)
        UserBookRelations.objects.create(user=user2, book=book_1, like=True, in_bookmarks=False)
        UserBookRelations.objects.create(user=user3, book=book_1, like=False, in_bookmarks=False)

        UserBookRelations.objects.create(user=user1, book=book_2, like=True, in_bookmarks=True)
        UserBookRelations.objects.create(user=user2, book=book_2, like=False, in_bookmarks=True)
        UserBookRelations.objects.create(user=user3, book=book_2, like=True, in_bookmarks=False)

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelations__like=True, then=1))),
            annotated_bookmarks=Count(Case(When(userbookrelations__in_bookmarks=True, then=1)))
        ).order_by('id')

        data = BooksSerializer(books, many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'Test book 1',
                'price': '25.00',
                'author_name': 'Test Author 1',
                'annotated_likes': 2,
                'annotated_bookmarks': 1,
                'owner_name': 'test_user3',
                'readers': [
                    {
                        'first_name': 'Test1',
                        'last_name': 'Name1'
                     },
                    {
                        'first_name': 'Test2',
                        'last_name': 'Name2'
                    },
                    {
                        'first_name': 'Test3',
                        'last_name': 'Name3'
                    },

                ]
            },
            {
                'id': book_2.id,
                'name': 'Test book 2',
                'price': '55.00',
                'author_name': 'Test Author 2',
                'annotated_likes': 2,
                'annotated_bookmarks': 2,
                'owner_name': '',
                'readers': [
                    {
                        'first_name': 'Test1',
                        'last_name': 'Name1'
                    },
                    {
                        'first_name': 'Test2',
                        'last_name': 'Name2'
                    },
                    {
                        'first_name': 'Test3',
                        'last_name': 'Name3'
                    },
                ]
            }
        ]
        print(data)
        self.assertEqual(expected_data, data)