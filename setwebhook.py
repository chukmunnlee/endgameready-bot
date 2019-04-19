import sys, os, time
import hashlib, requests

from pprint import pprint

KEYS = [ 'APP_PORT', 'MARVEL_PUBLIC', 'MARVEL_PRIVATE', 'TELEGRAM_TOKEN' ]

params = { 'APP_PORT': '3000' }

for _, v in enumerate(KEYS):
   if v in os.environ:
      params[v] = os.environ[v]


def mkRequest(token):
   return lambda res: "https://api.telegram.org/bot%s/%s" %(token, res)

bot = mkRequest(params['TELEGRAM_TOKEN'])

print(bot('getme'))

r = requests.get(bot('getme'))
pprint(r.json())

r = requests.post(bot('setwebhook'), data = { 'url': sys.argv[1] })
pprint(r.json())

r = requests.get(bot('getwebhookinfo'))
pprint(r.json())
