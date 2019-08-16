hostvirtual-python-sdk
======================

## This repo contains two libraries for accessing the hostvirtual api
  * hostvirtual.py which is the normal python 2.7 version
  * aiohostvirtual.py which is an asyncio enabled version that uses the newer python 3.7 syntax so it is python 3.7 only


### aiohostvirtual example
    from aiohostvirtual import (
        HostVirtualException,
	    HostVirtualNodeDriver,
	    HVJobStatus
    )
 
    api_key = <your api key>
    conn = HostVirtualNodeDriver(api_key)
    pkgid = <one of your server package IDs>
    pkg_status = await conn.status(pkgid)
    servers = await conn.servers() # to get a list of all your servers
    server = await conn.server(pkgid) # to specify one server
    locations = await conn.locations() # to see a list of available locations

	# NOTE: HVJobStatus class is not fully implemented yet.

### regular hostvirtual example (mostly the same)
    from hostvirtual import (
        HostVirtualException,
	    HostVirtualNodeDriver,
    )
 
    api_key = <your api key>
    conn = HostVirtualNodeDriver(api_key)
    pkgid = <one of your server package IDs>
    pkg_status = conn.status(pkgid)
    servers = conn.servers() # to get a list of all your servers
    server = conn.server(pkgid) # to specify one server
    locations = conn.locations() # to see a list of available locations
