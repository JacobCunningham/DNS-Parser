from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import subprocess
import re
import time

'''
The purpose of this script was to implement an idea I had and practice with some libs I haven't used much. 

This script parses an html table on a website to retrieve common public DNS server names and ipv4 addresses
and puts the data into a dictionary with the server name being the keyIt times how long an nslookup subprocess 
takes to resolve a name for each server and saves that value in a dictionary with the corresponding server
name as the key.

I have not tested the timing overhead of running nslookup in the run() functions, so the values are entirely 
relative.
'''

# I picked this website at random.
dns_html = urlopen('https://www.lifewire.com/free-and-public-dns-servers-2626062/')

dns_soup = soup(dns_html, 'html.parser')

dns_html.close()

dns_table = dns_soup.find('table')  # The data is located in a table on this website

nsinfo = {}  # Will store names ips, and latencies
servers = []  # Used for iterating over parsed html

print("Parsing...")

for item in dns_table:

    rows = item.findAll('tr')  # Extracting the rows

for row in rows:

    details = row.findAll('td')  # Three td blocks with name, primary, and secondary ip
    servers.append(details)

for server in servers:

    if len(server) == 3:
        nsinfo[server[0].text] = {'Latency': 0, 'Primary': server[1].text, 'Secondary': server[2].text}
    # Some of the servers do not have a secondary ip listed
    elif len(server) == 2:
        nsinfo[server[0].text] = {'Latency': 0, 'Primary': server[1].text, 'Secondary': 'Unknown'}

    else:
        pass

print("Testing connection...")

for key in nsinfo:
    # runs an nslookup process to time the servers response and suppresses the processes output
    start = time.time()
    subprocess.run("nslookup test.com " + nsinfo[key]['Primary'], shell=False, stdout=subprocess.DEVNULL)
    end = time.time()

    # This will be a relative speed. I have not tested the overhead of the run() function
    nsinfo[key]['Latency'] = end - start


top5 = []

for i in range(5):
    # Sorts by minimum latency. Adds that KVP to a list of tuples
    minimum = min(nsinfo, key=lambda k: nsinfo[k]['Latency'])
    top5.append((minimum, nsinfo[minimum]['Primary'], nsinfo[minimum]['Latency']))
    del(nsinfo[minimum])

print("Top 5 DNS servers")

for name, ip, lat in top5:

    print(f'''
    Name: {name}\n
    IP: {ip}\n
    Latency: {lat*1000}ms\n
    ''')
