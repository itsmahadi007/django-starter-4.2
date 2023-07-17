from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.social_serializers import TwitterLoginSerializer


class TwitterLogin(SocialLoginView):
    serializer_class = TwitterLoginSerializer
