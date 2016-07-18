Ko koniraš projekt, je treba:

* izmisli si svoj SECRET_KEY (settings.py)
* kreirat bazo
* naredit superuserja
* naredit po možnosti še nesuperuserja?
* v bazo [uvozit frontend/fixtures](https://docs.djangoproject.com/en/1.8/howto/initial-data/) (`python manage.py loaddata <ime fixtureja>)
* naredi google app in v top_secrets.py dodaj vse spremenljivke, ki jih rabiš v settings.py (SECRET_KEY, SOCIAL_AUTH_GOOGLE_OAUTH2_KEY, SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET, SCOPES, CLIENT_SECRET_FILE, APPLICATION_NAME)