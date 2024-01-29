from .views import MainView, AboutView, TaskCardListView, TaskCardDetailView, TaskCardCreateView, TaskCardUpdateView, TaskCardDeleteView, UpperStatusTaskCardView, LowerStatusTaskCardView, SetExecutorView, TaskCardModelViewSet
from django.urls import path, include
from rest_framework import routers



router = routers.SimpleRouter()
router.register('tasks', TaskCardModelViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
    path('', MainView.as_view(), name = 'mainpage'),
    path('about/', AboutView.as_view(), name = 'aboutpage'),
    path('tasklist/', TaskCardListView.as_view(), name = 'tasks'),
    path('task/<int:pk>/', TaskCardDetailView.as_view(), name = 'task_detail'),
    path('task/create/', TaskCardCreateView.as_view(), name = 'task_create'),
    path('task/<int:pk>/update/', TaskCardUpdateView.as_view(), name = 'task_update'),
    path('task/<int:pk>/delete/', TaskCardDeleteView.as_view(), name = 'task_delete'),
    path('tasks/<int:pk>/upper-status/', UpperStatusTaskCardView.as_view(), name='upper_task_status'),
    path('tasks/<int:pk>/lower-status/', LowerStatusTaskCardView.as_view(), name='lower_task_status'),
    path('tasks/<int:pk>/set-executor/', SetExecutorView.as_view(), name='set_executor'),
]
