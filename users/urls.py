from django.conf.urls import url
from users import views
urlpatterns = [
    url('register', views.UserRegisterView.as_view(), name='user_register'),
    url('login', views.UserLoginView.as_view(), name='user_login'),
    url('verification', views.UserVerificationView.as_view(), name='user_verification'),
    url('media', views.UserMediaView.as_view(), name='user_media')
]