from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import subprocess
import re

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
    # If ping exits with a non-zero exit code check_output will throw an exception.
    # This simply means that either the server is unreachable or
    # it drops ICMP Echo requests
    try:
        # This will return the literal response from ping as byte type objects
        response = subprocess.check_output("ping -4 " + dns_dict[key]['Primary'], shell=False, universal_newlines=False).splitlines()

    except subprocess.CalledProcessError:
        # For the purposes of this script we can just set the latency
        # to a silly value for a lazy way avoid any sorting issues while ensuring
        # it will never end up in the top 5
        print('{} is unreachable or did not respond'.format(key))
        dns_dict[key]['Latency'] = 9999
        continue

    for i in response:
        #  The last line of ping begins with "Minimum" every time and ends with what we want "Average"
        if b'Minimum' in i:
            # Finds the Average latency. Converts it to string, then we get just the digits and convert to int
            avg = int(re.search(r'\d+', str(re.findall(b'Average =\s\d*', i))).group())

            dns_dict[key]['Latency'] = avg

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
    '''.format(name, ip, lat))

