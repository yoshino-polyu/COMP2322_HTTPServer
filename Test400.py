import http.client
import pprint

con = http.client.HTTPConnection("localhost", 8000)

he = {"Connection" : "keep-alive"}
con.request("POST", "/", headers=he)
resp = con.getresponse() # response
print("Status: {} and reason: {}".format(resp.status, resp.reason))
headers = resp.getheaders()
pp = pprint.PrettyPrinter(indent=4)
pp.pprint("Headers: {}".format(headers))
print("the body of response:\n", resp.read().decode())
con.close()