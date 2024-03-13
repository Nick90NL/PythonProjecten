# Import
from python_aternos import Client
import requests

# Create object
atclient = Client()

# Log in
# with username and password
atclient.login("Nick90NL", "Bontekoe.90")
# ----OR----
# with username and MD5 hashed password
#atclient.login_hashed('Nick90NL', 'cc03e747a6afbbcbf8be7668acfebee5')
# ----OR----
# with session cookie
#atclient.login_with_session('ATERNOS_SESSION cookie value')

# Get AternosAccount object
aternos = atclient.account

# Get servers list
servs = aternos.list_servers()

# Get the first server
myserv = servs[0]

print(myserv)

# Start
#myserv.start()
# Stop
#myserv.stop()

# You can also find server by IP
testserv = None
for serv in servs:
    if serv.address == 'Nickpaper.aternos.me':
        testserv = serv

if testserv is not None:
    # Prints the server software and its version
    # (for example, "Vanilla 1.12.2")
    print(testserv.software, testserv.version)
    # Starts server
    testserv.start()
