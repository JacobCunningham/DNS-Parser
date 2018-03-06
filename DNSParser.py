from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import subprocess
import re
import time

# I picked this website at random.
dns_html = urlopen('https://www.lifewire.com/free-and-public-dns-servers-2626062/')

dns_soup = soup(dns_html, 'html.parser')

dns_html.close()

dns_table = dns_soup.find('table')  # The data is located in a table on this website

dns_dict = {}  # Will store names ips, and latencies
servers = []  # Used for iterating over parsed html

print("Parsing...")

for item in dns_table:

    rows = item.findAll('tr')  # Extracting the rows

for row in rows:

    details = row.findAll('td')  # Three td blocks with name, primary, and secondary ip
    servers.append(details)

print("Compiling results...")

for server in servers:

    if len(server) == 3:
        dns_dict[server[0].text] = {'Latency': 0, 'Primary': server[1].text, 'Secondary': server[2].text}
    # Some of the servers do not have a secondary ip listed
    elif len(server) == 2:
        dns_dict[server[0].text] = {'Latency': 0, 'Primary': server[1].text, 'Secondary': 'Unknown'}

    else:
        pass

print("Testing connection...")

for key in dns_dict:

    start = time.time()
    subprocess.check_output("nslookup test.com " + dns_dict[key]['Primary'], shell=False, universal_newlines=False)
    end = time.time()

    dns_dict[key]['Latency'] = end-start


top5 = []

for i in range(5):
    # Sorts by minimum latency. Adds that KVP to a list of tuples
    minimum = min(dns_dict, key=lambda k: dns_dict[k]['Latency'])
    top5.append((minimum, dns_dict[minimum]['Primary'], dns_dict[minimum]['Latency']))
    del(dns_dict[minimum])

print("Top 5 DNS servers")

for name, ip, lat in top5:

    print('''
    Name: {}\n
    IP: {}\n
    Latency: {}ms\n
    '''.format(name, ip, lat*1000))

