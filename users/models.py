# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


# Create your models here.
from django.utils.timezone import now
from rest_framework.authtoken.models import Token


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """
            Creates new user with given email and password
            :return
                user, token (auth_token)
        """

        if not email:
            raise ValueError('Valid email required')

        # Normalize the provided email
        email = self.normalize_email(email)

        # Creating user object
        user = self.model(email=email, **extra_fields)
        # # setting user password
        user.set_password(password)
        # # saving user in database
        user.save()

        return user


class User(AbstractBaseUser):
    """
        Maintain user and its attributes
    """

    class Meta:
        db_table = 'users'
    # first name of the user
    first_name = models.CharField(max_length=200, null=True)
    # last name of the user
    last_name = models.CharField(max_length=200, null=True)
    # email id of the user
    email = models.CharField(max_length=200, unique=True)
    # email id of the user
    username = models.CharField(max_length=200, null=True)
    # role of the user (foreign key to UserRole model)
    is_email_verified = models.BooleanField(default=False)
    # the date when the user was created
    created_at = models.DateTimeField(default=now)
    # the date when the user object was last modified
    updated_at = models.DateTimeField(auto_now=True)

    # defines the user manager class for User
    objects = UserManager()

    # specifies the field that will be used as username by django
    # drf_auth_users framework
    USERNAME_FIELD = 'email'


class UserVerification(models.Model):
    class Meta:
        db_table = 'user_verification'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=200, blank=True)
    # the date when the verification token expired for associated user
    expires_at = models.DateTimeField()


class UserMedia(models.Model):
    class Meta:
        db_table = 'user_media'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_url = models.TextField()
    compressed_url = models.CharField(max_length=100)
    # the date when the user media created
    created_at = models.DateTimeField(default=now)
    # the date when the user media object was last modified
    updated_at = models.DateTimeField(auto_now=True)
