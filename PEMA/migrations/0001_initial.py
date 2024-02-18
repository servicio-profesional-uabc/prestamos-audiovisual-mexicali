# Generated by Django 5.0 on 2024-02-13 23:23

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Articulo',
            fields=[
                ('codigo', models.CharField(max_length=250, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Carrito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inicio', models.DateTimeField(default=django.utils.timezone.now)),
                ('final', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('nombre', models.CharField(max_length=250, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Almacen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ArticuloCarrito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('articulo', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.articulo')),
                ('carrito', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.carrito')),
            ],
        ),
        migrations.CreateModel(
            name='CategoriaArticulo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('articulo', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.articulo')),
                ('categoria', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.categoria')),
            ],
        ),
        migrations.CreateModel(
            name='Coordinador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Materia',
            fields=[
                ('nombre', models.CharField(max_length=250, primary_key=True, serialize=False)),
                ('periodo', models.CharField(max_length=6)),
            ],
            options={
                'unique_together': {('nombre', 'periodo')},
            },
        ),
        migrations.CreateModel(
            name='ArticuloMateria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('articulo', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.articulo')),
                ('materia', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.materia')),
            ],
        ),
        migrations.CreateModel(
            name='Prestatario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Orden',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('OR', 'ORDINARIA'), ('EX', 'EXTRAORDINARIA')], default='OR', max_length=2)),
                ('lugar', models.CharField(default='', max_length=250)),
                ('emision', models.DateTimeField(default=django.utils.timezone.now)),
                ('recepcion', models.DateTimeField(null=True)),
                ('devolucion', models.DateTimeField(null=True)),
                ('prestatario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.prestatario')),
            ],
        ),
        migrations.AddField(
            model_name='carrito',
            name='prestatario',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.prestatario'),
        ),
        migrations.CreateModel(
            name='Alumno',
            fields=[
                ('matricula', models.CharField(max_length=250, primary_key=True, serialize=False)),
                ('prestatario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.prestatario')),
            ],
            options={
                'unique_together': {('prestatario', 'matricula')},
            },
        ),
        migrations.CreateModel(
            name='Profesor',
            fields=[
                ('num_emplado', models.CharField(max_length=250, primary_key=True, serialize=False)),
                ('prestatario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.prestatario')),
            ],
        ),
        migrations.CreateModel(
            name='Reporte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('AC', 'ACTIVO'), ('IN', 'INACTIVO')], default='AC', max_length=2)),
                ('descripcion', models.TextField(blank=True, max_length=250, null=True)),
                ('orden', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.orden')),
            ],
        ),
        migrations.CreateModel(
            name='Unidad',
            fields=[
                ('codigo', models.CharField(max_length=250, primary_key=True, serialize=False)),
                ('estado', models.CharField(choices=[('AC', 'ACTIVO'), ('IN', 'INACTIVO')], default='AC', max_length=2)),
                ('articulo', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.articulo')),
            ],
        ),
        migrations.CreateModel(
            name='AlumnoMateria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alumno', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.alumno')),
                ('materia', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.materia')),
            ],
            options={
                'unique_together': {('alumno', 'materia')},
            },
        ),
        migrations.CreateModel(
            name='AutorizacionCoordinador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('autorizar', models.BooleanField(default=False)),
                ('coordinador', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.coordinador')),
                ('orden', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.orden')),
            ],
            options={
                'unique_together': {('orden', 'coordinador')},
            },
        ),
        migrations.CreateModel(
            name='AutorizacionAlmacen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('autorizar', models.BooleanField(default=False)),
                ('almacen', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.almacen')),
                ('orden', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.orden')),
            ],
            options={
                'unique_together': {('orden', 'almacen')},
            },
        ),
        migrations.CreateModel(
            name='ProfesorMateria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('materia', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.materia')),
                ('profesor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.profesor')),
            ],
            options={
                'unique_together': {('profesor', 'materia')},
            },
        ),
    ]