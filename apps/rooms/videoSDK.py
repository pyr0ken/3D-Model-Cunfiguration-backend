from django.conf import settings
from django.utils import timezone
import jwt
import datetime
import requests


def generate_token(is_owner):
    expiration_in_seconds = 7200
    expiration = timezone.now() + datetime.timedelta(seconds=expiration_in_seconds)

    permissions = ['allow_join']

    if is_owner:
        permissions.append('allow_mod')

    token = jwt.encode(payload={
        'exp': expiration,
        'apikey': settings.VIDEOSDK_API_KEY,
        'permissions': permissions,  # 'ask_join' || 'allow_mod'
        'version': 2,  # OPTIONAL
        # 'roomId': '2kyv - gzay - 64pg',  # OPTIONAL
        # 'participantId': 'lxvdplwt',  # OPTIONAL
        # 'roles': ['crawler', 'rtc'],  # OPTIONAL
    }, key=settings.VIDEOSDK_SECRET_KEY, algorithm='HS256')

    return token


def create_room(token):
    headers = {"Authorization": token, 'Content-Type': 'application/json'}
    response = requests.post(
        settings.VIDEOSDK_API_ENDPOINT + "/rooms", headers=headers)
    return response.json()
