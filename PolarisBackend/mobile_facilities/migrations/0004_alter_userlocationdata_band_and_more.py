# Generated by Django 5.2.3 on 2025-06-19 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobile_facilities', '0003_alter_userlocationdata_arfcn_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlocationdata',
            name='band',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='userlocationdata',
            name='latitude',
            field=models.DecimalField(decimal_places=15, max_digits=15),
        ),
        migrations.AlterField(
            model_name='userlocationdata',
            name='longitude',
            field=models.DecimalField(decimal_places=15, max_digits=15),
        ),
    ]
