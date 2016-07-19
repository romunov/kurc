Before you start coding, you will have to:

* create `top_secrets.py` (or some other name, to which you link from `settings.py` and populate it with:
    * SECRET_KEY
    * SOCIAL_AUTH_GOOGLE_OAUTH2_KEY  (needed for Google login, needs [credentials from Google API](https://console.developers.google.com/apis/credentials))
    * SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET  (needed for Google login, needs [credentials from Google API](https://console.developers.google.com/apis/credentials))
    * SCOPES
    * CLIENT_SECRET_FILE
    * APPLICATION_NAME
* run migrations and link to the database
* creat superuser (`python manage.py createsuperuser`) and possibly other users for testing purposes
* import [frontend/fixtures](https://docs.djangoproject.com/en/1.8/howto/initial-data/) (`python manage.py loaddata <fixtures name>`)