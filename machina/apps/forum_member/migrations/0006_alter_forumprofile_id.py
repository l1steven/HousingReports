# Generated by Django 4.2.11 on 2024-04-14 19:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("forum_member", "0005_auto_20200423_1049"),
    ]

    operations = [
        migrations.AlterField(
            model_name="forumprofile",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
