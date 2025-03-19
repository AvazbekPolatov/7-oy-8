from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager
from shop.models import Product


class User(AbstractBaseUser):
    email = models.EmailField(max_length=100, unique=True)
    full_name = models.CharField(max_length=100)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    likes = models.ManyToManyField(Product, blank=True, related_name='liked_by_users')
    is_manager = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email

    @staticmethod
    def has_perm(perm, obj=None):
        return True

    @staticmethod
    def has_module_perms(app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin or self.is_manager

    def get_likes_count(self):
        return self.likes.count()
