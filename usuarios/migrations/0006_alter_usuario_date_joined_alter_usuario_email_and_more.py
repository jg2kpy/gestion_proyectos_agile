# Generated by Django 4.1 on 2022-08-20 23:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0005_alter_usuario_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='date_joined',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
    ]