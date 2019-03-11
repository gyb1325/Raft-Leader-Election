from Server import *
import sys

id = int(sys.argv[1])
server = Server(id)
server.run()