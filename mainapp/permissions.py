from rest_framework.permissions import BasePermission



class TaskCardPermission(BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create' or view.action == 'list':
            return request.user.is_authenticated 
        return True
    
    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return request.user.is_authenticated 
        elif view.action == 'destroy':
            return request.user == obj.creator or request.user.is_superuser
        elif view.action in ['update', 'partial_update']:
            return request.user.is_authenticated 
        return False
    