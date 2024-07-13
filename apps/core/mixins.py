from rest_framework.permissions import IsAuthenticated

class AuthenticatedAccessMixin:
    permission_classes = (IsAuthenticated, )
