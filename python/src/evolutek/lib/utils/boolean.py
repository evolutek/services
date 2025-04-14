from distutils.util import strtobool

def get_boolean(var):
    if isinstance(var, int):
        return var != 0
    try:
        s = str(var)
        return s.lower() == 'true' or bool(strtobool(s))
    except Exception as e:
        return False
