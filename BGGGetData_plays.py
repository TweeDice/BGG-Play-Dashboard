import urllib.request
import xml.etree.ElementTree as ET

import pandas as pd
import math
import sys

######################################################
#This Script gets play data and associated game data
#for a BGG user.
#-u             BGG user name *required
#-pages         Number of pages of game (~100 plays = 3 pages)
#-detail (True) Boolean That Prints Detailed Info
#Created by Michael Waldmeier
######################################################

USER_NAME = ''
PLAY_PAGES = 50
DETAIL = False

OUT_FILE_NAME = 'play_data.csv'

def getopts(argv):
	opts = {}  # Empty dictionary to store key-value pairs.
	while argv:  # While there are arguments left to parse...
		if argv[0][0] == '-':  # Found a "-name value" pair.
			opts[argv[0]] = argv[1]  # Add key and value to the dictionary.
		argv = argv[1:]  # Reduce the argument list by copying it starting from index 1.
	return opts

def set_argvs():
	global USER_NAME, PLAY_PAGES, DETAIL
	myargs = getopts(sys.argv)

	if '-u' in myargs:
		USER_NAME = myargs['-u']
	else:
		print('Error: No BGG User Name Provided')
		sys.exit()

	if '-pages' in myargs:
		PLAY_PAGES = int(myargs['-pages'])

	if '-detail' in myargs:
		DETAIL = True

def urlopen_with_retry(url):
	for _ in range(4):
		try:
			page = urllib.request.urlopen(url)
			break  # success
		except:
			print ('sleeping')
			time.sleep(3)
			raise  # propagate non-timeout errors
	else:  # all ntries failed
		raise   # re-raise the last timeout error
		# use page here
	return page

def htmlRequest_plays(page):
	urlTop = 'https://www.boardgamegeek.com/xmlapi2/plays'
	urlBottom = '?username=' + USER_NAME + '&page=' + str(page)
	file = urlopen_with_retry(urlTop + urlBottom)

	if DETAIL:
		print(urlTop + urlBottom)


	tree = ET.parse(file)
	doc = tree.getroot()
	file.close()

	return doc

def get_play_data():

	plays_pd = pd.DataFrame(columns=['game', 'id', 'date', 'quantity'])

	#get play data
	for page in range(1, PLAY_PAGES+1):#get up to 50 pages by default
		xml = htmlRequest_plays(page)
		if len(xml.findall('play')) > 0:
			for play in xml.findall('play'):
				item = play.find('item')
				temp = pd.DataFrame({'game'     : [item.get('name')],
				                     'id'       : [item.get('objectid')],
				                     'date'     : [play.get('date')],
				                     'quantity' : [play.get('quantity')]
				                     })
				plays_pd = pd.concat([plays_pd, temp])
		else:
			break

	if DETAIL:
		print('Play Data Collected')

	return plays_pd

#Get Game Stats

def set_pull_sets(plays_pd):
	#set limit on number of game stats per call
	games_played = plays_pd['id'].unique()
	game_sets = []

	set_size = 100 #games to get in one call
	for set in range(1, math.ceil(len(games_played) / set_size)+1):
		temp_set  = ",".join(games_played[(set-1)*set_size:set * set_size])
		game_sets.append(temp_set)

	return game_sets

def htmlRequest_games(game_id):
	urlTop = 'https://www.boardgamegeek.com/xmlapi2/thing'
	urlBottom = '?id=' + game_id + '&stats=1'
	file = urlopen_with_retry(urlTop + urlBottom)

	tree = ET.parse(file)
	doc = tree.getroot()
	file.close()

	return doc

def pull_game_stats(plays_pd):
	game_sets = set_pull_sets(plays_pd)

	lookup_games_pd = pd.DataFrame(columns=['id', 'yearpublished', 'playingtime', 'minplayers', 'maxplayers'
		, 'rating_average', 'rating_bayesaverage'])

	for game_id_sets in game_sets:
		if DETAIL:
			print('Getting Stats...')

		xml = htmlRequest_games(game_id_sets)
		games = xml.findall('item')
		for game in games:
			temp = pd.DataFrame({
				'id'                      : [game.get('id')],
				'yearpublished'           : [game.find('yearpublished').get('value')],
				'playingtime'             : [game.find('playingtime').get('value')],
				'minplayers'              : [game.find('minplayers').get('value')],
				'maxplayers'              : [game.find('maxplayers').get('value')],
				'rating_average'          : [game.find('statistics').find('ratings').find('average').get('value')],
				'rating_bayesaverage'     : [game.find('statistics').find('ratings').find('bayesaverage').get('value')]
			})
			lookup_games_pd = pd.concat([lookup_games_pd, temp])

	if DETAIL:
		print('Game Stats Collected')

	return lookup_games_pd

def join_game_data(plays_pd, lookup_games_pd):
	return pd.merge(plays_pd, lookup_games_pd, how='left', on='id')

if __name__ == '__main__':
	set_argvs()
	plays_pd = get_play_data()
	lookup_games_pd = pull_game_stats(plays_pd)
	joined_pd = join_game_data(plays_pd, lookup_games_pd)

	joined_pd.to_csv(OUT_FILE_NAME, index=False)

	print(OUT_FILE_NAME, 'Created')