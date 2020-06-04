# Reference - https://github.com/jitendrapurbey/qr_api/blob/master/api/utils.py

import base64
import qrcode
import io
from datetime import date


# e.g. calculateAge(date(1997, 2, 3))
def calculateAge(dob):
    dob = date(dob.split("-")[0], dob.split("-")[1], dob.split("-")[2])
    today = date.today()
    try:
        birthday = dob.replace(year=today.year)

    # raised when birth date is February 29
    # and the current year is not a leap year
    except ValueError:
        birthday = dob.replace(year=today.year,
                                month=dob.month + 1, day=1)

    if birthday > today:
        return today.year - dob.year - 1
    else:
        return today.year - dob.year


def generate_qr_code(data, size=10, border=0):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=size, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image()
    return img


def generate_qr(payload):
    generated_code = generate_qr_code(data=payload, size=4, border=1)
    bio = io.BytesIO()
    img_save = generated_code.save(bio)
    png_qr = bio.getvalue()
    base64qr = base64.b64encode(png_qr)
    img_base64_data = base64qr.decode("utf-8")
    context_dict = dict()
    context_dict['file_type'] = "png"
    context_dict['image_base64'] = img_base64_data
    return context_dict
