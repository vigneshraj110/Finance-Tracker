from django.urls import path
from django.conf import settings
from . import views
from django.conf.urls.static import static
from .views import register,summary, user_login, user_logout, home, welcome, predict
urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('welcome/', welcome, name='welcome'),
    path('summary/', summary, name='summary'),
    path('predict/', predict, name='predict'),
    path('download-items/', views.download_items_csv, name='download_items_csv'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urls.py



