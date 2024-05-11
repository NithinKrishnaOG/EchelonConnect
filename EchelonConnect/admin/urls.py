from django.urls import path
from . import views

urlpatterns = [
    path('admin/', views.admin, name='admin'),
    path('admin_home', views.admin_home, name='admin_home'),
    path('admin_search', views.admin_search, name='admin_search'),
    path('admin_user_detail', views.admin_user_detail, name='admin_user_detail'),
    path('admin_user_create', views.admin_user_create, name='admin_user_create'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    # path('admin_delete_user', views.admin_delete_user, name='admin_delete_user'),
    path('admin_delete_user/<str:username>/', views.admin_delete_user, name='admin_delete_user'),
    path('delete_post/<uuid:post_id>/', views.delete_post_view, name='delete_post'),
    path('admin_user_detail/<str:pk>', views.admin_user_detail, name='admin_user_detail'),
    path('admin_user_create/<str:username>/', views.admin_user_create, name='admin_user_create'),
]