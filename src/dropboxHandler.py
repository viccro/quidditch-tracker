#!/usr/bin/env python3

import dropbox
import os

token = os.environ['DROPBOX_TOKEN']
dbx = dropbox.Dropbox(token)

def write(local_path, dropbox_path):
    print('Uploading %s to %s' % (local_path, dropbox_path))
    try:
        with open(local_path, "rb") as f:
#        f = open(local_path, 'rb')
#        response = dbx.files_upload(f, dropbox_path)
            response = dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode('overwrite', None), mute=True)
            print("uploaded:", response)
    except Exception as err:
        print("Failed to upload %s\n%s" % (local_path, err))

print("Finished upload.")