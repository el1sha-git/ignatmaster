from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .models import User


def encrypt_user(user) -> tuple[str, str]:
    """
    Encrypt user info
    @param user: User object
    @return: tuple of encoded_id and token
    """
    encoded_id = urlsafe_base64_encode(force_bytes(user.id))
    token = PasswordResetTokenGenerator().make_token(user)
    return encoded_id, token


def decrypt_user(**kwargs) -> User:
    data = kwargs
    """
    Decrypt user info
    @param encoded_id: Encoded id
    @param token: Token
    @return: User object
    """
    user_id = urlsafe_base64_decode(data['enc_id']).decode()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise ValueError('User does not exist, invalid id')
    if not PasswordResetTokenGenerator().check_token(user, data['token']):
        raise ValueError('Token is invalid')
    return user
