from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import ast

import xmlrpclib
import json
import helper

model = 'res.company' # default model

url = 'http://128.199.198.251:8069'
db = 'topvalue'
username = 'admin'
password = 'topvalue'

common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})
models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

def exc(method, where, limit = ''):
  return models.execute_kw(db, uid, password, model, method, where, limit)

def dumps(data):
  return json.dumps(data, indent=2, sort_keys=True)

@csrf_exempt
def index(request):

  return HttpResponse('Hello World!')

'''
https://docs.djangoproject.com/en/1.8/ref/request-response/
method
  - search
  - search_count
  - search_read
  - read
  - fields_get
  - check_access_rights
'''

# /api/company/
@csrf_exempt
def endpoint(request):

  global model
  model = request.GET.get('model','res.company')
  method = request.method
  ids = ''

  # get ids object
  if request.GET.get('id'):
    ids = exc('search', [[['id', '=', request.GET.get('id')]]],{'limit': 1})

  if request.GET.get('name'):
    ids = exc('search',[[['name', '=', request.GET.get('name')]]],{'limit': 1})

  if method == 'POST':
    id = exc('create',[ast.literal_eval(request.body)])
    output = exc('search_read',[[['id','=',id]]],{'fields': ['id','name']})
    
  elif method == 'PUT':
    exc('write',[ids,ast.literal_eval(request.body)])
    output = exc('name_get',[ids])

  elif method == 'DELETE':
    output = exc('unlink', [ids])

  elif method == 'GET':
    if request.GET.get('field'):
      output = exc('fields_get',[],{'attributes': ['string', 'help', 'type']})
    elif ids:
      [output] = exc('read',[ids])
    else:
      output = exc('search_read',[[]],{'fields': ['id','name']})

  result = dumps(output)
  return HttpResponse(result)
