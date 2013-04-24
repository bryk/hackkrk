#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Piotr Bryk
import urllib
import json
import sys
import math
from PIL import Image

def Usage():
  print('Usage: ./paint.py `find imgs/ -name \'*.png\'`')

def Main():
  if not sys.argv[1:]:
    Usage()
  else:
    imgs, means, names = ReadAllImgs()
    while True:
      try:
        DoChallenge(imgs, means, names)
      except Exception as e:
        print(e)

def DoChallenge(imgs, means, names):
  data = r'api_token=implement sticky eyeballs'
  ret = urllib.urlopen('http://canvas.hackkrk.com/api/new_challenge', data.encode('utf-8'))
  data = ret.read().decode('utf-8')
  js = json.loads(data)
  print(js['color'])
  SendImageBrut(imgs, means, names, js)

def ModifyOne(im, ind, val):
  for x in xrange(64):
    for y in xrange(64):
      c = im[x, y]
      if c[ind] + val > 255 or c[ind] + val < 0:
        continue
      else:
        newc = list(c)
        newc[ind] += val
        im[x, y] = tuple(newc)

def Mean(im):
  sr, sg, sb = 0, 0, 0
  for x in range(64):
    for y in range(64):
      c = im[x, y]
      sr += c[0]
      sg += c[1]
      sb += c[2]
  sz = 64*64
  return (sr/sz, sg/sz, sb/sz)

def ReadAllImgs():
  imgs = []
  means = []
  names = []
  for name in sys.argv[1:]:
    print('Read image:', name)
    im = Image.open(name).resize((64, 64))
    l = im.load()
    if type(l[0, 0]) == int or len(l[0, 0]) < 3:
      print('skip', name)
      continue
    imgs += [im]
    means += [Mean(l)]
    names += [name]
  return imgs, means, names

def Dst(a, b):
  return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)

def PickTheBest(_imgs, means, names, c):
  bestind = 0
  bestdst = 0xffa
  for i in range(len(means)):
    ac = means[i]
    dst = Dst(c, ac)
    if dst < bestdst:
      bestdst = dst
      bestind = i
  print('bestdst', bestdst, 'name', names[bestind])
  return bestind

def ReadImg(imgs, means, names, js):
  cl = tuple(js['color'])
  png = imgs[PickTheBest(imgs, means, names, cl)]
  data = png.load()
  while Mean(data) != cl:
    cr, cg, cb = Mean(data)
    if cr < cl[0]:
      ModifyOne(data, 0, 1)
    elif cr > cl[0]:
      ModifyOne(data, 0, -1)
    if cg < cl[1]:
      ModifyOne(data, 1, 1)
    elif cg > cl[1]:
      ModifyOne(data, 1, -1)
    if cb < cl[2]:
      ModifyOne(data, 2, 1)
    elif cb > cl[2]:
      ModifyOne(data, 2, -1)
    #print(cr, cg, cb)
  #png.show()
  return png

def GetBase(png):
  ''' :) '''
  png.save('out.png')
  s = open('out.png', 'rb').read().encode('base64')
  #print(s)
  return s

def SendImageBrut(imgs, means, names, js):
  img = ReadImg(imgs, means, names, js)
  base = GetBase(img)
  args = []
  args += [('Content-Type','application/json')]
  args += [('api_token', 'implement sticky eyeballs')]
  args += [('image', base)] 
  s = urllib.urlencode(args)
  url = 'http://canvas.hackkrk.com/api/challenge/' + str(js['id']) + '.json'
  ret = urllib.urlopen(url, s.encode('utf-8'))
  data = ret.read().decode('utf-8')
  js = json.loads(data)
  print('Accepted:', js['accepted'])

if __name__ == '__main__':
  Main()

