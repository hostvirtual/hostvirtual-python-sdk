# import requests
# from requests import *
import asyncio
import aiohttp
import json

async def get_path(url=None, data=None):
    if data is None:
        data = {}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, data=data) as resp:
            response = await resp.text()

    return response

async def post_path(url=None, data=None):
    if data is None:
        data = {}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as resp:
            response = await resp.text()

    return response

API_HOSTS = {
    'v1': 'vapi.vr.org',
    'v1.1': 'oldthing.test/api/legacy',
    'v2': 'oldthing.test/api/legacy'
}


class HostVirtualException(Exception):
    async def __init__(self, code, message):
        self.code = code
        self.message = message
        self.args = (code, message)

    async def __str__(self):
        return self.__repr__()

    async def __repr__(self):
        return "<HostVirtualException in %d : %s>" % (self.code, self.message)


class HVFromDict(object):
    """Takes any dict and creates an object out of it
    May behave weirdly if you do multiple level dicts
    So don't...
    """
    def __init__(self, kwargs):
        self.__dict__ = kwargs

    def __len__(self):
        return len(self.__dict__)


class HVJobStatus(object):
    def __init__(self, conn=None, node_id=None, job_result=None):
        if job_result is None:
            self.job_result = {}
        else:
            self.job_result = job_result
        self.conn = conn
        self.node_id = node_id
        self._job = None

    async def status(self):
        if self._job is None:
            await self.refresh()
        return int(self._job['status'])

    async def job_id(self):
        if self._job is None:
            await self.refresh()
        return int(self._job.get('id', '0'))

    async def command(self):
        if self._job is None:
            await self.refresh()
        return self._job.get('command', '')

    async def inserted(self):
        if self._job is None:
            await self.refresh()
        return self._job.get('ts_insert', '0')

    async def is_success(self):
        if self._job is None:
            await self.refresh()
        return int(await self.status()) == 5

    async def is_working(self):
        if self._job is None:
            await self.refresh()
        return int(await self.status()) <= 3

    async def is_failure(self):
        if self._job is None:
            await self.refresh()
        return int(await self.status()) == 6

    async def _get_job_status(self):
        params = {'mbpkgid': self.node_id,
                  'job_id': self.job_result['id']}
        result = await self.conn.connection(
            '/cloud/serverjob',
            data=params)
        return json.loads(result) # json.loads(result)

    async def refresh(self):
        self._job = await self._get_job_status()
        return self


# This is a closure that returns the request method below pre-configured
def connection(key, api_version):

    __key__ = key
    if api_version in ['v1', 'v1.1', 'v2']:
        root_url = 'http://{}'.format(API_HOSTS[api_version])
    else:
        root_url = 'http://{}'.format(API_HOSTS['v1'])

    async def request(url, data=None, method=None):
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
                response = await get_path(url_root)
            elif method == 'POST':
                response = post_path(url_root, data=data)
        except aiohttp.ClientError:
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
        self.connection = connection(
            self.key,
            api_version=api_version)

    async def locations(self):
        return await self.connection('/cloud/locations/')

    async def os_list(self):
        return await self.connection('/cloud/images/')

    async def plans(self, location=False):
        if location:
            return await self.connection('/cloud/sizes/' + str(location))
        else:
            return await self.connection('/cloud/sizes/')

    async def servers(self, mbpkgid=False):
        if mbpkgid:
            result = self.connection('/cloud/server/' + str(mbpkgid))
        else:
            result = self.connection('/cloud/servers/')
        return result

    async def packages(self):
        return await self.connection('/cloud/packages')

    async def package(self, mbpkgid):
        return await self.connection('/cloud/package/' + str(mbpkgid))

    async def ipv4(self, mbpkgid):
        return await self.connection('/cloud/ipv4/' + str(mbpkgid))

    async def ipv6(self, mbpkgid):
        return await self.connection('/cloud/ipv6/' + str(mbpkgid))

    async def networkips(self, mbpkgid):
        return await self.connection('/cloud/networkips/' + str(mbpkgid))

    async def summary(self, mbpkgid):
        return await self.connection('/cloud/serversummary/' + str(mbpkgid))

    async def start(self, mbpkgid):
        return await self.connection(
            '/cloud/server/start/{}'.format(mbpkgid), method='POST')

    async def shutdown(self, mbpkgid, force=False):
        params = {}
        if force:
            params['force'] = 1
        return await self.connection(
            '/cloud/server/shutdown/{}'.format(mbpkgid), data=params, method='POST')

    async def reboot(self, mbpkgid, force=False):
        params = {}
        if force:
            params['force'] = 1
        return await self.connection(
            '/cloud/server/reboot/{}'.format(mbpkgid), data=params,
            method='POST')

    async def rescue(self, mbpkgid, password):
        params = {'rescue_pass': str(password)}
        return await self.connection(
            '/cloud/server/start_rescue/{}'.format(mbpkgid), data=params,
            method='POST')

    async def rescue_stop(self, mbpkgid):
        return await self.connection(
            '/cloud/server/stop_rescue/{}'.format(mbpkgid), method='POST')

    async def build(self, dc, image, fqdn, passwd, mbpkgid):
        params = {'fqdn': fqdn, 'mbpkgid': mbpkgid,
                  'image': image, 'location': dc,
                  'password': passwd}

        return await self.connection(
            '/cloud/server/build/', data=params, method='POST')

    async def delete(self, mbpkgid):
        return await self.connection(
            '/cloud/server/delete/{}'.format(mbpkgid), method='POST')

    async def unlink(self, mbpkgid, force=False):
        return await self.connection(
            '/cloud/unlink/{}'.format(mbpkgid), method='POST')

    async def status(self, mbpkgid):
        return await self.connection('/cloud/status/{0}'.format(mbpkgid))

    # TODO

    # root password call is not enabled for api key use yet,
    # however you can auth with the account password to verify & submit
    # params['email']= 'abc@cde.com'
    # params['password']= 'abc!@#'
    async def bandwidth_report(self, mbpkgid):
        return await self.connection('/cloud/servermonthlybw/' + str(mbpkgid))

    async def cancel(self, mbpkgid):
        return await self.connection(
            '/cloud/cancel/{}'.format(mbpkgid), method='POST')

    async def buy(self, plan):
        return await self.connection('/cloud/buy/' + plan)

    async def buy_build(self, plan, dc, image, fqdn, passwd, mbpkgid):
        params = {'fqdn': fqdn, 'mbpkgid': mbpkgid,
                  'image': image, 'location': dc,
                  'password': passwd, 'plan': plan}

        return await self.connection(
            '/cloud/buy_build/', data=params, method='POST')

    async def root_password(self, mbpkgid, passwd):
        params = {'rootpass': passwd}
        return await self.connection(
            '/cloud/server/password/' + mbpkgid, data=params, method='POST')

