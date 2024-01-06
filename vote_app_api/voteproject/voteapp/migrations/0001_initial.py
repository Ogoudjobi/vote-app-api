# Generated by Django 5.0.1 on 2024-01-06 00:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Election',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('election_date', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Voter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_valid', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('tagline', models.CharField(max_length=250)),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='voteapp.election')),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=100, unique=True)),
                ('has_voted', models.BooleanField(default=False)),
                ('vote_date', models.DateTimeField(blank=True, null=True)),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='voteapp.election')),
                ('voter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='voteapp.voter')),
            ],
        ),
    ]