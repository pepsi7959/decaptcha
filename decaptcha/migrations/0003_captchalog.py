# Generated by Django 3.2.11 on 2022-01-26 01:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('decaptcha', '0002_alter_captchausage_using_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaptchaLog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('partner_id', models.IntegerField()),
                ('decode_value', models.CharField(blank=True, max_length=20)),
                ('status', models.IntegerField(default=0)),
                ('image', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]