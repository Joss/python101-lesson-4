import os
import urllib.request
import http.server
import logging
import time
import threading

import pushover
from dotenv import load_dotenv

# add any Ok status here, they will be ignored
IGNORED_STATUES = (200,) 
# mandatory settings in .env file
MANDATORY_ENVIRONMENTS = ["PUSHOVER_TOKEN", "PUSHOVER_KEY", "URL", "DELAY"]

LOG = logging.getLogger('root')


def prepare_logger():
    global LOG 

    log_format = "[%(asctime)s | %(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    log_filename = os.path.join(os.path.dirname(__file__), 'url_status_checker.log')
    logging.basicConfig(filename=log_filename, format=log_format)
    LOG.setLevel(logging.INFO)


def load_environment():
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    if (os.path.exists(dotenv_path)):
        load_dotenv(dotenv_path)
        for var in MANDATORY_ENVIRONMENTS:
            if var not in os.environ:
                LOG.error(".env doesn't contain required settings")
                exit(-1)
    else:
        LOG.error(".env file doesn't exist")
        exit(-1)


def check_url_status(url, delay, pushover_key, pushover_token):
    while True:
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')

        url_status = urllib.request.urlopen(request).status
        if url_status not in IGNORED_STATUES:
            msg = "[{}]: {}".format(url_status, http.server.SimpleHTTPRequestHandler.responses[url_status])
            try:
                LOG.warning("Status code is wrong: {}".format(msg))
                pushover.init("<token>")
                pushover.Client("<user-key>").send_message(msg, title="Checker: {}".format(url))
            except pushover.RequestError as e:
                LOG.error("Can't make a request to pushover: {}".format(e))
                exit(-1)
        else:
            LOG.info("Status code is Ok")
        
        time.sleep(delay)


def run_checker():
    prepare_logger()
    load_environment()

    # settings from .env file
    pushover_key = os.getenv('PUSHOVER_KEY')
    pushover_token = os.getenv('PUSHOVER_TOKEN')
    url = os.getenv('URL')
    delay = int(os.getenv('DELAY'))

    # start checking thread
    threading.Thread(target=check_url_status, args=(url, delay, pushover_key, pushover_token)).start()


if __name__ == '__main__':
    run_checker()    
