import requests
from requests import *

API_HOST = 'vapi.vr.org'


class HostVirtualException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        self.args = (code, message)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "<HostVirtualException in %d : %s>" % (self.code, self.message)


def connection(key):

    __key__ = key
    root_url = 'https://{}'.format(API_HOST)

    def request(url, data={}, method='GET'):
        # left size url ;-)
        if not url.startswith('/'):
            url = '/{}'.format(url)

        # build full url
        url_root = '{}{}?key={}'.format(root_url, url, __key__)

        try:
            if method == 'GET':
                url_root = "{}&{}".format(url_root, data)
                response = requests.get(url_root)
            elif method == 'POST':
                response = requests.post(url_root, json=data)
        except HTTPError:
            raise HostVirtualException(response.status_code, response.content)

        return response

    return request


class HostVirtualNodeDriver():

    name = 'HostVirtual'
    website = 'http://www.vr.org'

    def __init__(self, key):
        self.key = key
        self.connection = connection(self.key)

    def locations(self, pkg=False):
        return self.connection('/cloud/locations/')

    def os_list(self):
        return self.connection('/cloud/images/')

    def plans(self, location=False):
        params = {}
        if location:
            params = {'location': location}
        return self.connection('/cloud/sizes/', data=params)

    def buy(self, plan):
        return self.connection('/cloud/package/' + plan)

    def summary(self, mbpkgid):
        return self.connection('/cloud/serversummary/' + str(mbpkgid))

    def bandwidth_report(self, mbpkgid):
        return self.connection('/cloud/servermonthlybw/' + str(mbpkgid))

    def networkips(self, mbpkgid):
        return self.connection('/cloud/networkips/', str(mbpkgid))

    def ipv4(self, mbpkgid):
        return self.connection('/cloud/ipv4/', str(mbpkgid))

    def ipv6(self, mbpkgid):
        return self.connection('/cloud/ipv6/', str(mbpkgid))

    def packages(self):
        return self.connection('/cloud/packages')

    def package(self, mbpkgid):
        return self.connection('/cloud/package/', str(mbpkgid))

    def servers(self, mbpkgid=None):
        params = {}
        if mbpkgid:
            params['mbpkgid'] = mbpkgid
        return self.connection('/cloud/servers/', data=params)

    def build(self, dc, image, fqdn, passwd, mbpkgid):
        params = {'fqdn': fqdn, 'mbpkgid': mbpkgid,
                  'image': image, 'location': dc,
                  'password': passwd}

        return self.connection(
            '/cloud/server/build/', data=params, method='POST')

    def buy_build(self, plan, dc, image, fqdn, passwd, mbpkgid):
        params = {'fqdn': fqdn, 'mbpkgid': mbpkgid,
                  'image': image, 'location': dc,
                  'password': passwd, 'plan': plan}

        return self.connection(
            '/cloud/buy_build/', data=params, method='POST')

    def rescue(self, mbpkgid, password):
        params = {'rescue_pass': str(password)}
        return self.connection(
            '/cloud/server/start_rescue/{}'.format(mbpkgid), data=params,
            method='POST')

    def rescue_stop(self, mbpkgid):
        return self.connection(
            '/cloud/server/stop_rescue/{}'.format(mbpkgid), method='POST')

    def reboot(self, mbpkgid, force=False):
        params = {}
        if force:
            params['force'] = 1
        return self.connection(
            '/cloud/server/reboot/{}'.format(mbpkgid), data=params,
            method='POST')

    def shutdown(self, mbpkgid, force=False):
        params = {}
        if force:
            params['force'] = 1
        return self.connection(
            '/cloud/server/stop/{}'.format(mbpkgid), data=params, method='POST')

    def start(self, mbpkgid):
        return self.connection(
            '/cloud/server/start/{}'.format(mbpkgid), method='POST')

    def delete(self, mbpkgid):
        return self.connection(
            '/cloud/server/delete/{}'.format(mbpkgid), method='POST')

    def cancel(self, mbpkgid):
        return self.connection(
            '/cloud/cancel/{}'.format(mbpkgid), method='POST')

    def unlink(self, mbpkgid, force=False):
        return self.connection(
            '/cloud/unlink/{}'.format(mbpkgid), method='POST')

    # root password call is not enabled for api key use yet,
    # however you can auth with the account password to verify & submit
    # params['email']= 'abc@cde.com'
    # params['password']= 'abc!@#'

    def root_password(self, mbpkgid, passwd):
        params = {'rootpass': passwd}
        return self.connection(
            '/cloud/server/password/' + mbpkgid, data=params, method='POST')
