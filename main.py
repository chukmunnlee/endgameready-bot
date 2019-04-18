import sys, os, time, io
import hashlib, requests, json
from flask import Flask
from flask import request as flask_req

from pprint import pprint

from lru import *

KEYS = [ 'APP_PORT', 'MARVEL_PUBLIC', 'MARVEL_PRIVATE', 'TELEGRAM_TOKEN' ]
URL = 'https://gateway.marvel.com:443/v1/public/characters'
TEMPLATE = '<b>%s</b><pre>%s</pre><code>%s</code>'

# construct the result
def extractResult(payload):
   result = []
   for _, v in enumerate(payload['data']['results']):
      c = {}
      c['attribution'] = payload['attributionText']
      c['name'] = v['name']
      c['description'] = v['description']
      c['image'] = '%s.%s' %(v['thumbnail']['path'], v['thumbnail']['extension'])
      c['image_name'] = '%s.%s' %(v['name'], v['thumbnail']['extension'])
      result.append(c)
   return (result)

def extractQuery(payload):
   if 'message' not in payload:
      return None
   result = {}
   result['chat_id'] = payload['message']['from']['id']
   result['text'] = payload['message']['text'].strip()
   result['parse_mode'] = 'HTML'
   return result

def queryMarvel(char_name):

   ts = str(int(time.time()))
   h = '%s%s%s' %(ts, params['MARVEL_PRIVATE'], params['MARVEL_PUBLIC'])

   md5 = hashlib.md5()
   md5.update((h).encode('utf-8'))

   qs = {
      'name': char_name,
      'apikey': params['MARVEL_PUBLIC'],
      'ts': ts,
      'hash': md5.hexdigest() }

   r = requests.get(URL, params=qs)
   if r.status_code >= 400:
      return (False, 'Cannot find any info on %s' %char_name, 'ok', 200)

   result = extractResult(r.json())
   if len(result) <= 0:
      return (False, 'Cannot find any info on %s' %char_name, 'ok', 200)

   return (True, result, '', 0)

def make_bot(token):
   def a(res, *args, **kwargs):
      url = 'https://api.telegram.org/bot%s/%s' %(token, res)
      if len(args) > 0:
         return requests.post(url, files=args, data=kwargs)
      return requests.get(url, data=kwargs)
   return a

def get_image(url):
   r = requests.get(url)
   photo = io.BytesIO(r.content)
   return photo

# main program

app = Flask(__name__)

params = { 'APP_PORT': '3000' }

for _, v in enumerate(KEYS):
   if v in os.environ:
      params[v] = os.environ[v]

bot = make_bot(params['TELEGRAM_TOKEN'])

lru = LRU(30)

@app.route('/')
def index():
   return 'hello world', 200

#@app.route('/%s' %params['TELEGRAM_TOKEN'], methods=['POST'])
@app.route('/character', methods=['POST'])
def character():
   payload = flask_req.get_json() 

   data = extractQuery(payload)
   if data is None:
      return 'strange no payload', 200

   # check cache
   found, result = lru.get(data['text'])
   if found:
      print('cache hit: ', data['text'])
      if result is None:
         data['text'] = 'Cannot find any info on %s' %data['text']
         bot('sendMessage', **data)
         return 'ok', 200

   else:
      cont, result, status_msg, status_code = queryMarvel(data['text'])
      lru.put(data['text'], result if cont else None)
      if not cont:
         data['text'] = result
         bot('sendMessage', **data)
         return status_msg, status_code

   for _, v in enumerate(result):
      data['photo'] = v['image']
      r = bot('sendPhoto', **data)
      #print('sendPhoto: %d' %r.status_code, r.text)

      data['text'] = TEMPLATE %(v['name'], v['description'], v['attribution'])
      r = bot('sendMessage', **data)
      #print('sendMessage: %d' %r.status_code, r.text)

   return 'ok', 200

if __name__ == '__main__':
   if len(params) < 4:
      print('Error missing requirement params: MARVEL_PUBLIC, MARVEL_PRIVATE')
      exit(0)
   print('Running on port ', params['APP_PORT'])
   app.run(port=int(params['APP_PORT']), debug=True)
