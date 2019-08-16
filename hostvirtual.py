import requests
# from requests import *

API_HOSTS = {
    'v1': 'vapi.vr.org',
    'v1.1': 'oldthing.test/api/legacy',
    'v2': 'oldthing.test/api/legacy'
}


class HostVirtualException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        self.args = (code, message)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "<HostVirtualException in %d : %s>" % (self.code, self.message)


def connection(key, api_version):

    __key__ = key
    if api_version in ['v1', 'v1.1', 'v2']:
        root_url = 'http://{}'.format(API_HOSTS[api_version])
    else:
        root_url = 'http://{}'.format(API_HOSTS['v1'])

    def request(url, data=None, method=None):
        if method is None:
            method = 'GET'
        if data is None:
            data = {}
        if not url.startswith('/'):
            url = '/{}'.format(url)

        # build full url
        url_root = '{}{}?key={}'.format(root_url, url, __key__)

        try:
            if method == 'GET':
                for k, v in data.items():
                    url_root = "{}&{}={}".format(url_root, k, v)
                response = requests.get(url_root)
            elif method == 'POST':
                response = requests.post(url_root, json=data)
        except requests.HTTPError:
            raise HostVirtualException(
                response.status_code, response.content)

        return response

    return request


class HostVirtualNodeDriver():

    name = 'HostVirtual'
    website = 'http://www.vr.org'

    def __init__(self, key, api_version=None):
        if api_version is None:
            self.api_version = 'v1'
        else:
            self.api_version = api_version
        self.key = key
        self.connection = connection(self.key, api_version=api_version)

    def locations(self):
        return self.connection('/cloud/locations/')

    def os_list(self):
        return self.connection('/cloud/images/')

    def plans(self, location=False):
        if location:
            return self.connection('/cloud/sizes/' + str(location))
        else:
            return self.connection('/cloud/sizes/')

    def servers(self, mbpkgid=False):
        if mbpkgid:
            result = self.connection('/cloud/server/' + str(mbpkgid))
        else:
            result = self.connection('/cloud/servers/')
        return result

    def packages(self):
        return self.connection('/cloud/packages')

    def package(self, mbpkgid):
        return self.connection('/cloud/package/' + str(mbpkgid))

    def ipv4(self, mbpkgid):
        return self.connection('/cloud/ipv4/' + str(mbpkgid))

    def ipv6(self, mbpkgid):
        return self.connection('/cloud/ipv6/' + str(mbpkgid))

    def networkips(self, mbpkgid):
        return self.connection('/cloud/networkips/' + str(mbpkgid))

    def summary(self, mbpkgid):
        return self.connection('/cloud/serversummary/' + str(mbpkgid))

    def start(self, mbpkgid):
        return self.connection(
            '/cloud/server/start/{}'.format(mbpkgid), method='POST')

    def shutdown(self, mbpkgid, force=False):
        params = {}
        if force:
            params['force'] = 1
        return self.connection(
            '/cloud/server/shutdown/{}'.format(mbpkgid), data=params, method='POST')

    def reboot(self, mbpkgid, force=False):
        params = {}
        if force:
            params['force'] = 1
        return self.connection(
            '/cloud/server/reboot/{}'.format(mbpkgid), data=params,
            method='POST')

    def rescue(self, mbpkgid, password):
        params = {'rescue_pass': str(password)}
        return self.connection(
            '/cloud/server/start_rescue/{}'.format(mbpkgid), data=params,
            method='POST')

    def rescue_stop(self, mbpkgid):
        return self.connection(
            '/cloud/server/stop_rescue/{}'.format(mbpkgid), method='POST')

    def build(self, dc, image, fqdn, passwd, mbpkgid):
        params = {'fqdn': fqdn, 'mbpkgid': mbpkgid,
                  'image': image, 'location': dc,
                  'password': passwd}

        return self.connection(
            '/cloud/server/build/', data=params, method='POST')

    def delete(self, mbpkgid):
        return self.connection(
            '/cloud/server/delete/{}'.format(mbpkgid), method='POST')

    def unlink(self, mbpkgid, force=False):
        return self.connection(
            '/cloud/unlink/{}'.format(mbpkgid), method='POST')

    def status(self, mbpkgid):
        return self.connection('/cloud/status/{0}'.format(mbpkgid))

    # TODO

    # root password call is not enabled for api key use yet,
    # however you can auth with the account password to verify & submit
    # params['email']= 'abc@cde.com'
    # params['password']= 'abc!@#'
    def bandwidth_report(self, mbpkgid):
        return self.connection('/cloud/servermonthlybw/' + str(mbpkgid))

    def cancel(self, mbpkgid):
        return self.connection(
            '/cloud/cancel/{}'.format(mbpkgid), method='POST')

    def buy(self, plan):
        return self.connection('/cloud/buy/' + plan)

    def buy_build(self, plan, dc, image, fqdn, passwd, mbpkgid):
        params = {'fqdn': fqdn, 'mbpkgid': mbpkgid,
                  'image': image, 'location': dc,
                  'password': passwd, 'plan': plan}

        return self.connection(
            '/cloud/buy_build/', data=params, method='POST')

    def root_password(self, mbpkgid, passwd):
        params = {'rootpass': passwd}
        return self.connection(
            '/cloud/server/password/' + mbpkgid, data=params, method='POST')
