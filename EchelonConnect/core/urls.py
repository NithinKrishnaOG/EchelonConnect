from django.urls import path
from . import views
from .views import PasswordsChangeView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('settings', views.settings, name='settings'),
    path('upload', views.upload, name='upload'),
    path('uploadtext', views.uploadtext, name='uploadtext'),
    path('follow', views.follow, name='follow'),
    path('search', views.search, name='search'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('like-post', views.like_post, name='like-post'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
    path('chat/<str:receiver_username>/', views.chat, name='chat'),
    path('password/', PasswordsChangeView.as_view(template_name='user_password_reset.html')),
    path('password_success/', views.password_success, name="password_success"),


    path('password_reset/', auth_views.PasswordResetView.as_view(), name="password_reset"),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),


    path('report/post/<uuid:post_id>/', views.report_post_view, name='report_post'),
    path('edit-post/<uuid:post_id>/', views.edit_post, name='edit_post'),
    path('deletepost/<uuid:post_id>/', views.deletepost, name='deletepost'),


]
