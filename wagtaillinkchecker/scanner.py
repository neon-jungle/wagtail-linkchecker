

try:
    from http import client as client
except ImportError:
    import httplib as client

import requests


def get_celery_worker_status():
    ERROR_KEY = "ERROR"
    try:
        from celery.task.control import inspect
        insp = inspect()
        d = insp.stats()
        if not d:
            d = {ERROR_KEY: 'No running Celery workers were found.'}
    except IOError as e:
        from errno import errorcode
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the RabbitMQ server is running.'
        d = {ERROR_KEY: msg}
    except ImportError as e:
        d = {ERROR_KEY: str(e)}
    return d


class Link(Exception):

    def __init__(self, url, page, status_code=None, error=None, site=None):
        self.url = url
        self.status_code = status_code
        self.error = error
        self.site = site
        self.page = page

    @property
    def message(self):
        if self.error:
            return self.error
        elif self.status_code in range(100, 300):
            message = "Success"
        elif self.status_code in range(500, 600) and self.url.startswith(self.site.root_url):
            message = str(self.status_code) + ': ' + 'Internal server error, please notify the site administrator.'
        else:
            try:
                message = str(self.status_code) + ': ' + client.responses[self.status_code] + '.'
            except KeyError:
                message = str(self.status_code) + ': ' + 'Unknown error.'
        return message

    def __str__(self):
        return self.url

    def __eq__(self, other):
        if not isinstance(other, Link):
            return NotImplemented
        return self.url == other.url

    def __hash__(self):
        return hash(self.url)


def get_url(url, page, site):
    data = {
        'url': url,
        'page': page,
        'site': site,
        'error': False,
        'invalid_schema': False
    }
    try:
        response = requests.get(url, verify=True)
        data['response'] = response
    except (requests.exceptions.InvalidSchema, requests.exceptions.MissingSchema):
        data['invalid_schema'] = True
        return data
    except requests.exceptions.ConnectionError as e:
        data['error'] = True
        data['error_message'] = 'There was an error connecting to this site.'
        return data
    except requests.exceptions.RequestException as e:
        data['error'] = True
        data['status_code'] = response.status_code
        data['error_message'] = type(e).__name__ + ': ' + str(e)
        return data

    if 'response' in locals():
        if response.status_code not in range(100, 300):
            data['error'] = True
            data['status_code'] = response.status_code
            data['error_message'] = client.responses[response.status_code]
        return data
    else:
        data['error'] = True
        data['error_message'] = 'There was an error connecting to this site.'
        return data


def clean_url(url, site):
    if url and url != '#':
        if url.startswith('/'):
            url = site.root_url + url
    else:
        return None
    return url


def broken_link_scan(site):
    from wagtaillinkchecker.models import Scan, ScanLink
    pages = site.root_page.get_descendants(inclusive=True).live().public()
    scan = Scan.objects.create(site=site)

    for page in pages:
        link = ScanLink.objects.create(url=page.full_url, page=page, scan=scan)
        link.check_link()
