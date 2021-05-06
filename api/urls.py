from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.handle_login, name="login"),
    path('logout/', views.handle_logout, name="logout"),
    path('posts', views.posts),
    path('posts/last_hour', views.last_hour_posts, name="last_hour_posts"),
    path('posts/list', views.post_list, name='post_list'),
    path('register/', views.register, name="register"),
    path('statistics', views.statistics, name="statistics"),
    path('stringCount', views.stringCount),
    path('utente/<int:pk>/', views.user_page, name="user_page"),
]
