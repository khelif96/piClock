#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################################################
######					PIClock			    	######
######				By Mohamed Khelif			######
######################################################
#Import necessary libraries
import lcddriver
import pywapi
import socket
import string
import sys
import time
from time import gmtime,strftime

#Config Variables
global timeSinceRefresh
ZipCode = '11209' #ZipCode for weather
PianobarOutLocation = '/home/pi/projects/piclock/out' #Location of the file Pianobar is writing the song name and artist output strings
hourFormat12H = True #Change this if you want the time to be displayed in 12h format or 24h format
	#True for 12h format or False for 24h format
CelciusUnit = False #Variable for weather unit; True for Celcius, False for Fahrenheit,
weatherRefreshInterval = 3600 #Interval to check the weather in Seconds, 3600 is 1 hour

#Initialize import items
lcd = lcddriver.lcd() # Set Up LCD Display
REMOTE_SERVER = "www.google.com" #Url to check if data connection is available

timeDelay = 4 #Refreshes clock every 4 Seconds


refreshInterval = 4

weatherRefreshInterval = weatherRefreshInterval/refreshInterval


timeSinceRefresh = 3500

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
	lcd.lcd_display_string(string.center("Pi Clock",20),2)
	lcd.lcd_display_string(string.center("Starting...",20),3)


	dataCheck = checkData()
	if dataCheck == True:
		print "dataCheck == True"
		WeatherResponse = getWeather()
		lcd.lcd_display_string(string.center(WeatherResponse,20),4)
	elif dataCheck == False:
		print "dataCheck == False"
		lcd.lcd_display_string(string.center("Weather Unavailable",20),4)

	mainClock()


def clear(arg1): #Clears a given line in arg1 when called takes integers 1-4 representing corresponding line numbers
	if 'ALL' == string.upper(str(arg1)):
		lcd.lcd_display_string("                    ",1)
		lcd.lcd_display_string("                    ",2)
		lcd.lcd_display_string("                    ",3)
		lcd.lcd_display_string("                    ",4)
	else:
		lcd.lcd_display_string("                    ",arg1)


#Main clock function simply gets current time and date and displays it.
def mainClock():
	# global weatherRefreshInterval
	global timeSinceRefresh
	while True:
		if hourFormat12H == True:
			lcd.lcd_display_string(string.center(time.strftime("%I:%M %p"),20),1) #Outputs time in 12H Minutes AM or PM Format
		elif hourFormat12H == False:
			lcd.lcd_display_string(string.center(time.strftime("%H:%M"),20),1) #Outputs time in 24H Minutes Format

		lcd.lcd_display_string(string.center(time.strftime("%a %b %d"),20),2)  #Outputs the date in DayName MonthName DayNumber

		CurrentPlayingSong()

		time.sleep(refreshInterval)
		if weatherRefreshInterval == timeSinceRefresh:
			# WeatherResponse = getWeather()
			lcd.lcd_display_string(string.center(getWeather(),20),4)
			timeSinceRefresh = 0
		else:
			timeSinceRefresh += 1

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
	yahoo_result = pywapi.get_weather_from_yahoo(ZipCode) #Uses pywapi to fetch the weather from the Yahoo weather api (Found this to be the least spotty service)
	if yahoo_result == '':
		#DoNothing just leave the previous weather
		print "Weather Returned Nothing"
	else:
		print yahoo_result['condition']['text']
		weatherString = string.capitalize(yahoo_result['condition']['text']) + ", "
		temp_Celcius = yahoo_result['condition']['temp']

		if CelciusUnit == False:
			weatherString = weatherString + CelciusToFahrenheit(temp_Celcius)
		elif CelciusUnit == True:
			weatherString = weatherString + temp_Celcius

		print time.strftime("%H:%M:%S %a %m:%d:%Y %z") + weatherString
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
	global SongValue

	f=open(PianobarOutLocation,'r')
	FileRead = f.readlines()
	f.close()

	# Seperates the Song name and Artists name and stores them into variables
	# Titled Title for Song Name and Artist for Artist name
	Title = FileRead[0]
	Title = Title[:-1]
	Artist = FileRead[1]
	Artist = Artist[:-1]

	SongAndArtistName = Title + " "+ Artist
	# print "SongAndArtistName Untruncated is " + SongAndArtistName
	# if SongAndArtistName != SongAndArtistNamePrev:
	# print "Song And Artist is " + SongAndArtistName

	# SplitTextValue = SplitText(SongAndArtistName)
	if SplitText(SongAndArtistName): #If function split text returns True
		if SongValue == 0:
			clear(3)
			Title = TrimLength(Title)
			lcd.lcd_display_string(string.center(Title,20),3)
			# print "title2 is " + Title
			SongValue = 1
			# print "SongValue is " + str(SongValue)
		elif SongValue == 1:
			clear(3)
			Artist = TrimLength(Artist)
			lcd.lcd_display_string(string.center(Artist,20),3)
			# print "Artist is " + Artist
			SongValue = 0
			# print "SongValue is " + str(SongValue)
	else:
		print SongAndArtistName
		lcd.lcd_display_string(string.center(SongAndArtistName,20),3)
	# elif SongTimeout <= ElapsedSongTime:
	# 	ElapsedSongTime = 0
	# 	clear(3)
	# 	lcd.lcd_display_string(string.center("Not Playing",20),3)
	# ElapsedSongTime = ElapsedSongTime + 1

#Takes the Artist name and song from CurrentPlayingSong and truncates it if the lenght is over 20 characters long
def SplitText(songName):
	if len(songName) > 20:
		# print "SplitText returned True"
		return True
	elif len(songName) == 20 or len(songName) < 20:
		# print "SplitText returned False"
		return False

#Trims the input variables length to below 20 Characters
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
