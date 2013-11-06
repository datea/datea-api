# Installing
## Install Postgis [1](https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/postgis/)

Set POSTGIS_SQL_PATH to the directory where Postgis was installed.
```
ie. POSTGIS_SQL_PATH=`pg_config --sharedir`/contrib/postgis-2.0
```
In the case of homebrew the directory is "/usr/local/share/postgis"

```bash
createdb -E UTF8 template_postgis
createlang -d template_postgis plpgsql
psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';"
psql -d template_postgis -f $POSTGIS_SQL_PATH/postgis.sql
psql -d template_postgis -f $POSTGIS_SQL_PATH/spatial_ref_sys.sql
Enabling users to alter spatial tables.
psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"
psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"
psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
```

### Create database
```bash
createdb -T template_postgis datea
```


## Install python packages

```bash
pip install -r requirements.txt
```

## Setup the database
```bash
python manage.py syncdb --settings settings.dev
```


## Running the project

- Make sure redis is running
- `python manage.py rqworker default --settings=settings.dev`
- `python manage.py runserver_plus default --settings=settings.dev`
