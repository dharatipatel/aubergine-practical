# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pyshorteners
import short_url
from django.shortcuts import render
from django.utils import timezone
from requests import ConnectTimeout
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users import tasks
from users.models import User, UserVerification, UserMedia
from users.serializers import UserRegistrationSerializer, UserSerializer, UserLoginSerializer, \
    UserVerificationSerializer, UserMediaSerializer, UrlListSerializer
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from aubergine_test.settings import BITLY_ACCESS_TOKEN
# Create your views here.


class UserRegisterView(APIView):

    def post(self, request):
        """

        :param request:
        {
          "email":"test@test.com",
          "password":"Test123456",
          "first_name":"Test",
          "last_name":"Test"
        }
        :return:

        'Failure'
            for invalid request params

            {
                "error": true,
                "message": "Bad Request",
                "data": {
                    "email": [
                        "This field is required."
                    ],
                    "password": [
                        "This field is required."
                    ]
                }
            }

            {
                "error": true,
                "message": "Bad Request",
                "data": {
                    "email": [
                        "Enter a valid email address."
                    ]
                }
            }

         'Success'
            {
                "error": false,
                "message": "Registered Successfully",
                "data": {
                    "user": {
                        "id": 2,
                        "last_login": "2020-07-10T06:22:11.659627Z",
                        "first_name": "dharati",
                        "last_name": "dekavadiya",
                        "email": "dharati.dhp@gmail.com",
                        "username": null,
                        "is_email_verified": false,
                        "created_at": "2020-07-10T06:22:11.659724Z",
                        "updated_at": "2020-07-10T06:22:11.842947Z"
                    },
                    "token": "e27bd8dfc7e36c14d38cd90a22ec4fa43cd3a768"
                }
            }
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': True,
                'message': "Bad Request",
                'data': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        extra_fields = {
            'first_name': request.data['first_name'],
            'last_name': request.data['last_name'],
            'last_login': timezone.now(),
            'username': request.data['username'] if 'username' in request.data else None
        }
        user = User.objects.create_user(email=request.data['email'], password=request.data['password'],
                                        **extra_fields)
        # Creating auth token for the user
        token = Token.objects.create(user=user)

        user_serializer = UserSerializer(user)

        tasks.send_verification_mail.delay(user_serializer.data)

        return Response({
            'error': False,
            'message': "Registered Successfully",
            'data': {
                'user': user_serializer.data,
                'token': token.key
            }
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):

    def post(self, request):
        """
            :param
            {
                    "email" : "dharati.20794@gmail.com",
                    "password": 123456
            }

            :return
            'Failure'
                For invalid request
                {
                    "error": true,
                    "message": "Bad Request",
                    "data": {
                        "email": [
                            "This field may not be blank."
                        ]
                    }
                }
                {
                    "error": true,
                    "message": "Bad Request",
                    "data": {
                        "email": [
                            "Enter a valid email address."
                        ]
                    }
                }
                for an email not registered
                {
                    "error": true,
                    "message": "Account does not exist with given email address",
                    "data": {}
                }
            'Success'
                {
                    "error": false,
                    "message": "Login Successfully",
                    "data": {
                        "user": {
                            "id": 10,
                            "last_login": "2020-07-10T06:50:07.886716Z",
                            "first_name": "hiren",
                            "last_name": "patel",
                            "email": "hiren@yopmail.com",
                            "username": null,
                            "is_email_verified": false,
                            "created_at": "2020-07-10T06:50:07.887012Z",
                            "updated_at": "2020-07-10T06:50:08.031816Z"
                        },
                        "token": "6a424722d7de3a91c72379c4ed966c136362fcce"
                    }
                }
        """

        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': True,
                'message': "Bad Request",
                'data': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=request.data['email'])
        except User.DoesNotExist:
            return Response({
                'error': True,
                'message': "Account does not exist with given email address",
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        if user.check_password(request.data['password']):

            token = Token.objects.get(user_id=user.id)
            user_serializer = UserSerializer(user)

            return Response({
                'error': False,
                'message': "Login Successfully",
                'data': {
                    'user': user_serializer.data,
                    'token': token.key
                }
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                'error': True,
                'message': "Invalid Credential",
                'data': {}
            }, status=status.HTTP_401_UNAUTHORIZED)


class UserVerificationView(APIView):

    def post(self, request):
        """
            :param
            {
                "token":"fda5afe60d47cf391fc2d0f3cb6e683bcddb401a"
            }
            :return
                'Failure'
                {
                    "error": true,
                    "message": "Bad Request",
                    "data": {
                        "token": [
                            "This field is required."
                        ]
                    }
                }

                {
                    "error": true,
                    "message": "Verification Token is not valid",
                    "data": {}
                }

                {
                    "error": true,
                    "message": "Verification Token Expired",
                    "data": {}
                }

                'Success'
                {
                    "error": false,
                    "message": "Already verified an email address",
                    "data": {}
                }

                {
                    "error": false,
                    "message": "Successfully verified an email address",
                    "data": {}
                }
            """
        serializer = UserVerificationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'error': True,
                'message': "Bad Request",
                'data': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_verification = UserVerification.objects.get(token=request.data['token'])
        except UserVerification.DoesNotExist:
            return Response({
                'error': True,
                'message': "Verification Token is not valid",
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        if user_verification.expires_at < timezone.now():
            return Response({
                'error': True,
                'message': "Verification Token Expired",
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = User.objects.get(id=user_verification.user_id)

            if user.is_email_verified:
                return Response({
                    'error': False,
                    'message': "Email address is already verified",
                    'data': {}
                }, status=status.HTTP_200_OK)

            user.is_email_verified = True
            user.save()

            return Response({
                'error': False,
                'message': "Successfully verified an email address",
                'data': {}
            }, status=status.HTTP_200_OK)


class UserMediaView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """

        :param request:
        {
            "urls":[
                String
            ]
        }
        :return:
            Failure if urls are not in request data
            {
                "error": true,
                "message": "Bad Request",
                "data": {
                    "urls": [
                        "This field is required."
                    ]
                }
            }

            Failure if urls are not valid
            {
                "error": true,
                "message": "Bad Request",
                "data": {
                    "urls": {
                        "0": [
                            "Enter a valid URL."
                        ]
                    }
                }
            }
        """
        serializer = UrlListSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'error': True,
                'message': "Bad Request",
                'data': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        media_obj = []

        shortner = pyshorteners.Shortener(api_key=BITLY_ACCESS_TOKEN)
        try:
            for url in request.data['urls']:
                media_obj.append({
                    'original_url': url,
                    'compressed_url': shortner.bitly.short(url),
                    'user_id': user.id
                })
        except ConnectTimeout as e:
            # bitly API is called to shorten url. It may raise connection timeout error
            return Response({
                'error': True,
                'message': "Could not shorten URL. Something went wrong",
                'data': serializer.errors
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serialized = UserMediaSerializer(many=True)
        serialized.create(media_obj)
        return Response({
            'error': False,
            'message': "Images saved Successfully",
            'data': media_obj
        }, status=status.HTTP_201_CREATED)
