from django.db import models
from django.contrib.auth.models import User




class Book(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='my_book')
    readers = models.ManyToManyField(User, through='UserBookRelations', related_name='book')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None, null=True)

    def __str__(self):
        return f'ID {self.id}: {self.name}'


class UserBookRelations(models.Model):
    RATE_CHOICES = (
        (1, 'Bad'),
        (2, 'Well'),
        (3, 'Good'),
        (4, 'Very good'),
        (5, 'Amazing')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True, blank=True)

    def __str__(self):
        return f'{self.user}: {self.book.name}, Rate: {self.rate}'

    def save(self, *args, **kwargs):
        from store.utils import set_rating

        creating = not self.pk
        old_rating = self.rate
        super().save(*args, **kwargs)
        new_rating = self.rate
        if creating:
            set_rating(self.book)
