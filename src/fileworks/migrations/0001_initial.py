# Generated by Django 4.0.4 on 2022-05-09 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DfUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ptss', models.IntegerField()),
                ('time', models.IntegerField()),
                ('exp', models.IntegerField()),
                ('t2ies', models.IntegerField()),
                ('cset', models.IntegerField()),
            ],
        ),
    ]
