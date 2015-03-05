#-*-coding:utf8;-*-
#qpy:console
#qpy:2
"""
This is the beta version of streaMe

version: 0.1

@Author: Gurzo
@Date: 2015-03-05
"""

import androidhelper
import json
import pafy
import re
import urllib

droid = None
	
def play(url):
	global droid
	droid.dialogCreateSpinnerProgress(title='Retrieving video information',message='Please wait',maximum_progress=100)
	droid.dialogShow()
	video = None 
	try:
		video = pafy.new(url)
	except:
		droid.makeToast('Not valid YouTube URL')
		return False
	droid.dialogDismiss()
	audiostreams = video.audiostreams
	audioquality = [a.bitrate + ' - ' + '%.2f' % round((float(a.get_filesize()) / 1024 )/ 1024, 2) + 'MB' for a in audiostreams]
	choice = choose('Select audio quality', audioquality, no = 'Cancel', yes = 'Best!')
	stream = ''
	if choice == 'positive':
		stream = video.getbestaudio().url
	elif choice == 'negative' or choice == 'c':
		return False
	else:
		stream = audiostreams[choice].url 
	title = str(video.title)
	extrap = {'itemTitle':title}
	try:
		activity = droid.startActivityForResult('android.intent.action.VIEW', 
		                    uri = stream, 
							extras = extrap, 
							type = 'application/mp4', 
							packagename = 'org.videolan.vlc.betav7neon')
		assert activity.error == None
		return True
	except:
		return False

def searchYT(word, page):
	global droid
	droid.dialogCreateSpinnerProgress(title='Searching',message='Please wait',maximum_progress=100)
	droid.dialogShow()
	param = { 'q' : word, 'sm' : '3', 'filters' : 'video', 'lclk' : 'video', 'page' : page}
	query = urllib.urlencode(param)
	url = 'https://www.youtube.com/results?' + query
	htmlSource = urllib.urlopen(url).read()
	search_results = re.findall(r'href=\"\/watch\?v=(.{11})', htmlSource)
	urls = ['http://www.youtube.com/watch?v=' + id for id in search_results[0:][::2]]
	titles = re.findall('title=\"([^"]{5,})\" rel="spf-prefetch" aria-describedby', htmlSource)
	if len(titles) == 0:
		titles = re.findall('title=\"([^"]{5,})\" aria-describedby', htmlSource)
	droid.dialogDismiss()
	return (titles, urls)
	
def search(by = '', page = 1):	
	word = ''
	if page == 1:
		line = droid.dialogGetInput(title='YouTube', message='Search for')
		if line.result == None or line.result == 'negative':
			return
		word = line.result
	else:
		word = by
	result  = searchYT(word, page)
	played = False
	while True:
		choice = choose('Search result on page ' + str(page), result[0], no='Cancel', yes='Next page')
		if choice == 'negative':
			return search()
		elif choice == 'positive':
			search(word, page+1)
		elif choice < len(result[1]):
			played = play(result[1][choice])
		else:
			break
	return played

def insert():
	global droid
	line = droid.dialogGetInput(title='YouTube Video to VLC Audio Stream', message='Insert URL')
	if line.result == '':
		droid.makeToast('You must insert a URL!')
		return insert()
	elif line.result != None:
		url = line.result
		played = play(url)
		if not played:
			return insert()
		return True
	return False
	
def choose(title, flist, no = 0, yes = 0):
	global droid
	droid.dialogCreateAlert(title, '')
	droid.dialogSetItems(flist)
	if yes:
		droid.dialogSetPositiveButtonText(yes)
	if no:
		droid.dialogSetNegativeButtonText(no)
	droid.dialogShow()
	resp = droid.dialogGetResponse()
	droid.dialogDismiss()
	s = 0
	if resp.result.has_key('item'):
		return resp.result['item']
	if resp.result.has_key('which'):
		return resp.result['which']
	elif resp.result.has_key("canceled"):
		return 'c'
	return resp.result

def createDroid():
	try:
		global droid
		droid = androidhelper.Android()
	except:
		print 'Error encurred during init operation, please restart application.'
		print 'If the problem persist, please restart your device'
		exit(0)

def main():
	createDroid()
	while 1:
		title = 'Welcome to StreaMe'
		flist = ['Search on YouTube', 'Insert URL']
		action = choose(title, flist, no = 'Exit')
		if action == 1:
			insert()
		elif action == 0:
			search()
		elif action == 'negative':
			exit(0)
		elif action == 'c':
			exit(0)

if __name__ == '__main__':
	main()
