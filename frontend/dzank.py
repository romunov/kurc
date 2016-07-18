from frontend.models import Activity, User, Docs, Recipients
from django.db.models import F


# add 1 to doccount of document '0-1/2007/11'
Docs.objects.filter(docname='0-1/2007/11').update(doccount=F('doccount') + 1)

# reset all doccounts
Docs.objects.all().update(doccount=0)

# reset activity for a user
Activity.objects.filter(userid=2).delete()
