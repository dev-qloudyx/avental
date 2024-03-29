from django.urls import path, reverse_lazy
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from .views import register, profile, stats, login_register, CheckTokenUploadView, UploadCreateView, UploadDetailView, VotoCreateView, CheckTokenView, UploadListView, UploadAllListView

app_name = "users"

urlpatterns = [
    path('register/', register, name='register'),
    path('stats/', stats, name='stats'),
    path('profile/', profile, name='profile'),
    path('upload/', UploadCreateView.as_view(), name='upload'),
    path('upload/<int:pk>/', UploadDetailView.as_view(), name='detail'),
    path('', UploadAllListView.as_view(), name='list-all'),
    path('list/<int:user_id>', UploadListView.as_view(), name='list'),
    # path('voto/<int:upload_id>/', VotoCreateView.as_view(), name='voto'),
    path('check-token/', CheckTokenView.as_view(), name='check-token'),
    path('check-token-upload/', CheckTokenUploadView.as_view(), name='check-token-upload'),
    path('login_register/', login_register, name='login-register'),
    path(
        'login',
        LoginView.as_view(
            template_name='users/login.html',
            redirect_authenticated_user=True
        ),
        name='login'
    ),
    path('logout/',
        LogoutView.as_view(template_name='users/logout.html'),
        name='logout'),
    path(
        'password-reset/',
        PasswordResetView.as_view(
            template_name='users/password_reset.html',
            email_template_name='users/password_reset_email.html',
            success_url=reverse_lazy('users:list-all')
        ),
        name='password_reset'
    ),
    path(
        'password-reset/done',
        PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>',
        PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            success_url=reverse_lazy('users:login')
        ),
        name='password_reset_confirm'
    ),
    path(
        'password-reset-complete',
        PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete'
    )
]
