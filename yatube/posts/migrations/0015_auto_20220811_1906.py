# Generated by Django 2.2.16 on 2022-08-11 19:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_auto_20220712_0940'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('created',), 'verbose_name': 'Комментарий поста', 'verbose_name_plural': 'Комментарии постов'},
        ),
    ]
