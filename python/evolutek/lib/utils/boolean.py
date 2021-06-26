from distutils.util import strtobool

def get_boolean(var):
    try:
        return strtobool(str(var))
    except Exception as e:
        return False