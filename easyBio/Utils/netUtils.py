import time
import requests


def defineSession():
    """
    This function defines and returns a new `requests.Session` object.

    Returns:
    A new `requests.Session` object.
    """
    session = requests.Session()
    session.trust_env = False
    return session


def requestGet(url, Headers={}, time_out=20, maxtimes=20, proxies=""):
    """
    This function sends an HTTP GET request to the specified URL and returns the response object.
    It has the option to set request headers, timeout, maximum number of retries, and proxies.
    If the request fails, it will retry up to a maximum number of times before giving up.
    
    Arguments:
    url -- The URL to which the GET request will be sent.
    Headers -- A dictionary of request headers (optional).
    time_out -- The timeout for the request in seconds (default 20 seconds).
    maxtimes -- The maximum number of times the request will be retried if it fails (default 20 times).
    proxies -- A dictionary of proxy servers to be used for the request (optional).
    
    Returns:
    The response object.
    """
    session = defineSession()
    keep = True
    count = 0

    while keep and count < maxtimes:
        try:
            try:
                res = requests.get(url=url, headers=Headers,
                                   timeout=time_out, proxies=proxies)
            except Exception as e:
                res = session.get(url=url, headers=Headers,
                                  timeout=time_out, proxies=proxies)
            keep = False
            print("\033[1;32mResponse time:   " + str(res.elapsed) + "\033[0m")
            return res
        except Exception as e:
            print(e)
            time.sleep(3)
            # Increments the "count" variable to track the number of retries
            count = count + 1
            print('\033[33mRetry ' + str(count) + '\033[0m')

    if keep == True:
        print("\033[31mTimeout!\033[0m")
        n += 1
        return ""

    print("success!" if res.status_code == 200 else "failed!")
