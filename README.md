![escudo-uabc-2022-color-cont](https://github.com/servicio-profesional-uabc/prestamos-audiovisual-mexicali/assets/78140218/278844f1-a8bf-43fd-b276-8fc5c6386be2)

# Sistema PEMA
PEMA es un programa diseñado para facilitar la gestión de préstamos de material de grabación audiovisual en la Facultad de Artes, campus Mexicali. El objetivo principal de este software es proporcionar una plataforma eficiente que permita a alumnos, profesores y personal administrativo realizar solicitudes, autorizaciones y dar seguimiento a los préstamos de manera efectiva.

## Configuración del Entorno de Desarrollo
### Linux (Ubuntu)
Puedes encontrar instrucciones más detalladas [aquí](https://github.com/servicio-profesional-uabc/prestamos-audiovisual-mexicali/wiki/Entorno-de-desarrollo).

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

python manage.py runserver
```

### Windows 
```sh
git clone https://github.com/servicio-profesional-uabc/prestamos-audiovisual-mexicali.git
cd prestamos-audiovisual-mexicali/

python -m venv .venv
./.venv/Scripts/activate
pip install -r requirements.txt

python manage.py makemigrations PEMA
python manage.py migrate
python manage.py crear_roles
python manage.py developer_setup

python manage.py runserver
```


## Documentación Completa
Toda la información detallada sobre el proyecto está disponible en la [sección de wiki](https://github.com/servicio-profesional-uabc/prestamos-audiovisual-mexicali/wiki). Esta documentación proporciona una guía completa para comprender y utilizar el sistema PEMA.
