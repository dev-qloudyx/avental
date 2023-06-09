from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from PIL import Image
from . import roles

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address.')
        if not username:
            raise ValueError('Users must have a username.')
        user = self.model(
            email=self.normalize_email(email),
            username=username
            )
        user.set_password(password)
        user.save()
        return user


    def create_superuser(self, email, username, password=None):
        user = self.create_user(
            email=email,
            username=username,
            password=password
        )
        user.role=roles.ADMIN
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True, verbose_name="E-mail")
    username = models.CharField(max_length=30, unique=True, verbose_name="Nome de Utilizador")
    first_name = models.CharField(max_length=80, blank=True, null=True, verbose_name="Nome")
    last_name = models.CharField(max_length=80, blank=True, null=True, verbose_name="Apelido")
    aceito = models.BooleanField(default=False)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    role = models.PositiveSmallIntegerField(
        choices=roles.TYPES, default=roles.USER)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email' #instead of username
    # USERNAME_FIELD and password are required by default
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def role_is_admin(self):
        return self.role == roles.ADMIN


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.user.username} Profile'


class Upload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True, verbose_name="E-mail")
    first_name = models.CharField(max_length=80, verbose_name="Nome")
    last_name = models.CharField(max_length=80, verbose_name="Apelido")
    imagem = models.ImageField(upload_to='avental_pics', verbose_name="Imagem")
    ativo = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.email}'

class Voto(models.Model):
    email = models.EmailField(unique=True)
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE)
    validade = models.BooleanField(default=False)
    data= models.DateTimeField(verbose_name='data', auto_now_add=True)

    def __str__(self):
        return f'{self.email}'


class Local(models.Model):
    nome = models.CharField(max_length=30)
    cidade = models.CharField(max_length=30)
    
    def __str__(self):
        return f'{self.nome} - {self.cidade}'
