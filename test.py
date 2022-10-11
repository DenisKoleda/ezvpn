import requests
import time
import hashlib
import json
import hmac

a = int(time.time())
print (a)
apikey = str("6fj6JAfUt3E3vbPb").encode('utf-8')

data = {
  'shop_id': 'ABAB5E3BB286834D766F03E121E4F3DB',
  'nonce': a,
  'page': 1,
}

print (data)

sign = hmac.new(apikey, str(data.encode('utf-8')), hashlib.sha256).hexdigest()

print (sign)

answer = requests.post(url='https://tegro.money/api/orders/', json = data, headers = {'Authorization': f'Bearer {sign}',})

print (answer.text)

