import http.client
import pprint

con = http.client.HTTPConnection("localhost", 8000)

# index.html
he = {"Connection" : "keep-alive"}
con.request("HEAD", "/", headers=he)
resp = con.getresponse() # response
print("Status: {} and reason: {}".format(resp.status, resp.reason))
headers = resp.getheaders()
pp = pprint.PrettyPrinter(indent=4)
pp.pprint("Headers: {}".format(headers))
print("the body of response:\n", resp.read().decode())

# ai.png
he = {"Connection" : "keep-alive"}
con.request("HEAD", "/ai.png", headers=he)
resp = con.getresponse() # response
print("Status: {} and reason: {}".format(resp.status, resp.reason))
headers = resp.getheaders()
pp = pprint.PrettyPrinter(indent=4)
pp.pprint("Headers: {}".format(headers))
print("the body of response:\n", resp.read().decode())

# # computer_n.jpg
he = {"Connection" : "keep-alive"}
con.request("HEAD", "/computer_n.jpg", headers=he)
resp = con.getresponse() # response
print("Status: {} and reason: {}".format(resp.status, resp.reason))
headers = resp.getheaders()
pp = pprint.PrettyPrinter(indent=4)
pp.pprint("Headers: {}".format(headers))
print("the body of response:\n", resp.read().decode())

# # helloworld.html
he = {"Connection" : "keep-alive"}
con.request("HEAD", "/helloworld.html", headers=he)
resp = con.getresponse() # response
print("Status: {} and reason: {}".format(resp.status, resp.reason))
headers = resp.getheaders()
pp = pprint.PrettyPrinter(indent=4)
pp.pprint("Headers: {}".format(headers))
print("the body of response:\n", resp.read().decode())

# # hello.html -> 404 File Not Found
he = {"Connection" : "keep-alive"}
con.request("HEAD", "/hello.html", headers=he)
resp = con.getresponse() # response
print("Status: {} and reason: {}".format(resp.status, resp.reason))
headers = resp.getheaders()
pp = pprint.PrettyPrinter(indent=4)
pp.pprint("Headers: {}".format(headers))
print("the body of response:\n", resp.read().decode())

