from dj_rest_auth.views import LoginView
from rest_framework import status
from rest_framework.response import Response


class CustomLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)

        self.login()
        if not self.user.email_verified:
            return Response(
                {"error": "User email is not verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return self.get_response()
