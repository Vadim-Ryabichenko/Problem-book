from django.contrib import admin
from django.urls import path, include
from accountsapp.views import ProblemBookAuthToken



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mainapp.urls')),
    path('accounts/', include('accountsapp.urls')),
    path('api-token-auth/', ProblemBookAuthToken.as_view()),
]
