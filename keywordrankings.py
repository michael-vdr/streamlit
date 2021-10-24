import streamlit as st
import pandas as pd
import random
st.header("Find the rankings of a list of keywords")
st.sidebar.header("Settings")
input_keywords=st.sidebar.text_area(label="enter keywords one by line")
website=st.sidebar.text_input(label="Website e.g. website.com")
se_name=st.sidebar.text_input(label='Search Engine: e.g. google.com')
se_language=st.sidebar.text_input(label='Language e.g. English')
loc_name_canonical=st.sidebar.text_input(label='Country e.g. Belgium')
dataforseouser = st.sidebar.text_input(label="DataForSEO.com username")
dataforseopass = st.sidebar.text_input(label="DataForSEO.com API password")
input_keywords = input_keywords.split('\n')
keywords=[]
errors=[]
if len(input_keywords[0])>0 and len(website)>0 and len(se_name)>0 and len(se_language)>0 and len(loc_name_canonical)>0 and len(dataforseouser)>0 and len(dataforseopass)>0:
     for keyword in input_keywords:
           keywords.append(keyword)
     keywordlist=list(set(keywords))
     #keywords naar json formaat omzetten
     import random
     def getpositionandurl(keywordlist,se_name,se_language,loc_name_canonical):
           post_data = dict()
           for keyword in keywordlist:
          #keyword[0]=keyword[0].decode(encoding = 'UTF-8',errors = 'strict')
          #print(str(keyword[0]))
          #random.randint(1, 30000000)
                 if isinstance(keyword, dict):
                       keyword = keyword.decode_dict(keyword)
                 try:    
                       if(str(keyword).replace(' ','').isalnum()):
                             post_data[len(post_data)] = dict(
                             language_name=se_language,
                             location_name=loc_name_canonical,
                             keyword=str(keyword)
                       )
                 except:
                       print("")
           return post_data
     post_data_test = getpositionandurl(keywordlist,se_name,se_language,loc_name_canonical)

     #DataforSEO API inladen
     from http.client import HTTPSConnection
     from base64 import b64encode
     from json import loads
     from json import dumps

     class RestClient:
          domain = "api.dataforseo.com"

          def __init__(self, username, password):
                self.username = username
                self.password = password

          def request(self, path, method, data=None):
                connection = HTTPSConnection(self.domain)
                try:
                     base64_bytes = b64encode(
                          ("%s:%s" % (self.username, self.password)).encode("ascii")
                          ).decode("ascii")
                     headers = {'Authorization' : 'Basic %s' %  base64_bytes, 'Content-Encoding' : 'gzip'}
                     connection.request(method, path, headers=headers, body=data)
                     response = connection.getresponse()
                     return loads(response.read().decode())
                finally:
                     connection.close()

          def get(self, path):
                return self.request(path, 'GET')

          def post(self, path, data):
                if isinstance(data, str):
                     data_str = data
                else:
                     data_str = dumps(data)
                return self.request(path, 'POST', data_str)
#request uitvoeren naar dataforseo api

     client = RestClient(dataforseouser, dataforseopass)
     start = 0
     responses=[]
     tasks=[]
     while(start<len(post_data_test)):
          eind=start+1
          response = client.post("/v3/serp/google/organic/live/regular", dict(list(post_data_test.items())[start:eind]))
          # you can find the full list of the response codes here https://docs.dataforseo.com/v3/appendix/errors
          if response["status_code"] == 20000:
                responses.append(response)
          else:
                print("error. Code: %d Message: %s" % (response["status_code"], response["status_message"]))
          start=start+1

     results=[]
     for response in responses:
          if response['status_code'] == 20000:
                for task in response['tasks']:
                
                     if (task['result'] and (len(task['result']) > 0)):
                          for resultTaskInfo in task['result']:             
                                results.append(resultTaskInfo)
                     else:
                          errors.append(task)

     #dataframe uit dataforseo
     resultdatalist=[]
     i=0
     #while(i<len(post_data_test)):
     for res in results:
          #print(res)
          try:
          #print(res)
          #print(res["keyword"])
                keyword=res["keyword"]
                se_domain = res["se_domain"]
                language = res["language_code"]
                result_types = ','.join(res["item_types"])
                for item in res["items"]:
                #print(item)
                     rank_group = item["rank_group"]
                     rank_absolute = item["rank_absolute"]
                     domain = item["domain"]
                     title = item["title"]
                     description = item["description"]
                     url = item["url"]
                #print([keyword,se_domain,language,result_types,rank_group,rank_absolute,domain,title,description,url])
                     resultdatalist.append([keyword,se_domain,language,result_types,rank_group,rank_absolute,domain,title,description,url])
          except:
                print("exception")
          i=i+1
     resultdf = pd.DataFrame(resultdatalist)                
     resultdf.columns=["Keyword","Search Engine","Language","Result types","Group Rank","Absolute Rank","Domain","Title","Description","URL"]
     sitedf = resultdf[resultdf["Domain"].str.contains(website)]
     
     import base64

     def download_link(object_to_download, download_filename, download_link_text):
          if isinstance(object_to_download,pd.DataFrame):
               object_to_download = object_to_download.to_csv(index=False)

          # some strings <-> bytes conversions necessary here
          b64 = base64.b64encode(object_to_download.encode()).decode()

          return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


     tmp_download_link = download_link(sitedf, 'keyworddata.csv', 'Click here to download your data!')
     st.markdown(tmp_download_link, unsafe_allow_html=True)
     st.table(sitedf)
     #for index,row in sitedf.iterrows():
          #st.write(row[0],row[4],row[9])
