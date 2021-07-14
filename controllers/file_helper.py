from flask import session, request
from werkzeug.utils import secure_filename
from datetime import datetime
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLD = '/Users/nirup/hsi_abc/app/photos/'
UPLOAD_FOLDER = os.path.join(APP_ROOT, UPLOAD_FOLD)

def upload_file(original_fname, new_fname, user_id, category):
    f = request.files[original_fname]
    if not f:
        raise KeyError("No image with name "+original_fname)
    filename = new_fname + "_" \
        + user_id + "_" + str(int(datetime.now().timestamp()))\
            + "." + f.filename.rsplit('.', 1)[1].lower()
    if category not in ["avatar", "pick_drop", "others"]:
        raise ValueError("Unknown category")
    f.save(os.path.join(UPLOAD_FOLDER + category, secure_filename(filename)))
    return secure_filename(filename)
    