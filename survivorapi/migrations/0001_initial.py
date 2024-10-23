# Generated by Django 5.1.1 on 2024-10-23 03:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season_number', models.IntegerField()),
                ('name', models.CharField(max_length=100, null=True)),
                ('is_current', models.BooleanField(default=False)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('location', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SeasonLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=50)),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survivorapi.season')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Survivor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('img_url', models.URLField()),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survivorapi.season')),
            ],
        ),
        migrations.CreateModel(
            name='SurvivorLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('is_juror', models.BooleanField(default=False)),
                ('episode_voted_out', models.IntegerField(blank=True, null=True)),
                ('is_user_winner_pick', models.BooleanField(default=False)),
                ('is_season_winner', models.BooleanField(default=False)),
                ('survivor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survivorapi.survivor')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FavoriteSurvivor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survivorapi.season')),
                ('survivor_log', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survivorapi.survivorlog')),
            ],
        ),
        migrations.CreateModel(
            name='SurvivorNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('survivor_log', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survivorapi.survivorlog')),
            ],
        ),
        migrations.CreateModel(
            name='Tribe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('color', models.CharField(max_length=50)),
                ('is_merge_tribe', models.BooleanField(default=False)),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survivorapi.season')),
            ],
        ),
        migrations.CreateModel(
            name='SurvivorTribe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('survivor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survivorapi.survivor')),
                ('tribe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survivorapi.tribe')),
            ],
        ),
    ]
