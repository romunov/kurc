from django.shortcuts import render, render_to_response
from django.template.context import RequestContext
from django.contrib import auth
from django.db.models import F
from .forms import UserAddressSettingsForm, BasicUserSettingsForm
from .models import UserAddress, Docs, Activity, Recipients
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.http import HttpResponseRedirect
from .misc_functions import get_credentials
from httplib2 import Http
from email.mime.text import MIMEText
from base64 import urlsafe_b64encode
from apiclient import discovery
from urllib.error import HTTPError


def index(request):
    context = RequestContext(request,
                             {'request': request,
                              'user': request.user})

    return render_to_response('frontend/login.html', context_instance=context)
    # return render(request, 'frontend/login.html')


def settings(request):
    # Prepare data to be filled into forms. User should always exist so no try/except call.
    prefill_user = User.objects.get(pk=request.user.id)

    # In case CustomUser table is empty, instantiate a CustomUser with request.user.id user_id.
    try:
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
        # TODO: reference na pošto se bi verjetno lahko implementiralo tako, da bi za vnešeno poštno številko iz tabele glede na id poiskal še ime pošte
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

        # if settings_form_user.is_valid() and settings_form_customuser.is_valid():
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
                   'data_user_add': prefill_customuser}
                  )


def logout(request):
    auth.logout(request)
    return render(request, 'frontend/login.html')


def login(request):
    return render(request, 'frontend/login.html')


def docs(request):
    # Initiate some objects and gather data.
    sending_error = None

    # Data of user's activity.
    u_docs = Activity.objects.filter(userid=request.user.id).order_by('-datumtime')

    # Find all documents from activity...
    u_docs_vals = u_docs.values('docid')

    # ... and exclude them from Docs
    a_docs = Docs.objects.exclude(id__in=u_docs_vals).order_by('-docname')[:10]
    # TODO: dodaj paginacijo v tabelo za Doc in Activity
    # TODO: fino bi blo met še filtriranje, po možnosti z bootstrap tabelam

    if request.method == "POST":
        # Get user address
        u_address = UserAddress.objects.get(pk=request.user.id)

        # Get clicked document name.
        clicked_doc = request.POST.get('clickedDocName', '')

        # Update Activity table, insert record of a requested document.
        my_docid = Docs.objects.get(docname=clicked_doc)
        my_userid = User.objects.get(pk=request.user.id)
        my_sentto = Recipients.objects.get(id=1)  # currently recipient hard-coded to roman.lustrik@biolitika.si

        try:
            creds = get_credentials()
            http = creds.authorize(Http())
            service = discovery.build('gmail', 'v1', http=http)

            # TODO: nadaljuj z buildanjem stringa, da pogruntaš kje crkne

            # message = MIMEText("a tole pa dela?" + clicked_doc)
            #     # my_userid.first_name + request.user.last_name +
            #                    # '\n' + u_address.street + '\n' + u_address.post_number + ' ' + u_address.post_name
            #                    # '\n\n\n'
            #                    # 'Zahtevek za pridobitev informacije javnega značaja (dokument št. ' + clicked_doc + ')'
            #                    # '\n\n\n'
            #                    # 'Spodaj podpisani želim, da mi skladno z Zakonom o dostopu do informacij javnega značaja'
            #                    # ' \n (Uradni list RS, št. 51/06 – uradno prečiščeno besedilo, 117/06 – ZDavP-2, 23/14, '
            #                    # '50/14, 19/15 – odl. US in 102/15) posredujete dokument št. ' + clicked_doc + '. Dokument'
            #                    # ' želim prejeti na zgoraj naveden elektronski naslov.'
            #                    # '\n \n ' + my_userid.first_name + my_userid.last_name
            #                    # )
            # message['to'] = my_sentto.email
            # message['from'] = request.user.email
            # message['subject'] = 'Zahtevek za pridobitev informacije javnega značaja (dokument št. ' + clicked_doc + ')'
            # raw = urlsafe_b64encode(message.as_bytes())
            # raw = raw.decode()
            # msg = {'raw': raw}
            # service.users().messages().send(userId='me', body=msg).execute()

            # Update Docs table, add count + 1.
            Docs.objects.filter(docname=clicked_doc).update(doccount=F('doccount') + 1)
            # Save change to database.
            my_act = Activity.objects.create(docid=my_docid, userid=my_userid, sentto=my_sentto,
                                             datumtime=timezone.now())
            my_act.save()

        except HTTPError as e:
            sending_error = 'Error: %s' % e
        except TypeError as te:
            sending_error = 'Error: %s' % te

    return render(request, 'frontend/dokumenti.html',
                  {'doc_list': a_docs, 'user_docs': u_docs, 'sending_error': sending_error})

    # return HttpResponseRedirect(request, 'frontend/dokumenti.html')


    # send e-mail
    # https://developers.google.com/gmail/api/guides/sending see quickstart on how to set up service

    # interact with user data
    # https://docs.djangoproject.com/en/dev/topics/auth/default/#user-objects
    # TODO: ko je uporabnik logiran, naj bo / nekaj drugega kot /login. v bistvu je lahko / -> /docs, dokumenti pa niti ne gnucam
    # TODO: kako poslat mail? dat nek formular al popup?
