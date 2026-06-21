from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from splitter import views as splitter_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', splitter_views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='splitter/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('splitter.urls')),
]
