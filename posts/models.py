from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Post(models.Model):
    text = models.TextField(verbose_name='Текст', help_text='Это поле обязательно, пожалуйста заполните его.')
    pub_date = models.DateTimeField('date published', auto_now_add=True, db_index=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts',
        null=True
    )
    group = models.ForeignKey(
        'Group', blank=True, null=True,
        related_name='posts', on_delete=models.SET_NULL,
        verbose_name='Группа',
        help_text='Это поле необязательно, но оно может помочь Вам найти единомышленников.'
    )

    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta():
        ordering = ('-pub_date',)

    def __str__(self):
        sentence = (self.text[:15] + '..') if len(self.text) > 15 else self.text
        return sentence


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Comment(models.Model):
    created = models.DateTimeField('date published', auto_now_add=True)
    text = models.TextField(max_length=240)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='following')
