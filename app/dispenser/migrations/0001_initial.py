# Generated by Django 3.2.5 on 2021-07-13 18:06

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='IPSubnet',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.GenericIPAddressField(
                    unique=True, verbose_name='адрес подсети')),
                ('gateway', models.GenericIPAddressField(
                    verbose_name='адрес шлюза')),
                ('mask', models.IntegerField(validators=[django.core.validators.MinValueValidator(
                    0), django.core.validators.MaxValueValidator(128)], verbose_name='маска подсети')),
                ('protocol', models.CharField(choices=[
                 ('v4', 'IPv4'), ('v6', 'IPv6')], max_length=2, verbose_name='протокол')),
            ],
            options={
                'verbose_name': 'Подсеть IP',
                'verbose_name_plural': 'Подсети IP',
                'ordering': ['address'],
            },
        ),
        migrations.CreateModel(
            name='IPAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.GenericIPAddressField(
                    unique=True, verbose_name='адрес')),
                ('claimed_at', models.DateTimeField(
                    auto_now=True, verbose_name='дата выдачи')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                 related_name='ip_addresses', to=settings.AUTH_USER_MODEL, verbose_name='владелец')),
                ('subnet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                 related_name='addresses', to='dispenser.ipsubnet', verbose_name='подсеть')),
            ],
            options={
                'verbose_name': 'IP-адрес',
                'verbose_name_plural': 'IP-адреса',
            },
        ),
    ]
