# Generated by Django 4.2.17 on 2024-12-11 14:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Advisor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
                ('phone', models.CharField(max_length=20)),
                ('mail', models.CharField(max_length=48)),
            ],
        ),
        migrations.CreateModel(
            name='Watcher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('active', models.BooleanField(default=True)),
                ('currency', models.CharField(choices=[('USD', 'US Dollar'), ('NIS', 'New Israeli Shekel'), ('EUR', 'Euro')], max_length=3)),
                ('type', models.CharField(choices=[('Investment', 'Investment'), ('Birthday', 'Birthday')], max_length=20)),
                ('advisor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='watchers', to='dashboard.advisor')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='watchers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('type', models.CharField(choices=[('Statement', 'Statement'), ('Distribution', 'Distribution'), ('Wire Receipt', 'Wire Receipt'), ('Commitment', 'Commitment')], max_length=20)),
                ('value', models.DecimalField(decimal_places=2, max_digits=20)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='dashboard.watcher')),
            ],
        ),
    ]
