
from django.urls import path
from .views import HomeView,ArticleDetailView
from . import views

urlpatterns = [
    # path('',views.home,name='home'),
    path('home/',HomeView.as_view(),name='blog-home'), 
    path('article/<int:pk>',ArticleDetailView.as_view(),name='article-detail'),
    path('add_post/',views.create_blog_post,name='add-post'),
    
]