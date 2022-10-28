#!/usr/bin/env python3

import argparse
import ast
from collections import OrderedDict
import errno
import json
import os
from os.path import basename
import shelve
import sys

tempstore = {}
fds = {}

parser=argparse.ArgumentParser()

parser.add_argument('-c','--clear-store',action='store_true', help='clear store'
)
parser.add_argument('-s','--store',action='store_true', help='print value of store'
                    )
parser.add_argument('-i','--input',action='append', metavar='config_filename',
                    help='names of files containing JSON configuration')
parser.add_argument('actions', metavar='action', type=str, nargs='*', 
                    help='actions to be applied to the config files')

opt = parser.parse_args()

store = shelve.open(os.path.expanduser('~/.store.{}'.format(basename(sys.argv[0]))))

if opt.clear_store:
  store.clear()

if opt.store:
  import pprint
  pprint.pprint(dict(store))
  exit()

def PRESERVE_check(): return PRESERVE('check')
def PRESERVE_force(): return PRESERVE('force')
def PRESERVE(modifier = 'no-replace'):
  #retval = []
  if opt.input:
    for fname in opt.input:
      key = '\0i'+ fname
      existing = store.get(key,'')
      if existing and modifier == 'check':
        truth = (existing == tempstore[fname])
        assert truth, 'PRESERVE mismatch in {} - maybe due to missed or failed RESTORE'.format(j)
      if modifier == 'force' or not existing:
        store[key] = tempstore[fname]
  #return not(retval) or all(retval)

def RESTORE():
  input_ = [ (k[2:],j) for k,j in store.items() if k.startswith('\0i') ]
  filt = None if not opt.input else lambda x:x[0] in opt.input
  input_ = filter(filt,input_)
  for f,j in input_:
    open(f,'w').write(json.dumps(j,indent=4))
  global do_savefiles
  do_savefiles=False
  
def VAR(v,do_store=False):
  if do_store:
    pfx,rest = v.split('*',1)
    store['\0v'+rest]=pfx
  else:
    return store.get('\0v'+v,'')+v

def savefiles():
  for fname,fd in fds.items():
    fd = fds[fname]
    fd.seek(0)
    fd.write(json.dumps(tempstore[fname],indent=4))
    fd.truncate()
    fd.close()

def loadfile(fname):
    s= ''
    try:
      f = open(fname,'r+')
    except (IOError,OSError) as exc:
      if exc.errno == errno.ENOENT:
        f = open(fname,'w+')
      else:
        raise
    s = f.read()
    if not s:
      j = {}
    else:
      j = json.loads(s,object_hook = OrderedDict)
    tempstore[fname] = j
    fds[fname] = f

funcs = {x:globals()[x] for x in ('PRESERVE',
				  'RESTORE',
				  'PRESERVE_check',
				  'PRESERVE_force'  )}

def isVARitem(item): return item.startswith('VAR=')
def notVARitem(item): return not(isVARitem(item))

do_savefiles=True

def main():

  if opt.input:
    for s in opt.input:
      loadfile(s)

  for c in filter(isVARitem,opt.actions):
    name,value = c.split('=',1)
    VAR(value,True)

  # special case - RESTORE all items in store regardless of argv input
  if 'RESTORE' in opt.actions and not fds:
    RESTORE()

  for fname,f in fds.items():
    j = tempstore[fname]
    for c in filter(notVARitem,opt.actions):
      name,value = c.split('=',1) if '=' in c else (c,'')
      if name in funcs:
         funcs[name]()  # RESTORE, PRESERVE[_*] for the list of fds active
         continue
      if not value:
        del j[VAR(name)]
      else:
        j[VAR(name)] = ast.literal_eval(value)

  if do_savefiles:
    savefiles()

if __name__ == '__main__':
  main()
