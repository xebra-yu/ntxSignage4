from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('mgr_upload/', views.mgr_upload, name='mgr_upload'),
    path('device/', views.device, name='device'),
    path('template/', views.template, name='template'),
    path('device_add/', views.device_add, name='device_add'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('ntxcmd', views.ntxcmd),
    path('showlog/', views.showlog),
]
