#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Import necessary libraries
import lcddriver
import pywapi
import socket
import string
import sys
import time
from time import gmtime,strftime


#Initialize import items
lcd = lcddriver.lcd()
ZipCode = '11209'
REMOTE_SERVER = "www.google.com"
PianobarOutLocation = '/home/pi/projects/piclock/out'
SongTimeout = 180
global SongAndArtistNamePrev
SongAndArtistNamePrev = ''
global ElapsedSongTime
ElapsedSongTime = 181
refreshDelay = 4
global weatherRefresh
weatherRefresh = 3500
global weatherConstant
weatherConstant = 3600
global SongValue
SongValue = 0

#First function to call Sets up important variables and misc.
def Initialize():
	ScriptStartTime = time.strftime("%I:%M:%S %a %m:%d:%Y %z")
	print ScriptStartTime
	print 'Pi Clock Starting'

	lcd.lcd_display_string(string.center("Welcome To",20),2)
	lcd.lcd_display_string(string.center("Pi Clock",20),3)
	time.sleep(1)
	clear(3)
	clear(2)
	lcd.lcd_display_string(string.center("Pi Clock",20),3)
	lcd.lcd_display_string(string.center("Starting...",20),3)
	global weatherRefresh
	weatherRefresh = weatherRefresh/refreshDelay
	global weatherConstant
	weatherConstant = weatherConstant/refreshDelay
	dataCheck = checkData()
	if dataCheck == True:
		print "dataCheck == True"
		WeatherResponse = getWeather()
		lcd.lcd_display_string(string.center(WeatherResponse,20),4)
	elif dataCheck == False:
		print "dataCheck == False"
		lcd.lcd_display_string(string.center("Weather Unavailable",20),4)
	mainClock()

#Clears a given line in arg1 when called 
def clear(arg1):
	if 'ALL' == string.upper(str(arg1)):
		lcd.lcd_display_string("                    ",1)
		lcd.lcd_display_string("                    ",2)
		lcd.lcd_display_string("                    ",3)
		lcd.lcd_display_string("                    ",4)
	else:
		lcd.lcd_display_string("                    ",arg1)

#Main clock function simply gets current time and date and displays it.
def mainClock():
	global weatherRefresh
	while True:
		currentTime = time.strftime("%I:%M %p")
		currentTime = string.center(currentTime,20)
		currentDate = time.strftime("%a %b %d")
		currentDate = string.center(currentDate,20)
		lcd.lcd_display_string(currentTime,1)
		lcd.lcd_display_string(currentDate,2)
		CurrentPlayingSong()
		time.sleep(refreshDelay)
		if weatherRefresh == weatherConstant:
			WeatherResponse = getWeather()
			lcd.lcd_display_string(string.center(WeatherResponse,20),4)
			weatherRefresh = 0
		else:
			weatherRefresh += 1 

#When called uses the PyWapi to fetch the current weather in your zip code
#and returns the value in a String format

	
def checkData():
  try:
    # see if we can resolve the host name -- tells us if there is
    # a DNS listening
    host = socket.gethostbyname(REMOTE_SERVER)
    # connect to the host -- tells us if the host is actually
    # reachable
    s = socket.create_connection((host, 80), 2)
    return True
  except:
     pass
  return False

def getWeather():
	yahoo_result = pywapi.get_weather_from_yahoo(ZipCode)	
	if yahoo_result == '':
		return 0
	else:
		print yahoo_result['condition']['text']
		weatherString = string.capitalize(yahoo_result['condition']['text']) + ", " 
		temp_Celcius = yahoo_result['condition']['temp']
		Temperature = CelciusToFahrenheit(temp_Celcius)
		weatherString = weatherString + Temperature
		print time.strftime("%I:%M:%S %a %m:%d:%Y %z") + weatherString
		return weatherString

#Does exactly what it says converts the input in celcius to Fahrenheit
def CelciusToFahrenheit(arg1):
	temp_Celcius = int(arg1)*9
	temp_Celcius = temp_Celcius/5
	temp_Celcius = temp_Celcius + 32
	temp_Fahrenheit = str(temp_Celcius)
	temp_Fahrenheit = temp_Fahrenheit + " F"
	return temp_Fahrenheit

#Reads the Currently playing song an artist name from a file that is created when Pianobar is run.
def CurrentPlayingSong():
	global ElapsedSongTime
	global SongAndArtistNamePrev
	global SongValue
	f=open(PianobarOutLocation,'r')
	FileRead = f.readlines()
	Title = FileRead[0]
	Title = Title[:-1]
	print "title1 is " + Title
	Artist = FileRead[1]
	Artist = Artist[:-1]
	f.close()
	SongAndArtistName = Title + " "+ Artist
	print "SongAndArtistName Untruncated is " + SongAndArtistName
	# if SongAndArtistName != SongAndArtistNamePrev:
	print "Song And Artist is " + SongAndArtistName
	ElapsedSongTime+=1
	print ElapsedSongTime
	SongAndArtistNamePrev = SongAndArtistName
	SplitTextValue = SplitText(SongAndArtistName)
	if SplitTextValue == True:

		if SongValue == 0:
			clear(3)
			Title = TrimLength(Title)
			lcd.lcd_display_string(string.center(Title,20),3)
			print "title2 is " + Title
			SongValue = 1
			print "SongValue is " + str(SongValue)
		elif SongValue == 1:
			clear(3)
			Artist = TrimLength(Artist)
			lcd.lcd_display_string(string.center(Artist,20),3)
			print "Artist is " + Artist
			SongValue = 0
			print "SongValue is " + str(SongValue)
	else:
		print SongAndArtistName
		lcd.lcd_display_string(string.center(SongAndArtistName,20),3)
	# elif SongTimeout <= ElapsedSongTime:
	# 	ElapsedSongTime = 0
	# 	clear(3)
	# 	lcd.lcd_display_string(string.center("Not Playing",20),3)
	ElapsedSongTime = ElapsedSongTime + 1

#Takes the Artist name and song from CurrentPlayingSong and truncates it if the lenght is over 20 characters long
def SplitText(songName):
	if len(songName) > 20:
		print "SplitText returned True"
		return True
	elif len(songName) == 20 or len(songName) < 20:
		print "SplitText returned False"
		return False
def TrimLength(name):
	if len(name) > 20:
		name = name[0:19]
		return name
	else:
		return name

# def AlarmState():
# 	AlarmFile = open('/home/pi/projects/piclock/alarmState')
# 	Lines = AlarmFile.readlines()
# 	print Lines[0]
# 	print Lines[1]
# AlarmState()
try:
	Initialize()
except (KeyboardInterrupt, SystemExit):
	print "Script Stopped"
	clear("all")
	lcd.lcd_display_string(string.center("Script Stopped",20),2)
	time.sleep(2)
	clear(2)
	lcd.lcd_display_string(string.center("Good Bye ;)",20),2)
	sys.exit("Good Bye")