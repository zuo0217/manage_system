from django.urls import path
from index.views import index, superManage

urlpatterns = [
    path(r'', index),
    path(r'super/', superManage)
]
