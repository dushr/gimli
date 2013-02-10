import redis
import json

SETTINGS_KEY = 'settings:v1'

ALL_SERVERS_KEY = '%(name)s:all_servers'

VERSION_SERVERS_KEY = '%(name)s:v%(version)d:currently_active'

r = redis.Redis(port=6710, db=3)

def get_all_cloud_types():

    all_servers = json.loads(r.get(SETTINGS_KEY))
    production_servers = all_servers['production_version'] 
    most_recent = all_servers['most_recent_version']


    clouds = []

    for name, production_version in production_servers.iteritems():
        most_recent_version = most_recent.get(name)
        cloud = CloudType(name, production=production_version, most_recent=most_recent_version)
        clouds.append(cloud)

    return clouds
        
    

class CloudType(object):

    def __init__(self, name, version=None, production=None, most_recent=None):
        self.name = name
        self.production = production
        self.most_recent = most_recent

    def _get_servers(self, key):
        response = r.sort(key, get='*')
        server_qs = []

        for server in response:
            server_qs.append(type('Server', (object,), json.loads(server)))

        return server_qs

    def get_all_servers(self):
        key = ALL_SERVERS_KEY % {'name': self.name}

        return self._get_servers(key)

    def get_versioned_servers(self, version):
        key = VERSION_SERVERS_KEY % {'name': self.name, 'version': version}
        return self._get_servers(key)

    def get_production_servers(self):
        return self.get_versioned_servers(self.production)

    def get_most_recent_servers(self):
        return self.get_versioned_servers(self.most_recent)

    def __unicode__(self):
        return self.name

if __name__ == '__main__':
    print 'hello'
