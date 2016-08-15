from django.shortcuts import render
from django.template.context import RequestContext
from django.contrib import auth, messages
from django.db.models import F
from .forms import UserAddressSettingsForm, BasicUserSettingsForm
from .models import UserAddress, Docs, Activity, Recipients
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from .misc_functions import get_credentials
from httplib2 import Http
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from base64 import urlsafe_b64encode
from apiclient import discovery
from urllib.error import HTTPError
from .misc_functions import create_html_string


def index(request):
    context = RequestContext(request,
                             {'request': request,
                              'user': request.user})

    if request.user.is_anonymous():
        return render(request, 'frontend/login.html', context_instance=context)
    else:
        if request.user.last_login is None:
            render(request, 'frontend/nastavitve.html')

        sending_error = None
        u_docs = Activity.objects.filter(userid=request.user.id).order_by('-datumtime')
        u_docs_vals = u_docs.values('docid')
        a_docs = Docs.objects.exclude(id__in=u_docs_vals).order_by('-docname')[:10]
        return render(request, 'frontend/dokumenti.html',
                      {'doc_list': a_docs, 'user_docs': u_docs, 'sending_error': sending_error})
        # return render(request, 'frontend/login.html')


def welcome(request):
    return render(request, 'frontend/login.html')


def settings(request):

    if request.user.is_anonymous():
        return render(request, 'frontend/404.html')

    # Prepare data to be filled into forms. User should always exist so no try/except call.
    prefill_user = User.objects.get(pk=request.user.id)

    # In case CustomUser table is empty, instantiate a CustomUser with request.user.id user_id.
    try:
        if 'remove_personal_info' in request.POST:
            UserAddress.objects.get(id=request.user.id).delete()
        prefill_customuser = UserAddress.objects.get(pk=request.user.id)
    except ObjectDoesNotExist:
        prefill_customuser = UserAddress(id=User(id=request.user.id))

    if request.method == "GET":
        # If CustomUser table is empty, fields will appear empty. If prefill_customuser is successful
        # at retrieving data, I expect this to be populated by values from the database.
        settings_form_user = BasicUserSettingsForm(initial={'first_name': prefill_user.first_name,
                                                            'last_name': prefill_user.last_name,
                                                            'email': prefill_user.email},
                                                   instance=prefill_user)

        settings_form_customuser = UserAddressSettingsForm(initial={'street': prefill_customuser.street,
                                                                    'post_name': prefill_customuser.post_name,
                                                                    'post_number': prefill_customuser.post_number},
                                                           instance=prefill_customuser)
        write_ok = None

    if request.method == "POST":

        settings_form_user = BasicUserSettingsForm(request.POST, instance=prefill_user)
        try:
            settings_form_customuser = UserAddressSettingsForm(request.POST, instance=prefill_customuser)
        except ObjectDoesNotExist:
            settings_form_customuser = UserAddressSettingsForm(request.POST)

        if settings_form_customuser.is_valid():
            settings_form_user.save()
            settings_form_customuser.save()
            write_ok = True

        else:
            settings_form_user = BasicUserSettingsForm(request.POST)
            settings_form_customuser = UserAddressSettingsForm(request.POST)
            write_ok = False

    return render(request, 'frontend/nastavitve.html',
                  {'settings_form_user': settings_form_user,
                   'settings_form_customuser': settings_form_customuser,
                   'write_ok': write_ok,
                   'data_user_acc': prefill_user,
                   'data_user_add': prefill_customuser,
                   'passto': 3,
                   'mypost': request.POST.get('remove_personal_info')}
                  )


def logout(request):
    auth.logout(request)
    return render(request, 'frontend/login.html')


def login(request):
    return render(request, 'frontend/login.html')


