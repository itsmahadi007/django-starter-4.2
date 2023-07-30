from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
async def async_view(request):
    # your code here

    return Response(
        {"message": "This is an asynchronous view!"}, status=status.HTTP_200_OK
    )
