# Generated by Django 4.1.5 on 2023-04-02 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carousel',
            name='banner',
            field=models.ImageField(blank=True, null=True, upload_to='carousel/', verbose_name='Баннер'),
        ),
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='categories/', verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='products/', verbose_name='Главное Изображение'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(help_text='Будут отображены на странице описания товара', upload_to='products/', verbose_name='Доп. Изображения'),
        ),
    ]
