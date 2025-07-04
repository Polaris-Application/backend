# Generated by Django 5.2.3 on 2025-06-19 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobile_facilities', '0005_alter_userlocationdata_latitude_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlocationdata',
            name='ec_no',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=25, null=True),
        ),
        migrations.AlterField(
            model_name='userlocationdata',
            name='power',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=25, null=True),
        ),
        migrations.AlterField(
            model_name='userlocationdata',
            name='quality',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=25, null=True),
        ),
        migrations.AlterField(
            model_name='userlocationdata',
            name='rscp',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=25, null=True),
        ),
        migrations.AlterField(
            model_name='userlocationdata',
            name='rsrp',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=25, null=True),
        ),
        migrations.AlterField(
            model_name='userlocationdata',
            name='rsrq',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=25, null=True),
        ),
        migrations.AlterField(
            model_name='userlocationdata',
            name='rssi',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=25, null=True),
        ),
        migrations.AlterField(
            model_name='userlocationdata',
            name='rx_lev',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=25, null=True),
        ),
    ]
