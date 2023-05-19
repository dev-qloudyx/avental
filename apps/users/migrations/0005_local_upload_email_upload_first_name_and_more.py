# Generated by Django 4.2.1 on 2023-05-18 15:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_voto'),
    ]

    operations = [
        migrations.CreateModel(
            name='Local',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=30)),
                ('cidade', models.CharField(max_length=30)),
            ],
        ),
        migrations.AddField(
            model_name='upload',
            name='email',
            field=models.EmailField(default='rodrigo@gmail.com', max_length=254, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='upload',
            name='first_name',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='Nome'),
        ),
        migrations.AddField(
            model_name='upload',
            name='last_name',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='Apelido'),
        ),
        migrations.AlterField(
            model_name='upload',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]