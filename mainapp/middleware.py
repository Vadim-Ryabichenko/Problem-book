from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import logout



class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated and not request.user.is_superuser:
            last_activity_str = request.session.get('last_activity')
            if not last_activity_str or (timezone.now() - timezone.datetime.fromisoformat(last_activity_str)).seconds > 60:
                logout(request)
                messages.warning(request, 'You have been inactive for more than 1 minute. You have been automatically logged out')
        request.session['last_activity'] = timezone.now().isoformat()

        return response