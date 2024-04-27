from . import views
from django.urls import path

urlpatterns = [
    path('',views.home,name='home'), 
    path('scrape/', views.scrape_data, name='scrape_data'),
    path('plot/', views.plot_graph, name='plot_graph'),
]