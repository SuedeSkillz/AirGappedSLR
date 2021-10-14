# function to test if an IP address is valid
def validIPAddress(IP):
# test each octets value
  def isIPv4(s):
     try: return str(int(s)) == s and 0 <= int(s) <= 255
     except: return False
# test each hectets value
  def isIPv6(s):
     if len(s) > 4:
        return False
     try : return int(s, 16) >= 0 and s[0] != '-'
     except:
        return False
# determine if the ip address is v4 or v6 and then validate it
  if IP.count(".") == 3 and all(isIPv4(i) for i in IP.split(".")):
     return True
  if IP.count(":") == 7 and all(isIPv6(i) for i in IP.split(":")):
     return True
  return False