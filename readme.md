### Send an encrypted email digest from a local mbox

The itch: plaintext emails (e.g. from logwatch) from my server.
The scratch: this. And a cronjob.

#### Usage

    usage: encryptedmboxdigest.py [-h] [-g GPGHOME] [-k KEY] mbox email

    Send encrypted email digest from local mbox

    positional arguments:
    mbox                  path to mbox
    email                 email address of recipient

    optional arguments:
    -h, --help            show this help message and exit
    -g GPGHOME, --gpghome GPGHOME
                          path to gpg home directory [default: ~/.gnupg]
    -k KEY, --key KEY     public key id [default: use key of recipient]
