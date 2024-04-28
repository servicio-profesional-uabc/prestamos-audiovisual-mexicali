# Generated by Django 5.0.3 on 2024-04-28 04:07

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
            name='Articulo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.ImageField(default='default.png', upload_to='')),
                ('nombre', models.CharField(max_length=250)),
                ('codigo', models.CharField(blank=True, max_length=250)),
                ('descripcion', models.TextField(blank=True, max_length=250, null=True)),
            ],
        ),
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
                ('_alumnos', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
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
            name='ArticuloCarrito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unidades', models.IntegerField(default=0)),
                ('articulo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PEMA.articulo')),
            ],
        ),
        migrations.CreateModel(
            name='Carrito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inicio', models.DateTimeField(default=django.utils.timezone.now)),
                ('final', models.DateTimeField(default=django.utils.timezone.now)),
                ('_articulos', models.ManyToManyField(blank=True, to='PEMA.articulocarrito')),
            ],
        ),
        migrations.AddField(
            model_name='articulocarrito',
            name='propietario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='PEMA.carrito'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='_categorias',
            field=models.ManyToManyField(blank=True, to='PEMA.categoria'),
        ),
        migrations.CreateModel(
            name='Orden',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=250, verbose_name='Nombre Producción')),
                ('tipo', models.CharField(choices=[('OR', 'Ordinaria'), ('EX', 'Extraordinaria')], default='OR', max_length=2, verbose_name='Tipo de la Solicitud')),
                ('lugar', models.CharField(choices=[('CA', 'En el Campus'), ('EX', 'Fuera del Campus')], default='CA', max_length=2, verbose_name='Lugar de la Producción')),
                ('descripcion_lugar', models.CharField(max_length=125, null=True, verbose_name='Lugar Especifico')),
                ('estado', models.CharField(choices=[('AP', 'Listo para iniciar'), ('PC', 'Esperando corresponsables'), ('PA', 'Esperando autorización'), ('RE', 'Rechazada'), ('CN', 'Cancelada'), ('EN', 'Activa'), ('DE', 'Terminado')], default='PC', max_length=2)),
                ('inicio', models.DateTimeField()),
                ('final', models.DateTimeField()),
                ('descripcion', models.TextField(max_length=512, verbose_name='Descripción de la Producción')),
                ('emision', models.DateTimeField(auto_now_add=True)),
                ('prestatario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Emisor')),
                ('materia', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='PEMA.materia')),
            ],
            options={
                'verbose_name_plural': 'Ordenes',
                'ordering': ('emision',),
            },
        ),
        migrations.AddField(
            model_name='materia',
            name='_articulos',
            field=models.ManyToManyField(blank=True, to='PEMA.articulo'),
        ),
        migrations.AddField(
            model_name='materia',
            name='_maestros',
            field=models.ManyToManyField(related_name='materias_profesor', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='carrito',
            name='materia',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='PEMA.materia'),
        ),
        migrations.CreateModel(
            name='Perfil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telefono', phonenumber_field.modelfields.PhoneNumberField(max_length=128, null=True, region=None)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Reporte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('AC', 'ACTIVO'), ('IN', 'INACTIVO')], default='AC', max_length=2)),
                ('descripcion', models.TextField(blank=True, max_length=250, null=True)),
                ('emision', models.DateTimeField(auto_now_add=True)),
                ('emisor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('orden', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='reportes', to='PEMA.orden')),
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
                'verbose_name_plural': 'Unidades',
                'unique_together': {('articulo', 'num_control')},
            },
        ),
        migrations.AddField(
            model_name='orden',
            name='_unidades',
            field=models.ManyToManyField(blank=True, to='PEMA.unidad', verbose_name='Equipo Solicitado'),
        ),
        migrations.AddField(
            model_name='orden',
            name='_corresponsables',
            field=models.ManyToManyField(related_name='corresponsables', to='PEMA.prestatario', verbose_name='Participantes'),
        ),
        migrations.AddField(
            model_name='carrito',
            name='_corresponsables',
            field=models.ManyToManyField(blank=True, related_name='corresponsables_carrito', to='PEMA.prestatario'),
        ),
        migrations.AddField(
            model_name='carrito',
            name='prestatario',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='PEMA.prestatario'),
        ),
        migrations.AlterUniqueTogether(
            name='articulo',
            unique_together={('nombre', 'codigo')},
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
                ('entregador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
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
        migrations.AlterUniqueTogether(
            name='materia',
            unique_together={('nombre', 'year', 'semestre')},
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
    ]
