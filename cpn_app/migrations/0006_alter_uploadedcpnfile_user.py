# Generated by Django 4.2.14 on 2025-01-27 01:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cpn_app', '0005_alter_uploadedcpnfile_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedcpnfile',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
