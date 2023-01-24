from django.urls import path
# TODO: nested routers
from .views import UserView, ResetUserPassword, UserRegister, UserActivate

urlpatterns = [
    path('', UserView.as_view(), name='index'),
    path('register/', UserRegister.as_view({'post': 'create'}), name='users_register'),
    path('activate/', UserActivate.as_view(), name='users_activate_query'),
    # path('activate/<str:enc_id>/<str:token>/', UserActivate.as_view(), name='users_activate'),
    path('reset/', ResetUserPassword.as_view(), name='users_reset_query'),
    # path('reset/<str:enc_id>/<str:token>/', ResetUserPassword.as_view(), name='users_reset'),
]
