import os


def get_temp_dir():
    tmp_dir = '/app/tmp'
    os.makedirs('/app/tmp', exist_ok=True)
    return tmp_dir