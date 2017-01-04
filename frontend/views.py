from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import auth, messages
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from .forms import UserAddressSettingsForm, BasicUserSettingsForm, UploadDocFileForm
from .models import UserAddress, Docs, Activity, Recipients, UploadedDocs, UserCredentials
from django.contrib.auth.models import User
from django.utils import timezone
import httplib2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from base64 import urlsafe_b64encode
from urllib.error import HTTPError
from .misc_functions import create_html_string
from os import path
from apiclient import discovery
from oauth2client.contrib.django_orm import Storage
from kurc.top_secrets import SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
from oauth2client.contrib import xsrfutil
from mimetypes import MimeTypes
from oauth2client.client import HttpAccessTokenRefreshError
from .misc_functions import flow


@login_required
def view_file(request, doc_id):

    doc = UploadedDocs.objects.get(id=doc_id)

    if not path.isfile(doc.docfile.path):
        return render(request, 'frontend/404.html')

    with open(doc.docfile.path, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type=MimeTypes().guess_type(doc.docfile.path)[0])
        response['Content-Disposition'] = 'inline;filename=%s' % doc.docfile.name
    pdf.closed
    return response


@login_required
def upload_file(request):

    # https://amatellanes.wordpress.com/2013/11/05/dropzonejs-django-how-to-build-a-file-upload-form/
    if request.method == "POST":
        try:

            newdoc = UploadedDocs(docname=request.FILES['docfile'].name,
                                  docfile=request.FILES['docfile'],
                                  docuser=User.objects.get(pk=request.user.id),
                                  doctime=timezone.now())
            newdoc.save()

            messages.success(request, "Uspešno poslano.")
            form = UploadDocFileForm()
        except:
            messages.error(request, "Nekaj je šlo narobe pri pošiljanju dokumenta %s" % request.FILES['docfile'].name)
            form = UploadDocFileForm()

    else:
        form = UploadDocFileForm()

    all_docs = UploadedDocs.objects.all()
    num_docs = len(all_docs)

    return render(request,
                  'frontend/upload_docs.html',
                  {'all_docs': all_docs,
                   'my_form': form,
                   'num_docs': num_docs  # pass to badge for document count
                   })


def index(request):

    if request.user.is_anonymous():
        return render(request, template_name='frontend/login.html')
    else:
        if request.user.last_login is None:
            render(request, 'frontend/nastavitve.html')

        return docs(request)


def help(request):

    if request.user.is_anonymous():
        return render(request, template_name='frontend/404.html')
    else:
        return render(request, 'frontend/navodila.html')


@login_required
def settings(request):

    # Prepare data to be filled into forms. User should always exist so no try/except call.
    prefill_user = User.objects.get(pk=request.user.id)
    prefill_customuser, pfcu_created = UserAddress.objects.get_or_create(id=User(id=request.user.id))

    if request.method == "POST":
        if any([s for s in request.POST if 'remove_personal_info' in s]):
            UserAddress.objects.get(id=request.user.id).delete()

        settings_form_user = BasicUserSettingsForm(request.POST, instance=prefill_user)
        settings_form_customuser = UserAddressSettingsForm(request.POST, instance=prefill_customuser)

        if settings_form_customuser.is_valid():
            settings_form_user.save()
            settings_form_customuser.save()
            write_ok = True
        else:
            messages.error(request, "Naslov je obvezen. Prosim izpolni manjkajoča polja.")
            write_ok = False

    else:
        settings_form_user = BasicUserSettingsForm(instance=prefill_user)
        settings_form_customuser = UserAddressSettingsForm(instance=prefill_customuser)
        write_ok = None

    return render(request, 'frontend/nastavitve.html',
                  {'settings_form_user': settings_form_user,
                   'settings_form_customuser': settings_form_customuser,
                   'write_ok': write_ok,
                   'data_user_acc': prefill_user,
                   'data_user_add': prefill_customuser
                   })


def logout(request):
    auth.logout(request)
    return render(request, 'frontend/login.html')


def login(request):
    return render(request, 'frontend/login.html')


