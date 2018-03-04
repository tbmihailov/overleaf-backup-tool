
import logging
import sys

def is_debug():
    """
    Checks if the project is debugged in an IDE
    :return: True if debug
    """
    gettrace = getattr(sys, 'gettrace', None)

    debug = False
    if gettrace is None:
        debug = False
    elif gettrace():
        debug = True
    else:
        debug = False

    return debug

def enable_http_client_debug():
    """
    Enable the debugging of http_client requests: logging the request info
    :return:
    """

    # https://stackoverflow.com/questions/10588644/how-can-i-see-the-entire-http-request-thats-being-sent-by-my-python-application
    # These two lines enable debugging at httplib level (requests->urllib3->http.client)
    # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # The only thing missing will be the response.body which is not logged.
    try:
        import http.client as http_client
    except ImportError:
        # Python 2
        import httplib as http_client
    http_client.HTTPConnection.debuglevel = 1

    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True