# Generated by Django 5.0.3 on 2024-04-18 02:35

import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('nombre', models.CharField(max_length=250, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Materia',
            fields=[
                ('nombre', models.CharField(max_length=250, primary_key=True, serialize=False)),
                ('year', models.IntegerField()),
                ('semestre', models.IntegerField()),
                ('activa', models.BooleanField(default=True)),
            ],
            options={
                'unique_together': {('nombre', 'year', 'semestre')},
            },
        ),
        migrations.CreateModel(
            name='Almacen',
            fields=[
            ],
            options={
                'verbose_name_plural': 'Encargados de Almacén',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.user',),
        ),
        migrations.CreateModel(
            name='Prestatario',
            fields=[
            ],
            options={
                'verbose_name_plural': 'Prestatarios',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.user',),
        ),
        migrations.CreateModel(
            name='Maestro',
            fields=[
            ],
            options={
                'verbose_name_plural': 'Maestros',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.user',),
        ),
        migrations.CreateModel(
            name='Coordinador',
            fields=[
            ],
            options={
                'verbose_name_plural': 'Coordinadores',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.user',),
        ),
        migrations.CreateModel(
            name='Articulo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.ImageField(default='default.png', upload_to='')),
                ('nombre', models.CharField(max_length=250)),
                ('codigo', models.CharField(max_length=250)),
                ('descripcion', models.TextField(blank=True, max_length=250, null=True)),
            ],
            options={
                'unique_together': {('nombre', 'codigo')},
            },
        ),
        migrations.CreateModel(
            name='Carrito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inicio', models.DateTimeField(default=django.utils.timezone.now)),
                ('final', models.DateTimeField(default=django.utils.timezone.now)),
                ('prestatario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('materia', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='PEMA.materia')),
            ],
        ),
        migrations.CreateModel(
            name='Orden',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=125)),
                ('inicio', models.DateTimeField()),
                ('final', models.DateTimeField()),
                ('tipo', models.CharField(choices=[('OR', 'Ordinaria'), ('EX', 'Extraordinaria')], default='OR', max_length=2)),
                ('lugar', models.CharField(choices=[('CA', 'CAMPUS'), ('EX', 'EXTERNO')], default='CA', max_length=2)),
                ('estado', models.CharField(choices=[('PC', 'PENDIENTE CORRESPONSABLES'), ('PA', 'PENDIENTE APROBACION'), ('RE', 'RECHAZADA'), ('AP', 'APROBADA'), ('CN', 'CANCELADO')], default='PC', max_length=2)),
                ('emision', models.DateTimeField(auto_now_add=True)),
                ('descripcion_lugar', models.CharField(max_length=125, null=True)),
                ('descripcion', models.TextField(blank=True, max_length=512)),
                ('materia', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='PEMA.materia')),
                ('prestatario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PEMA.prestatario')),
            ],
            options={
                'verbose_name_plural': 'Ordenes',
                'ordering': ('emision',),
            },
        ),
        migrations.CreateModel(
            name='Perfil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.ImageField(default='default.png', upload_to='')),
                ('telefono', phonenumber_field.modelfields.PhoneNumberField(max_length=128, null=True, region=None)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Unidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('AC', 'ACTIVO'), ('IN', 'INACTIVO')], default='AC', max_length=2)),
                ('num_control', models.CharField(max_length=250)),
                ('num_serie', models.CharField(max_length=250)),
                ('articulo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PEMA.articulo')),
            ],
            options={
                'unique_together': {('articulo', 'num_control')},
            },
        ),
        migrations.CreateModel(
            name='ArticuloCarrito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unidades', models.IntegerField(default=1)),
                ('articulo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PEMA.articulo')),
                ('carrito', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PEMA.carrito')),
            ],
            options={
                'unique_together': {('articulo', 'carrito')},
            },
        ),
        migrations.CreateModel(
            name='CategoriaArticulo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('articulo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PEMA.articulo')),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PEMA.categoria')),
            ],
            options={
                'unique_together': {('articulo', 'categoria')},
            },
        ),
        migrations.CreateModel(
            name='Devolucion',
            fields=[
                ('orden', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='PEMA.orden')),
                ('emision', models.DateTimeField(auto_now_add=True)),
                ('almacen', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.almacen')),
            ],
        ),
        migrations.CreateModel(
            name='Entrega',
            fields=[
                ('orden', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='PEMA.orden')),
                ('emision', models.DateTimeField(auto_now_add=True)),
                ('almacen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PEMA.almacen')),
            ],
        ),
        migrations.CreateModel(
            name='AutorizacionOrden',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('PN', 'Pendiente'), ('RE', 'Rechazada'), ('AC', 'Aceptada')], default='PN', max_length=2)),
                ('tipo', models.CharField(choices=[('OR', 'Ordinaria'), ('EX', 'Extraordinaria')], default='OR', max_length=2)),
                ('autorizador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('orden', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PEMA.orden')),
            ],
            options={
                'verbose_name_plural': 'Autorizaciones',
                'unique_together': {('orden', 'autorizador')},
            },
        ),
        migrations.CreateModel(
            name='ArticuloMateria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('articulo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PEMA.articulo')),
                ('materia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PEMA.materia')),
            ],
            options={
                'unique_together': {('materia', 'articulo')},
            },
        ),
        migrations.CreateModel(
            name='UnidadOrden',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orden', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PEMA.orden')),
                ('unidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PEMA.unidad')),
            ],
            options={
                'unique_together': {('unidad', 'orden')},
            },
        ),
        migrations.CreateModel(
            name='UsuarioMateria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('materia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PEMA.materia')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('materia', 'usuario')},
            },
        ),
        migrations.CreateModel(
            name='Reporte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('AC', 'ACTIVO'), ('IN', 'INACTIVO')], default='AC', max_length=2)),
                ('descripcion', models.TextField(blank=True, max_length=250, null=True)),
                ('emision', models.DateTimeField(auto_now_add=True)),
                ('orden', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PEMA.orden')),
                ('almacen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PEMA.almacen')),
            ],
            options={
                'unique_together': {('almacen', 'orden')},
            },
        ),
        migrations.CreateModel(
            name='CorresponsableOrden',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('PN', 'Pendiente'), ('RE', 'Rechazada'), ('AC', 'Aceptada')], default='PN', max_length=2)),
                ('orden', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PEMA.orden')),
                ('prestatario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PEMA.prestatario')),
            ],
            options={
                'unique_together': {('orden', 'prestatario')},
            },
        ),
        migrations.CreateModel(
            name='MaestroMateria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('materia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PEMA.materia')),
                ('maestro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PEMA.maestro')),
            ],
            options={
                'unique_together': {('materia', 'maestro')},
            },
        ),
    ]
