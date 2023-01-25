from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, status

from .models import User
from .serializers import UserSerializer, UsernameSerializer, TokenSerializer, \
    ResetPasswordSerializer
from app.settings import FRONTEND_URL
from .utils import encrypt_user, decrypt_user
from .mixins import SerializerByMethodMixin
from .tasks import send_email as send_email_task
from app.celery import debug_task


class UserView(mixins.RetrieveModelMixin, GenericAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get(id=self.request.user.id)
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request):
        serializer = self.get_serializer(request.user)
        return self.retrieve(serializer)


class UserRegister(GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommonUserActivateReset(SerializerByMethodMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                              GenericAPIView):
    serializer_map = {
        'POST': UsernameSerializer,
        'PATCH': UserSerializer
    }
    queryset = User.objects.all()

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(username=serializer.validated_data['username'])
            enc_id, token = encrypt_user(user)
            self.send_mail(enc_id=enc_id, token=token, user=user)
        except User.DoesNotExist:
            pass

        return Response({'message': 'if user exist, activate link will be send'}, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = self.patch_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = decrypt_user(**serializer.validated_data)
        self.patch_action(user, **serializer.validated_data)
        serialized_user = self.get_serializer(user)
        return Response(serialized_user.data, status=status.HTTP_200_OK)

    def send_mail(self, **kwargs):
        pass

    def patch_action(self, user, **kwargs):
        pass

    def patch_serializer(self, data):
        pass


class UserActivate(CommonUserActivateReset):

    def patch_serializer(self, data):
        return TokenSerializer(data=data)

    def patch_action(self, user, **kwargs):
        user.is_active = True
        user.save()

    def send_mail(self, **kwargs):
        enc_id, token, user = kwargs['enc_id'], kwargs['token'], kwargs['user']
        url = f"{FRONTEND_URL}/activate?enc_id={enc_id}&token={token}"
        body = f"Hello {user.username}\nActivate account  link: \n{url}"
        subject = 'Activate account on IgnatMaster'
        send_email_task.delay(body, subject, [user.username])


class ResetUserPassword(CommonUserActivateReset):

    def patch_serializer(self, data):
        return ResetPasswordSerializer(data=data)

    def patch_action(self, user, **kwargs):
        user.set_password(kwargs['password'])
        user.save()

    def send_mail(self, **kwargs):
        enc_id, token, user = kwargs['enc_id'], kwargs['token'], kwargs['user']
        url = f"{FRONTEND_URL}/reset-password?enc_id={enc_id}&token={token}"
        body = f"Hello {user.username}\nReset password link: \n{url}"
        subject = 'Reset password from IgnatMaster'
        send_email_task.delay(body, subject, [user.username])
        debug_task.delay()
