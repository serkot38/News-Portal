from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce


article = 'AR'
news = 'NW'

POST = [
    (news, 'Новость'),
    (article, 'Статья')
]


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_rating = models.IntegerField(default=0)

    def update_rating(self):
        posts_rating = Post.objects.filter(author_id=self.pk).aggregate(posts_rating_sum=Coalesce(Sum('rating_post')*3, 0))
        comments_rating = Comment.objects.filter(user_id=self.user).aggregate(comments_rating_sum=Coalesce(Sum('rating_comment'), 0))
        posts_comments_rating = Comment.objects.filter(post__author__user=self.user).aggregate(posts_comments_rating_sum=Coalesce(Sum('rating_comment'), 0))

        self.user_rating = posts_rating['posts_rating_sum'] + comments_rating['comments_rating_sum'] + posts_comments_rating['posts_comments_rating_sum']
        self.save()


class Category(models.Model):
    name = models.CharField(unique=True, max_length=255)


class Post(models.Model):
    objects = None
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=2, choices=POST)
    date_time = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through="PostCategory")
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating_post = models.IntegerField(default=0)

    def like(self):
        self.rating_post += 1
        self.save()

    def dislike(self):
        self.rating_post -= 1
        self.save()

    def preview(self):
        return self.text[:124]


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    objects = None
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)
    rating_comment = models.IntegerField(default=0)

    def like(self):
        self.rating_comment += 1
        self.save()

    def dislike(self):
        self.rating_comment -= 1
        self.save()
