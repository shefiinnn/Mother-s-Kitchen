# Generated by Django 5.1.7 on 2025-03-15 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0010_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='foodpost',
            name='image1',
            field=models.ImageField(default='file/button.png', upload_to='file'),
        ),
        migrations.AddField(
            model_name='foodpost',
            name='image2',
            field=models.ImageField(default='file/ealogo.jpg', upload_to='file'),
        ),
    ]
