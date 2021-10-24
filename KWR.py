#!/usr/bin/env python
# coding: utf-8

# #**Make a Keyword Research in 5 minutes using Google Suggest**
# 
# ---
# 

# This Keyword Script will quickly generate keyword ideas from Google Suggest and cluster them using the most common words

# ## Step 1: Change Settings

# Fill in the field lang_code with your language code (e.g. en, fr, es, nl) and enter up to 5 seed keywords you want to use.
# 
# 

# In[1]:

import streamlit as st
import pandas as pd
import random
import requests
import json
import time
import string
import nltk
nltk.download('punkt')
from stop_words import get_stop_words
from collections import Counter
from json import loads
from polyfuzz import PolyFuzz
from polyfuzz.models import RapidFuzz
st.header("Keyword research")
input_keywords=st.sidebar.text_area(label="enter keywords one by line")
lang_code=st.sidebar.text_input(label='Language code e.g. en')
input_keywords = input_keywords.split('\n')
keywords=[]
errors=[]
if len(input_keywords[0])>0 and len(lang_code)>0:
     for keyword in input_keywords:
           keywords.append(keyword)
     keywordlist=list(set(keywords))
     letterlist=[""]
     letterlist=letterlist+list(string.ascii_lowercase)
#Google Suggest for each combination of keyword and letter
     keywordsuggestions=[]
     for keyword in keywordlist: 
          for letter in letterlist :
              URL="http://suggestqueries.google.com/complete/search?client=firefox&hl="+str(lang_code)+"&q="+keyword+" "+letter
              headers = {'User-agent':'Mozilla/5.0'}
              time.sleep(1)
              st.write(URL) 
              response = requests.get(URL, headers=headers) 
              
              result = json.loads(response.content.decode('utf-8'))
              keywordsuggest=[keyword,letter] 
              for word in result[1]:
                  if(word!=keyword):
                      keywordsuggest.append(word)
                      time.sleep(1)
                  keywordsuggestions.append(keywordsuggest)
              #crearte a dataframe from this list
          keywordsuggestions_df = pd.DataFrame(keywordsuggestions)

          columnnames=["Keyword","Letter"]
          for i in range(1,len(keywordsuggestions_df.columns)-1):
              columnnames.append("Suggestion"+str(i))
          keywordsuggestions_df.columns=columnnames

          allkeywords = keywordlist
          for i in range(1,len(keywordsuggestions_df.columns)-1):
              suggestlist = keywordsuggestions_df["Suggestion"+str(i)].values.tolist()
              for suggestion in suggestlist:
                  allkeywords.append(suggestion)

          stop_words=get_stop_words(lang_code)
          wordlist=[]
          seed_words=[]
     for keyword in keywords:
          for seed_word in nltk.word_tokenize(str(keyword).lower()):
              if(len(seed_word)>0):
                    seed_words.append(seed_word)
     for keyword in allkeywords:
          words = nltk.word_tokenize(str(keyword).lower()) 
          for word in words:
              if(word not in stop_words and word not in seed_words and len(word)>1):
                  wordlist.append(word)

     rapidfuzz_matcher = RapidFuzz(n_jobs=1)
     model = PolyFuzz(rapidfuzz_matcher).match(from_list, to_list)
     model.get_matches()

     most_common_words= [word for word, word_count in Counter(wordlist).most_common(100)]
     rapidfuzz_matcher = RapidFuzz(n_jobs=1)
     model = PolyFuzz(rapidfuzz_matcher).match(list(set(keywordlist)), most_common_words)
     model.get_matches()
     keywordsdf = model.get_matches()
     #print keywordsdf
     st.dataframe(keywordsdf)  


# In[11]:




