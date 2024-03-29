# Generated by Django 5.0.1 on 2024-01-06 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voteapp', '0004_rename_vote_subscribe_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidate',
            name='name',
        ),
        migrations.AddField(
            model_name='candidate',
            name='picture',
            field=models.ImageField(null=True, upload_to='photos/'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='vote_count',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='tagline',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
