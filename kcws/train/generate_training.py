# -*- coding: utf-8 -*-
# @Author: Koth Chen
# @Date:   2016-10-21 16:17:53
# @Last Modified by:   Koth
# @Last Modified time: 2016-12-01 17:09:45

import sys
import os
import w2v

totalLine = 0
longLine = 0

MAX_LEN = 80
totalChars = 0


class Setence:
  def __init__(self):
    self.tokens = []
    self.chars = 0

  def addToken(self, t):
    self.chars += len(t)
    self.tokens.append(t)

  def clear(self):
    self.tokens = []
    self.chars = 0

  # label -1, unknown
  # 0-> 'S'
  # 1-> 'B'
  # 2-> 'M'
  # 3-> 'E'
  def generate_tr_line(self, x, y, vob):
    for t in self.tokens:
      if len(t) == 1:
        x.append(vob.GetWordIndex(str(t[0].encode("utf8"))))
        y.append(0)
      else:
        nn = len(t)
        for i in range(nn):
          x.append(vob.GetWordIndex(str(t[i].encode("utf8"))))
          if i == 0:
            y.append(1)
          elif i == (nn - 1):
            y.append(3)
          else:
            y.append(2)


def processToken(token, sentence, out, end, vob):
  global totalLine
  global longLine
  global totalChars
  global MAX_LEN
  nn = len(token)
  while nn > 0 and token[nn - 1] != '/':
    nn = nn - 1

  token = token[:nn - 1].strip()
  if token != '。':
    ustr = unicode(token.decode('utf8'))
    sentence.addToken(ustr)
  uline = u''
  if token == '。' or end:
    if sentence.chars > MAX_LEN:
      longLine += 1
    else:
      x = []
      y = []
      totalChars += sentence.chars
      sentence.generate_tr_line(x, y, vob)
      nn = len(x)
      assert (nn == len(y))
      for j in range(nn, MAX_LEN):
        x.append(0)
        y.append(0)
      line = ''
      for i in range(MAX_LEN):
        if i > 0:
          line += " "
        line += str(x[i])
      for j in range(MAX_LEN):
        line += " " + str(y[j])
      out.write("%s\n" % (line))
    totalLine += 1
    sentence.clear()


def processLine(line, out, vob):
  line = line.strip()
  nn = len(line)
  seeLeftB = False
  start = 0
  sentence = Setence()
  try:
    for i in range(nn):
      if line[i] == ' ':
        if not seeLeftB:
          token = line[start:i]
          if token.startswith('['):
            tokenLen = len(token)
            while tokenLen > 0 and token[tokenLen - 1] != ']':
              tokenLen = tokenLen - 1
            token = token[1:tokenLen - 1]
            ss = token.split(' ')
            for s in ss:
              processToken(s, sentence, out, False, vob)
          else:
            processToken(token, sentence, out, False, vob)
          start = i + 1
      elif line[i] == '[':
        seeLeftB = True
      elif line[i] == ']':
        seeLeftB = False
    if start < nn:
      token = line[start:]
      processToken(token, sentence, out, True, vob)
  except Exception as e:
    pass


def main(argc, argv):
  global totalLine
  global longLine
  global totalChars
  if argc < 4:
    print("Usage:%s <vob> <dir> <output>" % (argv[0]))
    sys.exit(1)
  vobPath = argv[1]
  rootDir = argv[2]
  vob = w2v.Word2vecVocab()
  vob.Load(vobPath)
  out = open(argv[3], "w")
  for dirName, subdirList, fileList in os.walk(rootDir):
    curDir = os.path.join(rootDir, dirName)
    for file in fileList:
      if file.endswith(".txt"):
        curFile = os.path.join(curDir, file)
        #print("processing:%s" % (curFile))
        fp = open(curFile, "r")
        for line in fp.readlines():
          line = line.strip()
          processLine(line, out, vob)
        fp.close()
  out.close()
  print("total:%d, long lines:%d, chars:%d" %
        (totalLine, longLine, totalChars))


if __name__ == '__main__':
  main(len(sys.argv), sys.argv)