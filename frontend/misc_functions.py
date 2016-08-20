from __future__ import print_function
import os
import oauth2client
from oauth2client import client
from oauth2client import tools
from kurc.settings import CLIENT_SECRET_FILE, SCOPES, APPLICATION_NAME
from django.core.exceptions import ValidationError
from django.db.models import FileField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
# https://developers.google.com/gmail/api/guides/sending
def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-kurc-authentication.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run(flow, store)
    return credentials


def create_html_string(first_name, last_name, street, post_number, post_name, email, doc_name, output):
    """
    Given data, produce a html string which can be passed to MIMEMultiPart or MIMEType
    """

    html = """
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">

    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title>Zahteva za dostop do informacije javnega značaja</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    </head>

    <body style="margin: 0; padding: 0;">

        <table align="left" border="0" cellpadding="0" cellspacing="0" width="600" style="border-collapse: collapse; font-family: sans-serif; font-size: 11pt;">
            <tr>
                <td align="left" style="padding: 20px 5px 10px 5px;">
                    %s %s
                    <br> %s
                    <br> %s %s
                    <br> %s
                </td>
            </tr>
            <tr>
                <td align="left" style="padding: 20px 5px 10px 5px;">
                    Ministrstvo za notranje zadeve
                    <br> Inšpektorat RS za notranje zadeve
                    <br> Štefanova 11
                    <br> 1000 Ljubljana
                    <br> mnz@gov.si
                </td>
            </tr>
            <tr>
                <td align="left" style="padding: 10px 5px 10px 5px;">
                    <strong>ZADEVA: Zahteva za dostop do informacije javnega značaja, zadeve št. %s</strong>
                </td>
            </tr>
            <tr>
                <td align="left" style="padding: 10px 5px 10px 5px;">
                    Želim, da mi skladno z Zakono o dostop do informacij javnega značaja (Uradni list RS, št. 51/06 -
                    uradno prečiščeno besedilo, 117/06 – ZDavP-2, 23/14, 50/14, 19/15 – odl. US in 102/15) posredujete
                    zaključni dokument zadeve številka %s. V kolikor dokument vsebuje osebne podatke, se želim z
                    dokumentom seznaniti delno, tako, da osebne podatke odstranite oz. zatemnite skladno z Zakonom o
                    varovanju osebnih podatkov. Dokumente želim prejeti v elektronski obliki na zgoraj naveden
                    elektronski naslov.
                </td>
            </tr>
            <tr>
                <td align="left" style="padding: 20px 5px 10px 5px;">
                    %s %s
                </td>
            </tr>
        </table>
    </body>

    </html>
                """ % (first_name, last_name, street, post_number, post_name, email,
                       doc_name, doc_name, first_name, last_name)

    text = """%s %s
%s
%s %s
%s

Inšpektorat RS za notranje zadeve
Ministrstvo za notranje zadeve
Štefanova ulica 2
1501 Ljubljana
mnz@gov.si

ZADEVA: Zahteva za dostop do informacije javnega značaja, zadeve št. %s

Želim, da mi skladno z Zakono o dostop do informacij javnega značaja (Uradni list RS, št. 51/06 -
uradno prečiščeno besedilo, 117/06 – ZDavP-2, 23/14, 50/14, 19/15 – odl. US in 102/15) posredujete
zaključni dokument zadeve številka %s. V kolikor dokument vsebuje osebne podatke, se želim z
dokumentom seznaniti delno, tako, da osebne podatke odstranite oz. zatemnite skladno z Zakonom o
varovanju osebnih podatkov. Dokumente želim prejeti v elektronski obliki na zgoraj naveden
elektronski naslov.


%s %s
            """ % (first_name, last_name, street, post_number, post_name, email,
                   doc_name, doc_name, first_name, last_name)

    if output == "text":
        return text
    if output == "html":
        return html


def validate_file_extension(value):
    """
    Accept only certain file extensions. From http://stackoverflow.com/a/8826854/322912
    """
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
    if ext not in valid_extensions:
        raise ValidationError(u'File not supported!')


class ContentTypeRestrictedFileField(FileField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types.
        Example: ['application/pdf', 'image/jpeg']
        * max_upload_size - a number indicating the maximum file
        size allowed for upload.
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 5242880
            100MB 104857600
            250MB - 214958080
            500MB - 429916160
    """

    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types")
        self.max_upload_size = kwargs.pop("max_upload_size")

        super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)
        file = data.file
        try:
            content_type = file.content_type
            if content_type in self.content_types:
                if file._size >= self.max_upload_size:
                    raise forms.ValidationError(_('Please keep filesize under'
                                                  '%s. Current filesize %s')
                                                % (filesizeformat(self.max_upload_size), filesizeformat(file._size)))
            else:
                raise forms.ValidationError(_('Filetype not supported.'))
        except AttributeError:
            pass

        return data
