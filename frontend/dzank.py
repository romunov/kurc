from frontend.models import Activity, User, Docs, Recipients
from django.db.models import F
from email.parser import Parser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from base64 import urlsafe_b64encode
from .misc_functions import create_html_string
from frontend.models import UserAddress

x = UserAddress.objects.filter(id=1)
UserAddress.objects.filter(id=1).delete()

# add 1 to doccount of document '0-1/2007/11'
Docs.objects.filter(docname='0-1/2007/11').update(doccount=F('doccount') + 1)

# reset all doccounts
Docs.objects.all().update(doccount=0)

# reset activity for a user
Activity.objects.filter(userid=2).delete()

clicked_doc = '123/23'
msg = MIMEMultipart()
msg['Subject'] = "Zahteva za dostop do informacije javnega značaja št. %s" % clicked_doc
msg['From'] = 'romunov@gmail.com'
msg['To'] = 'roman.lustrik@biolitika.si'

# https://docs.djangoproject.com/en/dev/topics/auth/default/#user-objects

x = create_html_string(first_name="Roman", last_name="Luštrik", doc_name="123/45", post_name="Šntvd",
                       post_number="1234", street="Podgorska 30", output="html")
