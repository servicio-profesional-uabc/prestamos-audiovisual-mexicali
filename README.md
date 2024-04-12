# Sistema PEMA
PEMA es un programa diseñado para facilitar la gestión de préstamos de material de grabación audiovisual en la Facultad de Artes, campus Mexicali.

## Documentación Completa
Toda la información detallada sobre el proyecto está disponible en la [sección de wiki](https://github.com/servicio-profesional-uabc/prestamos-audiovisual-mexicali/wiki). Esta documentación proporciona una guía completa para comprender y utilizar el sistema PEMA.

## Configuración del Entorno de Desarrollo
Puedes encontrar instrucciones más detalladas [aquí](https://github.com/servicio-profesional-uabc/prestamos-audiovisual-mexicali/wiki/Entorno-de-desarrollo).


### Linux (Ubuntu)
```sh
git clone https://github.com/servicio-profesional-uabc/prestamos-audiovisual-mexicali.git
cd prestamos-audiovisual-mexicali/

python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python manage.py makemigrations PEMA
python manage.py migrate
python manage.py crear_roles
python manage.py developer_setup
python manage.py crear_orden *ideal para probar historial y detalles de orden. crea 6 ordenes con caracteristicas diferentes sin articulos, 2 materias y 1 usuario*

python manage.py runserver
```

### Windows
```sh
git clone https://github.com/servicio-profesional-uabc/prestamos-audiovisual-mexicali.git
cd prestamos-audiovisual-mexicali/

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations PEMA
python manage.py migrate
python manage.py crear_roles
python manage.py developer_setup
python manage.py crear_orden

python manage.py runserver
```


