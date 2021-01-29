import sys
import urllib.request
import ssl
import json

from datetime import datetime
from lxml.etree import Element, SubElement, QName, tostring, CDATA

def generate_gpx_header():
	nsmap = {
		'xsd': 'http://www.w3.org/2001/XMLSchema',
		'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
	}
	
	qname = QName('http://www.w3.org/2001/XMLSchema-instance', 'schemaLocation')
	
	gpx = Element('gpx', { qname: 'http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd http://www.groundspeak.com/cache/1/0/1 http://www.groundspeak.com/cache/1/0/1/cache.xsd' }, nsmap=nsmap, version='1.0', creator='FJSFerreira', xmlns='http://www.topografix.com/GPX/1/0')
	
	nameElement = SubElement(gpx, 'name')
	nameElement.text = 'Geocaching Adventure Lab'
	
	descElement = SubElement(gpx, 'desc')
	descElement.text = 'Geocaching Adventure Lab'
	
	authorElement = SubElement(gpx, 'author')
	authorElement.text = 'FJSFerreira'
	
	timeElement = SubElement(gpx, 'time')
	timeElement.text = str(datetime.now())
	
	keywordsElement = SubElement(gpx, 'keywords')
	keywordsElement.text = 'lab cache, cache, geocache, groundspeak'
	
	return gpx

def generate_gpx(data):
	gpx = generate_gpx_header()
	
	for adventure in data['Items']:
		print('Getting adventure data: ' + adventure['Title'] + '...', file=sys.stderr)
		
		adventure_url = 'https://labs-api.geocaching.com/Api/Adventures/'+adventure['Id']
		
		with urllib.request.urlopen(adventure_url, context=ssl.SSLContext()) as url:
			data = json.loads(url.read().decode())
			
			for index, location in enumerate(data['GeocacheSummaries']):
				print('Getting location data: ' + location['Title'] + '...', file=sys.stderr)
				
				wptElement = SubElement(gpx, 'wpt')
				wptElement.set('lat', str(location['Location']['Latitude']))
				wptElement.set('lon', str(location['Location']['Longitude']))
				
				wptNameElement = SubElement(wptElement, 'name')
				wptNameElement.text = location['Id']
				
				wptDescElement = SubElement(wptElement, 'desc')
				wptDescElement.text = data['Title'] + (' (#' + str(index+1) + ')' if data['IsLinear'] == True else '') + ' - ' + location['Title']
				
				wptSymElement = SubElement(wptElement, 'sym')
				wptSymElement.text = 'Geocache'
				
				gsns = 'http://www.groundspeak.com/cache/1/0/1'
				gsnsmap = { 'groundspeak': gsns }
				
				cacheElement = SubElement(wptElement, '{' + gsns + '}cache', nsmap=gsnsmap)
				cacheElement.set('id', location['Id'])
				cacheElement.set('available', 'True')
				cacheElement.set('archived', 'False')
				
				cacheNameElement = SubElement(cacheElement, '{' + gsns + '}name')
				cacheNameElement.text = data['Title'] + (' (#' + str(index+1) + ')' if data['IsLinear'] == True else '') + ' - ' + location['Title']
				
				cacheOwnerElement = SubElement(cacheElement, '{' + gsns + '}owner')
				cacheOwnerElement.text = data['OwnerUsername']
				cacheOwnerElement.set('id', '0')
				
				cacheTypeElement = SubElement(cacheElement, '{' + gsns + '}type')
				cacheTypeElement.text = 'Lab Cache'
				
				cacheDifficultyElement = SubElement(cacheElement, '{' + gsns + '}difficulty')
				cacheDifficultyElement.text = '0'
				
				cacheTerrainElement = SubElement(cacheElement, '{' + gsns + '}terrain')
				cacheTerrainElement.text = '0'
				
				cacheShortDescriptionElement = SubElement(cacheElement, '{' + gsns + '}short_description')
				cacheShortDescriptionElement.text = '<img src="' + data['KeyImageUrl'] + '"/><br/><br/>' + data['Description'] + '<br/><br/>'
				cacheShortDescriptionElement.set('html', 'false')
				
				cacheLongDescriptionElement = SubElement(cacheElement, '{' + gsns + '}long_description')
				cacheLongDescriptionElement.text = '<img src="' + location['KeyImageUrl'] + '"/><br/><br/>' + (location['Description'] + '<br/><br/>' + location['Question'] + '<br/><br/>' + str(location['CompletionAwardMessage']))
				cacheLongDescriptionElement.set('html', 'false')
				
		print('-----', file=sys.stderr)
				
	return gpx

def fetch_data():
	list_url = 'https://labs-api.geocaching.com/Api/Adventures/SearchV3?origin.latitude='+latitude+'&origin.longitude='+longitude+'&radiusMeters='+radius
	
	with urllib.request.urlopen(list_url, context=ssl.SSLContext()) as url:
		data = json.loads(url.read().decode())
		return generate_gpx(data)

if len(sys.argv) < 2:
	print('Parameter error! Usage: <latitude> <longitude> <radius, default=60000>', file=sys.stderr)
else:
	latitude = sys.argv[1]
	longitude = sys.argv[2]
	radius = sys.argv[3] if len(sys.argv) > 3 else '60000'
	
	print('Center: ' + latitude + ',' + longitude, file=sys.stderr)
	print('Radius: ' + radius + ' m', file=sys.stderr)
	
	gpx = fetch_data()
	print('<?xml version="1.0" encoding="utf-8"?>')
	print(tostring(gpx, encoding='unicode', method='xml', pretty_print=True))
