#!/usr/bin/env python3

# Copyright © 2014 sgelb
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.

import argparse
import email
import gnupg
import mailbox
import os
import re
import smtplib
import sys
import time
from email.mime.text import MIMEText
from string import Template

# TODO: use real digest format
# http://code.activestate.com/recipes/52243-sending-multipart-mime-email-with-smtplib-and-mime/


def getBodyFromMail(msg):
    body = None
    # Walk through the parts of the email to find the text body.
    if msg.is_multipart():
        for part in msg.walk():

            # If part is multipart, walk through the subparts.
            if part.is_multipart():
                for subpart in part.walk():
                    if subpart.get_content_type() == 'text/plain':
                        # Get the subpart payload (i.e the message body)
                        body = subpart.get_payload(decode=True)

            # Part isn't multipart so get the email body
            elif part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True)

    # If this isn't a multi-part message, get the payload/message body
    elif msg.get_content_type() == 'text/plain':
        body = msg.get_payload(decode=True)

    return body


def getKeyId(gpg, key):
    for item in gpg.list_keys():
        if (
            re.search(re.escape(key), ' '.join(item['uids']), re.IGNORECASE) or
            re.search(re.escape(key), item['keyid'], re.IGNORECASE)
        ):
            return item['keyid']


def extractMailsFromMbox(mboxfile):
    mails = []
    mbox = mailbox.mbox(mboxfile)
    if len(mbox):
        for msg in mbox:
            mail = {}
            mail['sender'] = email.utils.parseaddr(msg['from'])[1]
            mail['subject'] = msg['subject']
            mail['date'] = time.strftime(
                '%m/%d, %H:%M', email.utils.parsedate(msg['date']))
            mail['body'] = getBodyFromMail(msg).decode('utf-8')
            mails.append(mail)
    return mails


def createDigestMail(mails):
    mailtpl = Template('$date $sender\n$subject\n\n$body\n$divider')
    digestMail = ''
    for msg in mails:
        d = {'date': msg['date'], 'sender': msg['sender'],
             'subject': msg['subject'], 'body': msg['body'],
             'divider': '-'*50+'\n'}
        digestMail += mailtpl.safe_substitute(d)

    return digestMail


def encryptDigestMail(digestMail, gpg, keyId):
    return str(gpg.encrypt(digestMail, keyId))


def sendDigest(header, encryptedDigest):
    msg = MIMEText(encryptedDigest)
    msg['Subject'] = header['Subject']
    msg['From'] = header['From']
    msg['To'] = header['To']

    try:
        s = smtplib.SMTP('localhost')
        s.sendmail(header['From'], [header['To']], msg.as_string())
        s.quit
        return True
    except smtplib.SMTPServerDisconnected:
        return False


def run(mbox, recipient, gpg, keyId):

    mails = extractMailsFromMbox(mbox)
    if not mails:
        print("No mails.")
    else:
        header = {'From': mails[0]['sender'],
                  'Subject': 'email digest',
                  'To': recipient}
        digestMail = createDigestMail(mails)
        encryptedDigest = encryptDigestMail(digestMail, gpg, keyId)
        if sendDigest(header, encryptedDigest):
            os.remove(mbox)
        else:
            print("Error: could not send email")
            sys.exit(5)


if __name__ == '__main__':
    p = argparse.ArgumentParser(
        description='Send encrypted email digest from local mbox')
    p.add_argument('mbox', help='path to mbox')
    p.add_argument('email', help='email address of recipient')
    p.add_argument('-g', '--gpghome',
                   help='path to gpg home directory [default: ~/.gnupg]')
    p.add_argument('-k', '--key',
                   help='public key id [default: use key of recipient]')

    args = vars(p.parse_args())

    if not os.path.isfile(args['mbox']):
        print("Error: " + args['mbox'] + " does not exist or is not a file")
        sys.exit(1)
    if not re.match(r"[^@]+@[^@]+\.[^@]+", args['email'], re.IGNORECASE):
        print("Error: " + args['email'] + " is not a valid email address")
        sys.exit(2)
    if args['gpghome']:
        gpghome = args['gpghome']
    else:
        gpghome = os.path.join(os.getenv('HOME'), '.gnupg')
    if not os.path.isdir(gpghome):
        print("Error: " + gpghome + " does not exist")
        sys.exit(3)

    gpg = gnupg.GPG(gnupghome=gpghome)
    gpg.encoding = 'utf-8'

    key = args['key'] if args['key'] else args['email']
    keyId = getKeyId(gpg, key)
    if not keyId:
        print("Error: couldn\'t find public key for " + key)
        sys.exit(4)

    run(args['mbox'], args['email'], gpg, keyId)
    sys.exit(0)

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