@login_required
def docs(request):

    passto = None

    # Invite first timers to add their information.
    if request.user.last_login is None:
        passto = 'First time logger.'

    # Initiate some objects and gather data.
    sending_error = None

    # Data of user's activity.
    u_docs = Activity.objects.filter(userid=request.user.id).order_by('-datumtime')

    # Find all documents from activity...
    u_docs_vals = u_docs.values('docid')

    # Extract first ten documents
    a_docs = Docs.objects.exclude(id__in=u_docs_vals).exclude(id__lte=3).order_by('?')[:10]

    if request.method == "POST":

        # Get user address
        u_address = UserAddress.objects.get(pk=request.user.id)

        if u_address.street == "" or u_address.post_number is None or u_address.post_name == "":
            messages.error(request,
                           "Naslov je obvezen. Prosim, da v Nastavitvah izpolniš manjkajoča polja in poskusiš znova.")
            return render(request, 'frontend/dokumenti.html',
                          {'doc_list': a_docs, 'user_docs': u_docs, 'sending_error': sending_error,
                           'passto': passto})

        # Get clicked document name.
        clicked_doc = request.POST.get('clickedDocName', '')

        # Update Activity table, insert record of a requested document.
        my_docid = Docs.objects.get(docname=clicked_doc)
        my_userid = User.objects.get(pk=request.user.id)

        # If everything is right, this will get only one email, because I haven't tested it it with multiple emails.
        # See admin.sending_on() how I handle this.
        my_sentto = Recipients.objects.get(active=True)

        try:
            # https://github.com/google/google-api-python-client/blob/master/samples/django_sample/plus/views.py
            storage = Storage(UserCredentials, 'id', request.user, 'credentials')
            credential = storage.get()

            if credential is None or credential.invalid is True:
                flow.params['state'] = xsrfutil.generate_token(SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                                                               request.user)
                authorize_url = flow.step1_get_authorize_url()
                messages.warning(request,
                                 "Zahtevek št. %s zahtevan vendar je prišlo do napake. Prosim ponovi." % clicked_doc)
                return HttpResponseRedirect(authorize_url)
            else:
                http = credential.authorize(httplib2.Http())

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

                try:
                    x = service.users().messages().send(userId='me', body=msg).execute()
                except HttpAccessTokenRefreshError as e:
                    messages.warning(request,
                                     "Pri pošiljanju zadeve št. %s je prišlo do napake. Prosim ponovi." % clicked_doc)

                    return render(request, 'frontend/dokumenti.html',
                                  {'doc_list': a_docs, 'user_docs': u_docs, 'sending_error': sending_error,
                                   'passto': passto})

                if x['labelIds'][0] == 'SENT':
                    # Update Docs table, add count + 1.
                    Docs.objects.filter(docname=clicked_doc).update(doccount=F('doccount') + 1)
                    # Save change to database.
                    my_act = Activity.objects.create(docid=my_docid, userid=my_userid, sentto=my_sentto,
                                                     datumtime=timezone.now())
                    my_act.save()

                    messages.success(request,
                                     "Zahteva št. %s uspešno poslan. Organ ima 30 dni časa, da odgovori." % clicked_doc)

        except HTTPError as e:
            sending_error = 'Error: %s' % e
        except TypeError as te:
            sending_error = 'Error: %s' % te

    return render(request, 'frontend/dokumenti.html',
                  {'doc_list': a_docs, 'user_docs': u_docs, 'sending_error': sending_error,
                   'passto': passto})


@login_required
def auth_return(request):
    if not xsrfutil.validate_token(SOCIAL_AUTH_GOOGLE_OAUTH2_KEY, request.GET['state'].encode('utf-8'), request.user):
        return HttpResponseBadRequest()

    credential = flow.step2_exchange(request.GET)
    storage = Storage(UserCredentials, 'id', request.user, 'credentials')
    storage.put(credential)
    return HttpResponseRedirect("/")


@login_required
def stats(request):
    if request.user.is_staff:
        sending_error = None

        req_docs = Docs.objects.filter(doccount__gt=0)
        active_docs = Activity.objects.all()
        user_upload = UploadedDocs.objects.all()

        return render(request, 'frontend/stats.html',
                      {'all_req_docs': req_docs,
                       'activity_docs': active_docs,
                       'user_upload': user_upload,
                       'sending_error': sending_error})
    else:
        return render(request, 'frontend/404.html')
