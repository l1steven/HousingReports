# Generated by Django 4.2.11 on 2024-04-14 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_attachments', '0002_auto_20181103_1404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
