from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserInvite
from apps.accounts.serializers import AcceptInviteSerializer, PublicInviteSerializer


class PublicInviteDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            invite = UserInvite.objects.get(token=token)
        except UserInvite.DoesNotExist:
            return Response({"detail": "Invite not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(PublicInviteSerializer(invite).data)


class AcceptInviteView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, token):
        try:
            invite = UserInvite.objects.get(token=token)
        except UserInvite.DoesNotExist:
            return Response({"detail": "Invite not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AcceptInviteSerializer(
            data=request.data,
            context={"invite": invite},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(
            {"message": "Invite accepted successfully"},
            status=status.HTTP_201_CREATED,
        )
