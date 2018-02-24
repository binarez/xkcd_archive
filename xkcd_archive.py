#! python3

# @author Stephane Duguay // binarez

# Derived from downloadXkcd.py - Downloads every single XKCD comic.
#			  https://codereview.stackexchange.com/questions/178239/archives-xkcd-comics

"""
Webscraper that downloads xkcd comics.
Checks if comic already downloaded so for increased efficiency on rerun.

Two run modes: Full and Update
Full mode goes through every comic.
Update mode quits when it reaches the first comic that is already downloaded.

Derived from original project: https://automatetheboringstuff.com/chapter11/

@author: david.antonini // toonarmycaptain
"""
import time
import os
import requests
import bs4
import threading

print('This script searches xkcd.com and downloads each comic.')

# User input for full run or until finding already downloaded comic.
print('There are two mode options:\n'
	  'Update mode: Or "refresh mode", checks until it finds '
	  'a previously downloaded comic.\n'
	  'Full mode: Checks for every comic, downloads undownloaded comics.\n'
	  )

while True:
	try:
		print('Please select mode:\n'
			  'Enter 0 for Update mode, or 1 for Full mode')
		run_mode_selection = input('Mode: ')
		if int(run_mode_selection) == 0:
			full_mode = False  # Update mode
			break
		if int(run_mode_selection) == 1:
			full_mode = True	# Full mode
			break
	except ValueError:
		continue

start = time.time()


os.makedirs('xkcd_archive', exist_ok=True)   # store comics in ./xkcd


def download_image(session, url, filename):
	with open(os.path.join('xkcd_archive', filename), 'xb') as image_file:
		print('Downloading image ' + filename)
		res = session.get(url)
		res.raise_for_status()
		for chunk in res.iter_content(100000):
			image_file.write(chunk)

# Get latest comic number:
url = 'https://xkcd.com/archive/'
res = requests.get(url)
res.raise_for_status()
soup = bs4.BeautifulSoup(res.text, 'lxml')
all_comics = soup.select("div[id=middleContainer] > a[title]")

with requests.Session() as session:
	for comic in all_comics:
		comic_num = int(comic.get('href')[1:-1])
		try:
			res = session.get('http://xkcd.com/' + str(comic_num))
			res.raise_for_status()
			soup = bs4.BeautifulSoup(res.text, 'lxml')
		except requests.exceptions.HTTPError:
			continue

		comic_image = soup.select_one('#comic img[src]')
		if not comic_image:
			print('Could not find comic image #' + str(comic_num))
			continue

		try:
			comic_url = 'https:' + comic_image['src']
			download_image(session, comic_url,
							'xkcd.' + str(comic_num) + '.' +  comic.get('title') + '.' + os.path.basename(comic_url))
		except requests.exceptions.MissingSchema:
			print('--- Missing comic ' + str(comic_num))
			continue  # skip this comic
		except FileExistsError:
			if full_mode:   # Full mode
				continue  # skip this comic
			if not full_mode:
				break

print('Done.')
