# risks-api

> Risk modeling app

## Build Setup

``` bash
# Create virtualenv
# install dependencies
pip install -r requirements.txt

# serve with hot reload at localhost:8000
python manage.py migrate
python manage.py runserver

# deploy to https://0k1sug0ej1.execute-api.eu-central-1.amazonaws.com/dev (relevant permissions needed)
python manage.py migrate --settings=risks_api.settings.develop
zappa update
```

## DEV environment
API endpoints:
* schemas
  * list `/schemas/`
  * retrieve  `/schemas/<id>/`

* instances 
  * list `/instances/<schema_name_plural>/`
  * retrieve `/instances/<schema_name_plural>/<id>/`
  * create `/instances/<schema_name_plural>/`

Base url: https://0k1sug0ej1.execute-api.eu-central-1.amazonaws.com/dev/

Admin panel: https://0k1sug0ej1.execute-api.eu-central-1.amazonaws.com/dev/admin/
