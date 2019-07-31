# Instalación del proyecto Bots 2.0

## Requisitos:

*   Python 2.7
*   pip
*   Apache2
*   virtualenv
*   Redis server v=3.2.6

Si necesita instalar estos requisitos puede ejecutar los siguientes comandos:

`apt-get install python-pip`

`apt-get install python-dev`

## Instalacion de Redis.

* Ver: [Guía de instalacción Debian](https://blog.programster.org/debian-8-install-redis-server)
* Ver: [Guía de Instalación Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-redis-on-ubuntu-16-04)

## Configuración de Redis
1. cd utils
1. ./install_server.sh
1. Seguir las instrucciones-.
1. Habilitar celery en arranque:
`systemctl enable redis_6379`
1. Cambair el `maxmemory` de acuerdo a la memoria disponible.
1. Cambiar el `maxmemory-policy` a `volatile-lru`
1. Cambiar el valor de `stop-writes-on-bgsave-error` a `no`






## Instalación.
 * Clonar el proyecto
 * Verificar la versión de pip

 `pip --version`

* En caso de que la version del pip sea menor  a 10.0.1 debemos realizar un update del mismo.

`pip install -U pip`

`pip install --upgrade setuptools`

* Instalar requirements.txt 

 `pip install -r requirements.txt`

* Copiar el archivo config_example.py con el nombre config.py

* Realizar pruebas
 
### Enviroments
------
------
#### Development
> **NOTA**: Para configuracion de servidores se debe saltar el proceso de instalacion e inicializacion de un ambiente virtual y proceder al clonado del proyecto en la ruta base.

* Instalar virtualenv

`apt-get install python-virtualenv` 

* creamos el ambiente virtual para el proyecto.

`virtualenv *nombre_ambiente*`

* Nos movemos a la carpeta del ambiente 

`cd *nombre_ambiente*`

* lo iniciamos y realizamos la clonación del proyecto bots 2.0

`source bin/activate`

* Desde la ruta del proyecto clonado ejecutarlo:

`python manage.py runserver`

* Ejecutar el Celery (en paralelo)

`celery worker -c 1 -A app.celery --loglevel=info -B`

-----
-----
#### Production

##### Despliegue
_**Despachador**_

Se puede emplear cualquier despachador, para apache o nginx

**Nginx**
* Instalar Nginx
`apt-get install nginx`
* Instalar gunicorn con pip
`pip install gunicorn`

* Crear el service indicando el directorio dobnde se clonó y donde está instalado gunicoirn:

`nano /etc/systemd/system/bots.service`

```
[Unit]
Description=Gunicorn instance to serve bots
After=network.target


[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/html
ExecStart=/usr/local/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 -m 007 wsgi:app


[Install]
WantedBy=multi-user.target

```


* Iniciar y habilitar el servicio

`systemctl start bots`

`systemctl enable bots`

* Crear Site de nginx

`nano /etc/nginx/sites-available/bots`

```
server {
    listen 80;
    server_name IP_SERVER;

    location / {
        include proxy_params;
        proxy_pass http://IP_SERVER:5000;
    }
}
```

* Crear enlace simbólico de site

`ln -s /etc/nginx/sites-available/bots /etc/nginx/sites-enabled`

* Test sintaxis

`nginx -t`

Esto debe mostrar:

* Reiniciar nginx

`systemctl restart nginx`

```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

##### Información de debug:
* Para que se detecten los cambios:

`service nginx restart`

`systemctl stop bots`

`systemctl daemon-reload`

`systemctl start bots`

`systemctl enable bots`

*To do*: login de error para app.

**Apache**

* Instalar apache
`apt install apache2`
* Instalar wsgi
`apt install libapache2-mod-wsgi`
* Copiar el archivo index_example.wsgi 
`cp index_example.wsgi index.wsgi`
* Reemplazar en index.qsgi la ruta del archivo por la ruta de tu proyecto:
`sys.path.insert(0,"/path/to/project")`
* Crear virtual host
`touch /etc/apache2/sites-available/bots.conf`
`nano /etc/apache2/sites-available/bots.conf`

```
<VirtualHost *:80>
    ServerAdmin webmaster@localhost

    WSGIDaemonProcess botsapp user=www-data group=www-data processes=10 threads=100 request-timeout=100 home=/path/to/project
    WSGIScriptAlias / /path/to/project/index.wsgi

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined

    <Directory /path/to/project>
        WSGIProcessGroup botsapp
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
</VirtualHost>http://192.168.10.220/bitinka_1.0/Bots2.0/edit/master/README.md#preview

```
* Habilitar site
`a2ensite bots.conf`
* Reiniciar Apache
`service apache2 restart`

* Verificar status de los bots
`celeryd run status`

* Reiniciar los bots
`celeryd restart`

* Iniciar los bots
`celeryd start`

* Parar los bots
`celeryd stop`

* Killear los procesos de bots
`celeryd kill`

> **NOTA**: Si se hace un cambio de código, los bots se tienen que reiniciar. Este cambio puede tomar bastante dependiendo de la cantidad de workers. Tambien se puede utilizar celeryd kill y celeryd start, pero se tiene que hacer pruebas.



##### Información de debug:

* Detectar cambios realizados `service apache2 restart`
* Log de celery `tail -f {APACHE_LOG_DIR}/celery/info.log`




##### Consideraciones con el Celery:

El log de celery es muy importante puesto que nos indica el status en tiempo real de la aplicación. Si el log comienza a mostrar información de MySQL reiterativo, comunicarlo a BD, si se muestra 
el mensaje 'Redis is loading the dataset in memory', comunicarselo a Infraestructura. Si se muestra 'pidbox() received method ping() [reply_to: {u routing_key: 9ba1e5-2501-3e60-b7e4-b7e7f135a15e, 
u exchange: u reply.celery.pidbox() } ticket: e5123012as-sa1-b21sasafmb] comunicarselo a Infraestructura.




_**Celery**_
1. Copiar celeryd en /etc/init.d
`cp /path/to/file/celeryd /etc/init.d/celeryd`
1. Agregar permisos 755 al archivo copiado
`chmod 755 /etc/init.d/celeryd`
1. Crear un enlace simbólico de celeryd
`ln -sf /etc/init.d/celeryd /usr/bin/celeryd`
1. Copiar el archivo celeryd_config  en /etc/default/celeryd
`cp /path/to/file/celeryd_config /etc/default/celeryd`
1. Agregar permiso 644 al archivo copiado
`chmod 644 /etc/default/celeryd`
1. Crear el usuario con que se ejecutará el celery:
`useradd -M --system celery`
1. Cambiar la configuración en `/etc/default/celeryd` tomando en consideración los sigueintes valores 

>>>
**CELERYD_NODES**: Names of nodes to start, alternatively, you can specify the number of nodes to start.
  - CELERYD_NODES="worker1"
  - CELERYD_NODES="worker1 worker2 worker3"
  - CELERYD_NODES=5

**CELERY_BIN**: Absolute or relative path to the 'celery' command.
  - CELERY_BIN="/usr/local/bin/celery"

**CELERY_APP**: App instance to use (or fully qualified:)
  - CELERY_APP="controller"
  - CELERY_APP="proj.tasks:app"

**CELERYD_CHDIR**: Where to chdir at start.
  - CELERYD_CHDIR="/srv/Api-Celery/src/"

**CELERYD_OPTS**: Extra command-line arguments to the worker:
  - CELERYD_OPTS="--time-limit=300 -c 8 -c:worker2 4 -c:worker3 2 -Ofair:worker1"
  - CELERYD_OPTS="--time-limit=300 --concurrency=6 -0fair"

**CELERYD_LOG_LEVEL**: Set logging level to DEBUG
  - CELERYD_LOG_LEVEL="DEBUG"
  - CELERYD_LOG_LEVEL="INFO"

**CELERYD_LOG_FILE**: File to write log. %n will be replaced with the first part of the nodename.:
  - CELERYD_LOG_FILE="/var/log/celery/%n%I.log"
  - 
**CELERYD_PID_FILE**: Folder to write pid files. %n will be replaced with the first part of the nodename.:
  - CELERYD_PID_FILE="/var/run/celery/%n.pid"
 
**CELERYD_USER**: Workers should run as an unprivileged user. You need to create this user manually (or you can choose a user/group combination that already exists (e.g., nobody).
  - CELERYD_USER="celery"
**CELERYD_GROUP**: Workers should run as an unprivileged user. You need to create this user manually (or you can choose a user/group combination that already exists (e.g., nobody).
  - CELERYD_GROUP="celery"
**CELERY_CREATE_DIRS**: If enabled pid and log directories will be created if missing,and owned by the userid/group configured:
  - CELERY_CREATE_DIRS=1
>>>

1. Ejecutar `systemctl daemon-reload`
1. Ejecutar `systemctl enable celeryd` 

-----
-----

Ver Wiki para mayor información
