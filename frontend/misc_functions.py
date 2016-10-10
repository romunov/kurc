from __future__ import print_function
import os
from django.core.exceptions import ValidationError


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
                    Želim, da mi skladno z Zakonom o dostop do informacij javnega značaja (Uradni list RS, št. 51/06 -
                    uradno prečiščeno besedilo, 117/06 – ZDavP-2, 23/14, 50/14, 19/15 – odl. US in 102/15) posredujete
                    zaključni dokument zadeve številka %s. V kolikor dokument vsebuje osebne podatke, se želim z
                    dokumentom seznaniti delno, tako, da osebne podatke odstranite oz. zatemnite skladno z Zakonom o
                    varovanju osebnih podatkov. Dokumente želim prejeti v elektronski obliki na zgoraj naveden
                    elektronski naslov. Informacijo bom uporabljal v zasebne namene.
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

Želim, da mi skladno z Zakonom o dostop do informacij javnega značaja (Uradni list RS, št. 51/06 -
uradno prečiščeno besedilo, 117/06 – ZDavP-2, 23/14, 50/14, 19/15 – odl. US in 102/15) posredujete
zaključni dokument zadeve številka %s. V kolikor dokument vsebuje osebne podatke, se želim z
dokumentom seznaniti delno, tako, da osebne podatke odstranite oz. zatemnite skladno z Zakonom o
varovanju osebnih podatkov. Dokumente želim prejeti v elektronski obliki na zgoraj naveden
elektronski naslov. Informacijo bom uporabljal v zasebne namene.


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


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Nepodprt format.')


# http://python-social-auth.readthedocs.io/en/latest/use_cases.html#multiple-scopes-per-provider
# class GmailOAuth2(GoogleOAuth2):
#     name = 'gmail'
