# Generated by Django 3.2.6 on 2021-09-13 04:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import play.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(blank=True, max_length=50)),
                ('town', models.CharField(blank=True, max_length=50)),
                ('street', models.CharField(blank=True, max_length=50)),
                ('street_number', models.CharField(blank=True, max_length=10)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50)),
                ('rent_cost', models.FloatField(blank=True, null=True)),
                ('photo', models.ImageField(blank=True, default='field_default.jpg', upload_to=play.models.media_path_field)),
                ('show', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('address', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='play.addressfield')),
            ],
        ),
        migrations.CreateModel(
            name='FootballType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('duration', models.IntegerField()),
                ('max_players', models.IntegerField()),
                ('min_players', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(blank=True, choices=[('femenino', 'Femenino'), ('masculino', 'Masculino')], max_length=50)),
                ('nationality', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('dominant_food', models.CharField(blank=True, choices=[('derecho', 'Derecho'), ('izquierdo', 'Izquierdo')], max_length=50)),
                ('photo', models.ImageField(blank=True, default='avatar_default.png', upload_to=play.models.media_path, validators=[play.models.validate_media_size])),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('players', models.ManyToManyField(blank=True, related_name='teams', to='play.Player')),
            ],
        ),
        migrations.AddField(
            model_name='player',
            name='position',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='players', to='play.position'),
        ),
        migrations.AddField(
            model_name='player',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='players', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('category', models.CharField(choices=[('varonil', 'Varonil'), ('femenil', 'Femenil'), ('mixto', 'Mixto')], max_length=30)),
                ('active', models.BooleanField(default=True)),
                ('accepted', models.BooleanField(blank=True, default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='play.field')),
                ('organizer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='matches', to=settings.AUTH_USER_MODEL)),
                ('team', models.ManyToManyField(related_name='matches', to='play.Team')),
            ],
        ),
        migrations.CreateModel(
            name='Manager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(blank=True, default='manager_default.png', upload_to=play.models.media_path, validators=[play.models.validate_media_size])),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('field', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='managers', to='play.field')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='managers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='field',
            name='fields_services',
            field=models.ManyToManyField(blank=True, related_name='fields', to='play.Service'),
        ),
        migrations.AddField(
            model_name='field',
            name='football_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='play.footballtype'),
        ),
    ]
