# Generated by Django 5.2 on 2025-06-15 00:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfil',
            name='imagen',
            field=models.ImageField(default='static/perfiles/perfil_defecto.jpg', upload_to='static/perfiles/'),
        ),
    ]