def docs(request):

    passto = None

    # send away non-registered users
    if request.user.is_anonymous():
        return render(request, 'frontend/404.html')

    # Invite first timers to add their information.
    if request.user.last_login is None:
        passto = 'First time logger.'

    try:
        sadd = UserAddress.objects.get(pk=request.user.id)
    except UserAddress.DoesNotExist as de:
        passto = 'No address (error %s).' % de

    # Initiate some objects and gather data.
    sending_error = None

    # Data of user's activity.
    u_docs = Activity.objects.filter(userid=request.user.id).order_by('-datumtime')

    # Find all documents from activity...
    u_docs_vals = u_docs.values('docid')

    # ... and exclude them from Docs
    a_docs = Docs.objects.exclude(id__in=u_docs_vals).filter(doccount__lt=3)[1:100]

    if request.method == "POST":
        # Get user address
        u_address = UserAddress.objects.get(pk=request.user.id)

        # Get clicked document name.
        clicked_doc = request.POST.get('clickedDocName', '')

        # Update Activity table, insert record of a requested document.
        my_docid = Docs.objects.get(docname=clicked_doc)
        my_userid = User.objects.get(pk=request.user.id)
        my_sentto = Recipients.objects.get(id=1)

        try:
            creds = get_credentials()
            http = creds.authorize(Http())
            service = discovery.build('gmail', 'v1', http=http)

            # Create message container - the correct MIME type is multipart/alternative.
            # https://docs.python.org/2.7/library/email-examples.html?highlight=mimemultipart
            msg = MIMEMultipart()
            msg['Subject'] = "Zahteva za dostop do informacije javnega značaja št. %s" % clicked_doc
            msg['From'] = '%s %s <%s>' % (my_userid.first_name, my_userid.last_name, request.user.email)
            msg['To'] = my_sentto.email

            html = create_html_string(first_name=my_userid.first_name, last_name=my_userid.last_name,
                                      street=u_address.street, post_number=u_address.post_number,
                                      post_name=u_address.post_name, email=my_userid.email, doc_name=clicked_doc,
                                      output="html")
            text = create_html_string(first_name=my_userid.first_name, last_name=my_userid.last_name,
                                      street=u_address.street, post_number=u_address.post_number,
                                      post_name=u_address.post_name, email=my_userid.email, doc_name=clicked_doc,
                                      output="text")

            part1 = MIMEText(text, 'plain')
            part1.add_header('Content-Disposition', 'attachment', filename="zahteva_ijz_%s.txt" % clicked_doc)
            part2 = MIMEText(html, 'html')

            # Attach parts into message container.
            # According to RFC 2046, the last part of a multipart message, in this case
            # the HTML message, is best and preferred. But HTML is prettier and 2016, FFS.
            msg.attach(part2)
            msg.attach(part1)

            raw = urlsafe_b64encode(msg.as_bytes())
            raw = raw.decode()
            msg = {'raw': raw}

            service.users().messages().send(userId='me', body=msg).execute()

            # Update Docs table, add count + 1.
            Docs.objects.filter(docname=clicked_doc).update(doccount=F('doccount') + 1)
            # Save change to database.
            my_act = Activity.objects.create(docid=my_docid, userid=my_userid, sentto=my_sentto,
                                             datumtime=timezone.now())
            my_act.save()

            messages.success(request,
                             "Zahtevek št. %s uspešno poslan. Organ ima 30 dni časa, da odgovori." % clicked_doc)

        except HTTPError as e:
            sending_error = 'Error: %s' % e
        except TypeError as te:
            sending_error = 'Error: %s' % te

    return render(request, 'frontend/dokumenti.html',
                  {'doc_list': a_docs, 'user_docs': u_docs, 'sending_error': sending_error,
                   'passto': passto})


def stats(request):
    if request.user.is_staff:
        sending_error = None

        req_docs = Docs.objects.filter(doccount__gt=0)
        active_docs = Activity.objects.all()

        return render(request, 'frontend/stats.html',
                      {'all_req_docs': req_docs,
                       'activity_docs': active_docs,
                       'sending_error': sending_error})
    else:
        return render(request, 'frontend/404.html')
