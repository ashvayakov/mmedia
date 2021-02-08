#!/usr/bin/env python2.7
# Extracting sound tracks from cue and encoding them to the flac
import subprocess as subp
import sys
import os
from os.path import splitext, basename
import random
import glob

records = []
filename = ""
album=''
alb_artist=''
codec = 'flac'
ffmpeg_exec = 'ffmpeg'
encodingList = ('utf-8','euc-kr', 'shift-jis', 'cp936', 'big5')

filecontent = open(sys.argv[1]).read()
for enc in encodingList:
    try:
        lines = filecontent.decode(enc).split('\n')
        encoding = enc
        break
    except UnicodeDecodeError as e:
        if enc == encodingList[-1]:
            raise e
        else:
            pass

for l in lines:
    a = l.split()
    if not a:
        continue
    if a[0] == "FILE":
        filename = ' '.join(a[1:-1]).strip('\'"')
    elif a[0]=='TRACK':
        records.append({})
        records[-1]['index'] = a[1]
    elif a[0]=='TITLE':
        if len(records)>0:
            records[-1]['title'] = ' '.join(a[1:]).strip('\'"')
        else:
            album =  ' '.join(a[1:]).strip('\'"')
    elif a[0]=='INDEX' and a[1]=='01':
        timea = a[2].split(':')
        if len(timea) == 3 and int(timea[0]) >= 60:
            timea.insert(0, str(int(timea[0])/60))
            timea[1] = str(int(timea[1])%60)
        times = '{0}.{1}'.format(':'.join(timea[:-1]), timea[-1])
        records[-1]['start'] = times
    elif a[0]=='PERFORMER':
        if len(records)>1:
            records[-1]['artist'] = ' '.join(a[1:]).strip('\'"')
        else:
            alb_artist = ' '.join(a[1:]).strip('\'"')

for i, j in enumerate(records):
    try:
        j['stop'] = records[i+1]['start']
    except IndexError:
        pass

if not os.path.isfile(filename):
    tmpname = splitext(basename(sys.argv[1]))[0]+splitext(filename)[1]
    if os.path.exists(tmpname):
        filename = tmpname
        del tmpname
    else:
        for ext in ('.ape', '.flac', '.wav', '.mp3'):
            tmpname = splitext(filename)[0] + ext
            if os.path.exists(tmpname):
                filename = tmpname
                break

if not os.path.isfile(filename):
    raise IOError("Can't not find file: {0}".format(filename))

fstat = os.stat(filename)
atime = fstat.st_atime
mtime = fstat.st_mtime

records[-1]['stop'] = '99:59:59'

if filename.lower().endswith('.flac'):
    tmpfile = filename
else:
    tmpfile = splitext(filename)[0] + str(random.randint(10000,90000)) + '.flac'

try:
    if filename != tmpfile:
        ret = subp.call([ffmpeg_exec, '-hide_banner', '-y', '-i', filename, 
            '-c:a', codec,'-compression_level','12','-f','flac',tmpfile])

        if ret != 0:
            raise SystemExit('Converting failed.')

    for i in records:
        output = i['index'] +' - '+ i['title']+'.flac'
        commandline = [ffmpeg_exec, '-hide_banner', 
        '-y', '-i', tmpfile,
        '-c', 'copy', 
        '-ss', i['start'], '-to', i['stop'],
        '-metadata', u'title={0}'.format(i['title']), 
        '-metadata', u'artist={0}'.format(i.get('artist', '')),
        '-metadata', u'performer={0}'.format(i.get('artist', '')),
        '-metadata', u'album={0}'.format(album), 
        '-metadata', 'track={0}/{1}'.format(i['index'], len(records)), 
        '-metadata', u'album_artist={0}'.format(alb_artist), 
        '-metadata', u'composer={0}'.format(alb_artist), 
        '-metadata', 'encoder=Meow', 
        '-write_id3v1', '1', 
        output]
        ret = subp.call(commandline)
        if ret == 0:
            os.utime(output, (atime, mtime))
finally:
    if os.path.isfile(tmpfile):
        os.remove(tmpfile)

