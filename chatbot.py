"""
This file is adapted from an nlp application using the nltk library.

https://www.nltk.org/_modules/nltk/chat/util.html#Chat.respond
"""

import re
import random
import pandas as pd
import nltk
from nltk.chat.util import Chat, reflections 
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

# the sheet contains dresses information on amazon
df = pd.read_csv('Amazon dresses - Sheet1.csv')
df = df.drop_duplicates(subset=['name'])
s = Service('driver/chromedriver')

driver = webdriver.Chrome(service=s)

# a method get rid of all punctuation in a string and change to lowercase
def preprocess(response):
    preprocess_response = response
    preprocess_response = preprocess_response.lower()
    preprocess_response = re.sub(r'\n|[^a-zA-Z]', ' ', preprocess_response)
    #preprocess_response = preprocess_response.split()
    return preprocess_response

df['name'] = df['name'].apply(lambda x: preprocess(x))
df = df.sort_values(by='rating', ascending=False)


class MyChat(Chat):
    rec_count = 0

    def __init__(self, pairs, reflections):

        # add `z` because now items in pairs have three elements
        self._pairs = [(re.compile(x, re.IGNORECASE), y, z) for (x, y, z) in pairs]
        self._reflections = reflections
        self._regex = self._compile_reflections()

    def respond(self, str):

        # add `callback` because now items in pairs have three elements
        for (pattern, response, callback) in self._pairs:
            match = pattern.match(str)

            if match:

                resp = random.choice(response)
                resp = self._wildcards(resp, match)

                if resp[-2:] == '?.':
                    resp = resp[:-2] + '.'
                if resp[-2:] == '??':
                    resp = resp[:-2] + '?'

                # run `callback` if exists  
                if callback: # eventually: if callable(callback):
                    callback(match)

                return resp

# a method that split response
def split_words(sentence):
    sentence = sentence.replace("and", ",")
    words = sentence.split(", ")
    for i in range(len(words)):
        words[i] = words[i].strip().replace("-", " ")
    try:
        words.remove("")
    except:
        words = words
    try:
        words.remove(" ")
    except:
        words = words
    
    return words


def recommendation(match):
    if MyChat.rec_count > 0:
        driver.execute_script("window.open('about:blank', 'new_tab');")
        driver.switch_to.window("new_tab")
    MyChat.rec_count += 1

    request = split_words(match.groups()[-1])
    
    if len(request) == 0:
        print("Can you be more specific?")
        return
    
    new_df = df
    df_list = []
    for i in request:
        print(i)
        if not len(df_list) == 0:
            lst = [False if (re.search(r'\b' + i + r'\b', df_list[-1].get('name').iloc[x]) == None) else True for x in range(df_list[-1].shape[0])]
            if sum(lst) == 0:
                print("Sorry I cannot find a dress that fulfills all your requirements, but you may love these dresses!")
                length = df_list[-1].shape[0]
                if length <= 3:
                    lnks = df_list[-1].get('url')
                    url = lnks.iloc[0]
                    driver.get(url)
                    driver.execute_script("window.open('about:blank', '0tab');") # learn from https://www.geeksforgeeks.org/python-opening-multiple-tabs-using-selenium/
                    driver.switch_to.window("0tab")
                    for j in range(1,length):
                    	time.sleep(j) 
                    	url = lnks.iloc[j]
                    	driver.get(url)
                    	if j < length-1:
	                    	string = "window.open(\'about:blank\', \'"+ str(j)+"tab"+"\')"
	                    	driver.execute_script(string)
	                    	driver.switch_to.window(str(j)+"tab")

                else:
                	lnks = df_list[-1].get('url')
                	url = lnks.iloc[0]
                	driver.get(url)
                	driver.execute_script("window.open('about:blank', '0tab');")
                	driver.switch_to.window("0tab")
                	for j in range(1,3):
                		time.sleep(j)
                		url = lnks.iloc[j]
                		driver.get(url)
                		if j < 2:
	                		string = "window.open(\'about:blank\', \'"+ str(j)+"tab"+"\')"
	                		driver.execute_script(string)
	                		driver.switch_to.window(str(j)+"tab")
                return
            df_list.append(df_list[-1][lst])
        else:
            lst = [False if (re.search(r'\b' + i + r'\b', new_df.get('name').iloc[x]) == None) else True for x in range(new_df.shape[0])]
            if sum(lst) == 0:
                print("Sorry we cannot find your best fit...can you be general?")
                return
            df_list.append(new_df[lst])

    
    length = df_list[-1].shape[0]
    if length <= 3:
    	lnks = df_list[-1].get('url')
    	url = lnks.iloc[0]
    	driver.get(url)
    	driver.execute_script("window.open('about:blank', '0tab');")
    	driver.switch_to.window("0tab")
    	for j in range(1,length):
    		time.sleep(j) 
    		url = lnks.iloc[j]
    		driver.get(url)
    		if j < length-1:
	    		string = "window.open(\'about:blank\', \'"+ str(j)+"tab"+"\')"
	    		driver.execute_script(string)
	    		driver.switch_to.window(str(j)+"tab")
    else:
    	lnks = df_list[-1].get('url')
    	url = lnks.iloc[0]
    	driver.get(url)
    	driver.execute_script("window.open('about:blank', '0tab');")
    	driver.switch_to.window("0tab")
    	for j in range(1,3):
    		time.sleep(j) 
    		url = lnks.iloc[j]
    		driver.get(url)
    		if j < 2:
	    		string = "window.open(\'about:blank\', \'"+ str(j)+"tab"+"\')"
	    		driver.execute_script(string)
	    		driver.switch_to.window(str(j)+"tab")

    # print(df_list[-1])
    return

pairs = [
    [
        r"Hi im (.*)",
        ["hello %1, What can I do for you?"],
        None
    ],
    [
        r"quit",
        ["Okey, see you next time!", "Have a nice day!"],
        None
    ],
    [
        r"(.*) a (.*) dress", 
        ["Hope this is helpful! If you wanna leave, please type \'quit\'"],
        recommendation
    ],
    [
        r"see you",
        ["Okey, see you next time!", "Have a nice day!"],
        None
    ]
]

# --- every question needs `callback` or `None`---

print("Greetings! My name is Chatbot, What is yours?.")
Chatbot = MyChat(pairs, reflections)
Chatbot.converse()

