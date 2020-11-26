#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 19:10:07 2020

@author: sophie
"""
#import libraries
import datetime
import os
import pandas as pd
import re
import shelve
import time
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver

pd.set_option('display.max_rows', 10)
pd.set_option('display.max_columns', 5)
pd.set_option('display.width',800)
driver = webdriver.Chrome(executable_path="/Users/sophie/Desktop/Chromedriver_max/chromedriver 2")
scrape_link = 'https://www.tripadvisor.com/Attraction_Review-g60745-d8400863-Reviews-Quincy_Market-Boston_Massachusetts.html'
driver.get(scrape_link)

reviews_one_store = []

#find the next button
arrow = driver.find_element_by_xpath("//a[@class = 'ui_button nav next primary ']")

#if arrow is None,stop the while loop because all pages should be loaded
while arrow is not None:
    #find all the reviews in one page
    reviews = driver.find_elements_by_xpath("//div[@class = 'Dq9MAugU T870kzTX LnVzGwUB']")
    r=0

    #use for loop to go through each review in one page
    for r in range(len(reviews)):
        one_review = {}

        #find scrapping_date, url and attach them to one_review dictionary
        one_review['scrapping_date'] = datetime.datetime.now()
        one_review['google_url'] = driver.current_url
        soup = BeautifulSoup(reviews[r].get_attribute('innerHTML'))

        #extract the innerHTML and add it to dictionary
        try:
            one_review_raw = reviews[r].get_attribute('innerHTML')
        except:
            one_review_raw = ""
        one_review['review_raw'] = one_review_raw

        #extract review title
        try:
            one_review_title = soup.find('a', attrs={'class':'ocfR3SKN'}).text
        except:
            one_review_title = ""
        one_review['review_title'] = one_review_title

        #extract review text
        try:
            one_review_text = soup.find('q', attrs={'class':'IRsGHoPm'}).text
        except:
            one_review_text = ""
        one_review['review_text'] = one_review_text

        #extract customers' experience date
        try:
            one_review_experience_date = soup.find('span', attrs={'class':'_34Xs-BQm'}).text
            one_review_edate = one_review_experience_date[one_review_experience_date.find(": ")+2:]
        except:
            one_review_edate = ""
        one_review['date_of_experience'] = one_review_edate

        #see how many people find the review helpful and give a thumbs-up
        try:
            one_review_vote = soup.find('span', attrs={'class':'_3kbymg8R _2o1bmw1O'}).text
            one_review_thumbsup = one_review_vote[:one_review_vote.find(" ")]
        except:
            one_review_thumbsup = ""
        one_review['thumbs_up'] = one_review_thumbsup

        #extract the rating
        try:
            one_review_stars = re.findall('[_][0-5][0]',reviews[r].get_attribute('innerHTML'))[0]
            one_review_rating = "{} stars".format(one_review_stars[1])
        except:
            one_review_rating = ""
        one_review['rating'] = one_review_rating

        #extract reviewer name
        try:
            one_review_reviewer= soup.find('a',attrs = {'class': 'ui_header_link _1r_My98y'}).text
        except:
            one_review_reviewer = ""
        one_review['reviewer_name'] = one_review_reviewer

        #give the city that the customer is from
        try:
            one_review_from= soup.find('span',attrs = {'class': '_1TuWwpYf'}).text
            find_index = one_review_from.find(",")
            if  find_index != -1:
                one_review_city = one_review_from[find_index+2:]
            else:
                one_review_city = one_review_from
        except:
            one_review_city = ""
        one_review['reviewer_from'] = one_review_city
    
        #find how many review contributions the customer has based on the profile
        try:
            one_review_contributions= soup.findAll('span',attrs = {'class': '_1fk70GUn'})[0].text
        except:
            one_review_contributions = "0"
        one_review['reviewer_contributions'] = one_review_contributions

        #find how many votes(thumbs-up) the customer gets by providing helpful review
        try:
            one_review_helpful= soup.findAll('span',attrs = {'class': '_1fk70GUn'})[1].text
        except:
            one_review_helpful = "0"
        one_review['reviewer_helpful_vote'] = one_review_helpful

        #append the dictionary to list
        reviews_one_store.append(one_review)

    #click the arrow if it is not None, and give 2s time for loading    
    try:
        arrow.click()
        time.sleep(2)
    except:
        break

#create dataframe a, change data types of two columns, and export to csv    
a = pd.DataFrame.from_dict(reviews_one_store)
a['reviewer_contributions']=a['reviewer_contributions'].str.replace(",","").astype('int64')
a['reviewer_helpful_vote'] = a['reviewer_helpful_vote'].str.replace(",","").astype('int64')
a.to_csv("tripadvisor_quincy.csv")

    
