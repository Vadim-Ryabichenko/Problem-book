from datetime import timedelta
from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from django.utils import timezone



class ProblemBookTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        time_now = (timezone.now() - timedelta(minutes=100)).replace(tzinfo=None)
        if user.is_superuser:
            token.created = timezone.now()
            token.save()
        elif token.created.replace(tzinfo=None) < time_now:
            token.delete()
            raise exceptions.AuthenticationFailed("Your token has expired")
        else:
            token.created = timezone.now()
            token.save()

        return user, token
    


