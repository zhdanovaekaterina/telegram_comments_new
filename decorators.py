import time as t

from requests import exceptions as e


def connectionerror(foo):
    def proceed_errors():
        while True:
            try:
                foo()
            except e.ConnectionError:
                print('requests.exceptions.ConnectionError raised, bot will be restarted in 10 s.')
                t.sleep(10)
                continue
            except ConnectionResetError:
                print('ConnectionResetError raised, bot will be restarted in 10 s.')
                t.sleep(10)
                continue
    return proceed_errors
