from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    # url(r'^user_settings$', views.user_settings),
    url(r'^validate_register$', views.validate_register),
    url(r'^validate_login$', views.validate_login),
    url(r'^login_success$', views.success),
    url(r'^wheel$', views.wheel),

]
