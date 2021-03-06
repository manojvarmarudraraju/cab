# Generated by Django 2.0.5 on 2019-02-25 22:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hiring', '0002_auto_20190225_2234'),
    ]

    operations = [
        migrations.CreateModel(
            name='drivercar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hiring.HiredCar')),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hiring.Driverdb')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='drivercar',
            unique_together={('driver', 'car')},
        ),
    ]
