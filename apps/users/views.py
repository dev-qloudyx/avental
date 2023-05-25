import jwt
from django.db.models.query import QuerySet
from django.db.models import Count
from typing import Any, Dict
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetCompleteView, PasswordResetDoneView
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView, TemplateView, ListView
from django.urls import reverse_lazy, reverse
from django.conf import settings
from .models import Profile, User, Upload, Voto
from .forms import UserRegisterForm, UserUpdateForm, ProfileRegisterForm, UploadForm, VotoForm
from .roles import role_required, ADMIN
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django_filters.views import FilterView
from .filters import UploadFilter



def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            reset_password_form = PasswordResetForm(data={'email': email})
            if reset_password_form.is_valid():
                reset_password_form.save(request=request,
                    email_template_name='users/password_define_email.txt',
                    html_email_template_name='users/password_define_email.html')
                messages.success(request,
                    f'Conta criada com sucesso. Consulte a caixa de correio {email} para definir a palavra-passe')
                return redirect('users:login')
            else:
                messages.error(request,
                    'Problemas com o envio de email para definir a password...')
            return redirect('users:login')
        else:
            messages.error(request,
                'Problemas com a criação de conta. Ver informação em baixo...')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, 'A tua conta foi atualizada!')
            return redirect('users:profile')
        else:
            messages.error(request,
                'Problemas a atualizar a tua conta, vê os erros em baixo...')
    else:
        u_form = UserUpdateForm(instance=request.user)
    context = {
        'u_form': u_form,
    }
    return render(request, 'users/profile.html', context)


def login_register(request):
    return render(request, 'users/login_register.html')


class MyPasswordResetCompleteView(PasswordResetCompleteView):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.success(request, 'A sua palavra-passe foi definida com sucesso \
            Faça o login agora.')
        return redirect('users:login')

class MyPasswordResetDoneView(PasswordResetDoneView):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.success(request, 'Um e-mail acabou de ser enviado com as \
            instruções para redefinir a sua senha... Confirme, por favor.')
        return redirect('users:login')

class UploadCreateView(CreateView):
    model = Upload
    form_class = UploadForm

    def get(self, request):
        self.user_id = request.user.id
        return super().get(request)

    def post(self, request):
        self.user_id = request.user.id
        return super().post(request)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs()
        kwargs['user_id'] = self.user_id
        return kwargs

    def get_success_url(self):
        messages.success(self.request, 'Participação Submetida! Deverá consultar o e-mail para validar a participação!')
        return reverse(
            'users:list',
            kwargs={
                'user_id': self.user_id
            })


class UploadDetailView(DetailView):
    model = Upload
    template_name = 'users/detail.html'

    def get_context_data(self, **kwargs: Any):
        ctx = super().get_context_data(**kwargs)
        votos = Voto.objects.filter(upload = self.object.id,validade=True).count()
        ctx['votos'] = votos
        return ctx

class UploadListView(FilterView, ListView):
    model = Upload
    filterset_class = UploadFilter
    template_name = 'users/list.html'

    def get(self,request, user_id):
        self.user_id = request.user.id
        return super().get(request)

    def get_queryset(self):
        return Upload.objects.filter(user=self.user_id, ativo=True).annotate(votos=Count("voto", distinct=True))
    
    def get_context_data(self, **kwargs: Any):
        ctx = super().get_context_data(**kwargs)
        return ctx


class UploadAllListView(FilterView,ListView):
    model = Upload
    filterset_class = UploadFilter
    template_name = 'users/list.html'

    def get_queryset(self):
        return Upload.objects.filter(ativo=True).annotate(votos=Count("voto", distinct=True))


class VotoCreateView(CreateView):
    model = Voto
    form_class = VotoForm

    def get(self,request, upload_id):
        self.upload_id = upload_id
        return super().get(request)

    def post(self,request, upload_id):
        self.upload_id = upload_id
        return super().post(request)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs()
        kwargs['upload_id'] = self.upload_id
        return kwargs
    
    def get_success_url(self):
        messages.success(self.request, 'Voto Submetido! Deverá consultar o seu e-mail para validar o voto!')
        return reverse(
            'users:detail',
            kwargs={
                'pk': self.upload_id
            })

class CheckTokenView(TemplateView):
    def get(self, request, *args, **kwargs):
        token = self.request.GET.get('token')
        if token:
            try:
                decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                vote_id = decoded_token['vote_id']
                voto = Voto.objects.get(id=vote_id)
                if voto.validade:
                    messages.success(self.request, 'Voto já foi Validado!')
                else:
                    messages.success(self.request, 'Voto Validado!')
                    Voto.objects.filter(id=vote_id).update(validade=True)
                upload_id = decoded_token['upload_id']
                redirect_url = reverse('users:detail', kwargs={'pk': upload_id})
                return redirect(redirect_url)
            except jwt.ExpiredSignatureError:
                message = 'Token expirado.'
                messages.error(self.request, message)
                redirect_url = reverse('users:login')
                return redirect(redirect_url)
            except jwt.InvalidTokenError:
                message = 'Token inválido.'
                messages.error(self.request, message)
                redirect_url = reverse('users:login')
                return redirect(redirect_url)
        else:
            message = 'Nenhum Token encontrado.'
            messages.warning(self.request, message)
            redirect_url = reverse('users:login')
            return redirect(redirect_url)
        
        
class CheckTokenUploadView(TemplateView):
    def get(self, request, *args, **kwargs):
        token = self.request.GET.get('token')
        if token:
            try:
                decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                upload_id = decoded_token['upload_id']
                upload = Upload.objects.get(id=upload_id)
                if upload.ativo:
                    messages.success(self.request, 'Upload já foi Validado!')
                else:
                    messages.success(self.request, 'Upload Validado!')
                    Upload.objects.filter(id=upload_id).update(ativo=True)
                redirect_url = reverse('users:list-all')
                return redirect(redirect_url)
            except jwt.ExpiredSignatureError:
                message = 'Token expirado.'
                messages.error(self.request, message)
                redirect_url = reverse('users:login')
                return redirect(redirect_url)
            except jwt.InvalidTokenError:
                message = 'Token inválido.'
                messages.error(self.request, message)
                redirect_url = reverse('users:login')
                return redirect(redirect_url)
        else:
            message = 'Nenhum Token encontrado.'
            messages.warning(self.request, message)
            redirect_url = reverse('users:login')
            return redirect(redirect_url)
