from django.contrib.auth.models import User
from django.test import TestCase

from store.models import Book, UserBookRelations
from store.utils import set_rating


class SetRatingTestCase(TestCase):
    def setUp(self):
        user1 = User.objects.create(username='test_user1', first_name='Test1', last_name='Name1')
        user2 = User.objects.create(username='test_user2', first_name='Test2', last_name='Name2')
        user3 = User.objects.create(username='test_user3', first_name='Test3', last_name='Name3')

        self.book_1 = Book.objects.create(name='Test book 1', price=25, author_name='Test Author 1', owner=user3)

        UserBookRelations.objects.create(user=user1, book=self.book_1, like=True, in_bookmarks=True, rate=5)
        UserBookRelations.objects.create(user=user2, book=self.book_1, like=True, in_bookmarks=False)
        user_book3 = UserBookRelations.objects.create(user=user3, book=self.book_1, like=False, in_bookmarks=False)
        user_book3.rate = 4
        user_book3.save()

    def test_set_rating(self):
        set_rating(self.book_1)
        self.book_1.refresh_from_db()
        self.assertEqual(4.5, self.book_1.rating)
