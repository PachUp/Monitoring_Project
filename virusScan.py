import requests
import pyclamd
pyclamd.init_unix_socket('/tmp/clamd.socket')
print(cd.ping()) 