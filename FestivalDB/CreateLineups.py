import time
import random
import json
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By

class Festival:
    def __init__(self):
        self.festivalChar = pd.DataFrame(columns=["name","description",'url','city','state','startDate','endDate'])
        self.driver = None

    def getDriver(self):
        service = Service('LOCATION_OF_CHROMEDRIVER')
        service.start()
        self.driver = webdriver.Chrome(service=service)

    def getData(self,url):
        self.getDriver()
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        data = soup.find('div',{'id':"artist-lineup-container"})
        self.driver.quit()
        ds2 = data.find_all('div',{'class':"article lineup-item grid__item one-fifth lap-one-third palm-one-third mobile-one-whole"} )
        for entry in ds2:
            text = entry.find("script", type="application/ld+json").text
            d = json.loads(text.replace('\n',''))
            row = {"name":d['name'], "description":d['description'],'url':d['url'],\
                'city':d['location']['address']['addressLocality'],'state':d['location']['address']['addressRegion'],\
                    'startDate':d['startDate'],'endDate':d['endDate']}
            self.festivalChar = pd.concat([self.festivalChar,pd.DataFrame.from_dict(row, orient='index').transpose()], ignore_index=True)
    
    def CreateFestivalDF(self):
        for i in range(1,11):
            url = 'https://www.musicfestivalwizard.com/all-festivals/page/{}/?festival_guide=us-festivals&month&festivalgenre=electronic&festivaltype&festival_length&festival_size&camping&artist&company&sdate=July%201%2C%202022&edate=Dec%2031%2C%202023&lineup=onlylineups#038;month&festivalgenre=electronic&festivaltype&festival_length&festival_size&camping&artist&company&sdate=July+1%2C+2022&edate=Dec+31%2C+2023&lineup=onlylineups'.format(i)
            self.getData(url)

    def CreateLineupsArtist(self):
        if len(self.festivalChar) == 0:
            self.CreateFestivalDF()
        fests = list(self.festivalChar['name'])
        lineups = []
        for festname in fests:
            print(festname)
            url = str(self.festivalChar[self.festivalChar['name'] == festname]['url'].iloc[0])

            self.getDriver()
            self.driver.get(url)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            sleepTime = random.uniform(0,3)
            time.sleep(sleepTime)
            self.driver.quit()

            lst = soup.find('div',{'class':"lineupblock"}).find('div',{'class':"hublineup"}).find_all('li')
            artist = []
            for act in lst:
                artist.append(act.text)
            lineups.append(artist) 
        self.festivalChar['artists'] = pd.Series(lineups)

    def exportDF(self):
        self.CreateLineupsArtist()
        self.festivalChar.excel('FestivalDB/Festival_Characteristics.xlsx')

f = Festival()
f.exportDF()

