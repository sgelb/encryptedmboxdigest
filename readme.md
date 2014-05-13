### Send an encrypted email digest from a local mbox

The itch: plaintext logwatch emails from my server.
The scratch: this. And a cronjob.

#### Usage
    '''
    usage: encryptedmboxdigest.py [-h] [-k KEY] mbox email

    Send encrypted email digest from local mbox

    positional arguments:
    mbox               path to mbox
    email              email address of recipient

    optional arguments:
    -h, --help         show this help message and exit
    -k KEY, --key KEY  public key [default: use key of recipient]
    '''
