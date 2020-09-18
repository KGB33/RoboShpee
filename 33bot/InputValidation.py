# int i > 0
def verify_int_g_zero(i):
    if isinstance(i, int):
        if i > 0:
            return True
    return False
