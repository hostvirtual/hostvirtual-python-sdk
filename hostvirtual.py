import urllib
import urllib2


class HostVirtualException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        self.args = (code, message)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "<HostVirtualException in %d : %s>" % (self.code, self.message)


API_ROOT = '/vapi'
API_HOST = 'www.vr.org'


class HostVirtualConnection():

    def __init__(self, key):
        self.key = key
        self.url = 'https://' + API_HOST + API_ROOT

    def request(self, url, data=None, method='GET'):
        opener = urllib2.build_opener(urllib2.HTTPSHandler(debuglevel=1))
        urllib2.install_opener(opener)
        url_root = self.url
        url_root += url
        if data:
            data['key'] = self.key
        else:
            data = {'key': self.key}
        params = urllib.urlencode(data)
        if method == 'GET':
            response = urllib2.urlopen(url_root + '?' + params).read()
        elif method == 'POST':
            response = urllib2.urlopen(url_root, params).read()

        print response


class HostVirtualNodeDriver():

    name = 'HostVirtual'
    website = 'http://www.vr.org'

    def __init__(self, key, mbpkgid=False):
        self.mbpkgid = mbpkgid
        self.connection = HostVirtualConnection(key)

    def locations(self, pkg=False):
        return self.connection.request('/cloud/locations/')

    def os_list(self):
        return self.connection.request('/cloud/images/')

    def plans(self, location=False):
        params = {}
        if location:
            params = {'location': location}
        return self.connection.request('/cloud/sizes/', data=params)

    def buy(self, plan):
        return self.connection.request('/cloud/package/' + plan)

    def summary(self):
        params = {'mbpkgid': self.mbpkgid}
        return self.connection.request('/cloud/serversummary/', data=params)

    def bandwidth_report(self):
        params = {'mbpkgid': self.mbpkgid}
        return self.connection.request('/cloud/servermonthlybw/', data=params)

    def networkips(self):
        params = {'mbpkgid': self.mbpkgid}
        return self.connection.request('/cloud/networkips/', data=params)

    def ipv4(self):
        params = {'mbpkgid': self.mbpkgid}
        return self.connection.request('/cloud/ipv4/', data=params)

    def ipv6(self):
        params = {'mbpkgid': self.mbpkgid}
        return self.connection.request('/cloud/ipv6/', data=params)

    def packages(self):
        return self.connection.request('/cloud/packages')

    def package(self):
        params = {'mbpkgid': self.mbpkgid}
        return self.connection.request('/cloud/package/', data=params)

    def servers(self, server_id=None):
        params = {}
        if server_id:
            params['mbpkgid'] = server_id
        return self.connection.request('/cloud/servers/', data=params)

    def build(self, dc, image, fqdn, passwd):
        params = {'fqdn': fqdn, 'mbpkgid': self.mbpkgid,
                  'image': image, 'location': dc,
                  'password': passwd}

        return self.connection.request(
            '/cloud/server/build/', data=params, method='POST')

    def buy_build(self, plan, dc, image, fqdn, passwd):
        params = {'fqdn': fqdn, 'mbpkgid': self.mbpkgid,
                  'image': image, 'location': dc,
                  'password': passwd, 'plan': plan}

        return self.connection.request(
            '/cloud/buy_build/', data=params, method='POST')

    def rescue(self, password):
        params = {'mbpkgid': self.mbpkgid, 'rescue_pass': password}
        return self.connection.request(
            '/cloud/server/start_rescue/', data=params, method='POST')

    def rescue_stop(self):
        params = {'mbpkgid': self.mbpkgid}
        return self.connection.request(
            '/cloud/server/stop_rescue/', data=params, method='POST')

    def reboot(self, force=False):
        params = {}
        if force:
            params['force'] = 1

        params['mbpkgid'] = self.mbpkgid
        return self.connection.request(
            '/cloud/server/reboot/', data=params, method='POST')

    def shutdown(self, force=False):
        params = {}
        if force:
            params['force'] = 1
        params['mbpkgid'] = self.mbpkgid
        return self.connection.request(
            '/cloud/server/stop/', data=params, method='POST')

    def start(self):
        params = {'mbpkgid': self.mbpkgid}
        return self.connection.request(
            '/cloud/server/start/', data=params, method='POST')

    def delete(self):
        params = {'mbpkgid': self.mbpkgid}
        return self.connection.request(
            '/cloud/server/delete/', data=params, method='POST')

    def cancel(self):
        params = {'mbpkgid': self.mbpkgid}
        return self.connection.request(
            '/cloud/cancel/', data=params, method='POST')

    def unlink(self, force=False):
        params = {'mbpkgid': self.mbpkgid}
        return self.connection.request(
            '/cloud/unlink/', data=params, method='POST')

    #root password call is not enabled for api key use yet,
    #however you can auth with the account password to verify & submit
    #params['email']= 'abc@cde.com'
    #params['password']= 'abc!@#'

    def root_password(self, passwd):
        params = {'mbpkgid': self.mbpkgid, 'rootpass': passwd}
        return self.connection.request(
            '/cloud/server/password/', data=params,
            method='POST')

if __name__ == '__main__':
    driver = HostVirtualNodeDriver(
        'bjSNBp9UpSSrPxA4TA2BasMCPU7qtk6pKvSeYSEBVrI7omW04YHucuDj2Vo4hhDn',
        '74549')
    driver.shutdown()
