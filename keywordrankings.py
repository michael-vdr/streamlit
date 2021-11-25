import streamlit as st
import pandas as pd
import random
st.header("Find the rankings of a list of keywords and compare with best page of direct competitor")
st.sidebar.header("Settings")
input_keywords=st.sidebar.text_area(label="Keywords one by line")
input_competitors=st.sidebar.text_area(label="Competitor domains one by line e.g competitor.com")

website=st.sidebar.text_input(label="Website e.g. website.com")
se_name=st.sidebar.text_input(label='Search Engine: e.g. google.com')
se_language=st.sidebar.text_input(label='Language e.g. English')
loc_name_canonical=st.sidebar.text_input(label='Country e.g. Belgium')
dataforseouser = st.sidebar.text_input(label="DataForSEO.com username")
dataforseopass = st.sidebar.text_input(label="DataForSEO.com API password")
input_keywords = input_keywords.split('\n')
input_competitors = input_competitors.split('\n')
keywords=[]
errors=[]
if len(input_keywords[0])>0 and len(input_competitors[0])>0 and len(website)>0 and len(se_name)>0 and len(se_language)>0 and len(loc_name_canonical)>0 and len(dataforseouser)>0 and len(dataforseopass)>0:
     for keyword in input_keywords:
           keywords.append(keyword)
     keywordlist=list(set(keywords))
     competitors=list(set(input_competitors))


     keywordsdf=pd.DataFrame(keywordlist,columns=["Keyword"])
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
     keywords_and_site_df = pd.merge(keywordsdf,sitedf,how="left",on="Keyword")
     keywords_and_comp_df = keywords_and_site_df.copy()
     #posities eigen website en competitor 
     competitors2=[]
     for competitor in competitors:
          competitor="."+competitor
          competitors2.append(competitor)
     columns=["Keyword","Search Engine","Language","Result types","Position","Absolute Rank","Domein","Page Title","Description","Page"]
     sitedf.columns=columns
     i=1
     for competitor2 in competitors:
          if(competitor2!=""):
          #competitor="www.brusselsairport.be"
               compdf = resultdf[resultdf["Domain"].str.contains(competitor2, na=False, regex=True)][["Keyword","Group Rank","URL"]]

               compdf.columns=["Keyword","C"+str(i)+" Position","C"+str(i)+"Page"]
               keywords_and_comp_df = pd.merge(keywords_and_comp_df,compdf,how="left",on="Keyword")
          i=i+1
     keyworddf = keywords_and_comp_df.copy()
     def get_rank(position,competitorpositions):
          rank = 1
          for competitorposition in competitorpositions:
               if(position>=competitorposition):
                    rank=rank+1
               if(competitorposition==0 and position<101):
                    rank=rank-1
          return rank

     if(len(competitors)==1):
          keyworddf["competitive rank"]=keyworddf.apply(lambda x:get_rank(x["Group Rank"],[x["C1 Position_y"]]),axis=1)
     if(len(competitors)==2):
          keyworddf["competitive rank"]=keyworddf.apply(lambda x:get_rank(x["Group Rank"],[x["C1 Position"],x["C2 Position"]]),axis=1)
     if(len(competitors)==3):
          keyworddf["competitive rank"]=keyworddf.apply(lambda x:get_rank(x["Group Rank"],[x["C1 Position"],x["C2 Position"],x["C3 Position"]]),axis=1)
     if(len(competitors)==4):
          keyworddf["competitive rank"]=keyworddf.apply(lambda x:get_rank(x["Group Rank"],[x["C1 Position"],x["C2 Position"],x["C3 Position"],x["C4 Position"]]),axis=1)
     if(len(competitors)==5):
          keyworddf["competitive rank"]=keyworddf.apply(lambda x:get_rank(x["Group Rank"],[x["C1 Position"],x["C2 Position"],x["C3 Position"],x["C4 Position"],x["C5 Position"]]),axis=1)
     if(len(competitors)==6):
          keyworddf["competitive rank"]=keyworddf.apply(lambda x:get_rank(x["Group Rank"],[x["C1 Position"],x["C2 Position"],x["C3 Position"],x["C4 Position"],x["C5 Position"],x["C6 Position"]]),axis=1)
     if(len(competitors)==7):
          keyworddf["competitive rank"]=keyworddf.apply(lambda x:get_rank(x["Group Rank"],[x["C1 Position"],x["C2 Position"],x["C3 Position"],x["C4 Position"],x["C5 Position"],x["C6 Position"],x["C7 Position"]]),axis=1)
     if(len(competitors)==12):
          keyworddf["competitive rank"]=keyworddf.apply(lambda x:get_rank(x["Group Rank"],[x["C1 Position"],x["C2 Position"],x["C3 Position"],x["C4 Position"],x["C5 Position"],x["C6 Position"],x["C7 Position"],x["C8 Position"],x["C9 Position"],x["C10 Position"],x["C11 Position"],x["C12 Position"]]),axis=1)

     def get_best_competitor(competitorurls,competitorpositions):
          minposition=101
          for competitorposition in competitorpositions:
               if(competitorposition>0 and competitorposition<minposition):
                    minposition=competitorposition
          i=0
          for competitorposition in competitorpositions:
               if(minposition==101):
                    besturl=""
               else:
                    if(minposition==competitorposition):
                         besturl = competitorurls[i]
               i=i+1
          return [minposition,besturl]

     if(len(competitors)==1):
          keyworddf["best competitor"]=keyworddf.apply(lambda x:get_best_competitor(x["C1Page"],[x["C1 Position"]])[0],axis=1)
          keyworddf["url competitor"]=keyworddf.apply(lambda x:get_best_competitor(x["C1Page"],[x["C1 Position"]])[1],axis=1)
     if(len(competitors)==2):
          keyworddf["best competitor"]=keyworddf.apply(lambda x:get_best_competitor([x["C1Page"],x["C2Page"]],[x["C1 Position"],x["C2 Position"]])[0],axis=1)
          keyworddf["url competitor"]=keyworddf.apply(lambda x:get_best_competitor([x["C1Page"],x["C2Page"]],[x["C1 Position"],x["C2 Position"]])[1],axis=1)
     if(len(competitors)==3):
          keyworddf["best competitor"]=keyworddf.apply(lambda x:get_best_competitor([x["C1Page"],x["C2Page"],x["C3Page"]],[x["C1 Position"],x["C2 Position"],x["C3 Position"]])[0],axis=1)
          keyworddf["url competitor"]=keyworddf.apply(lambda x:get_best_competitor([x["C1Page"],x["C2Page"],x["C3Page"]],[x["C1 Position"],x["C2 Position"],x["C3 Position"]])[1],axis=1)
     if(len(competitors)==4):
          keyworddf["best competitor"]=keyworddf.apply(lambda x:get_best_competitor([x["C1Page"],x["C2Page"],x["C3Page"],x["C4Page"]],[x["C1 Position"],x["C2 Position"],x["C3 Position"],x["C4 Position"]])[0],axis=1)
          keyworddf["url competitor"]=keyworddf.apply(lambda x:get_best_competitor([x["C1Page"],x["C2Page"],x["C3Page"],x["C4Page"]],[x["C1 Position"],x["C2 Position"],x["C3 Position"],x["C4 Position"]])[1],axis=1)
     if(len(competitors)==5):
          keyworddf["best competitor"]=keyworddf.apply(lambda x:get_best_competitor([x["C1Page"],x["C2Page"],x["C3Page"],x["C4Page"],x["C5Page"]],[x["C1 Position"],x["C2 Position"],x["C3 Position"],x["C4 Position"],x["C5 Position"]])[0],axis=1)
          keyworddf["url competitor"]=keyworddf.apply(lambda x:get_best_competitor([x["C1Page"],x["C2Page"],x["C3Page"],x["C4Page"],x["C5Page"]],[x["C1 Position"],x["C2 Position"],x["C3 Position"],x["C4 Position"],x["C5 Position"]])[1],axis=1)
     if(len(competitors)==6):
          keyworddf["best competitor"]=keyworddf.apply(lambda x:get_best_competitor([x["C1Page"],x["C2Page"],x["C3Page"],x["C4Page"],x["C5Page"],x["C6Page"]],[x["C1 Position"],x["C2 Position"],x["C3 Position"],x["C4 Position"],x["C5 Position"],x["C6 Position"]])[0],axis=1)
          keyworddf["url competitor"]=keyworddf.apply(lambda x:get_best_competitor([x["C1Page"],x["C2Page"],x["C3Page"],x["C4Page"],x["C5Page"],x["C6Page"]],[x["C1 Position"],x["C2 Position"],x["C3 Position"],x["C4 Position"],x["C5 Position"],x["C6 Position"]])[1],axis=1)
     if(len(competitors)==7):
          keyworddf["best competitor"]=keyworddf.apply(lambda x:get_best_competitor([x["C1Page"],x["C2Page"],x["C3Page"],x["C4Page"],x["C5Page"],x["C6Page"],x["C7Page"]],[x["C1 Position"],x["C2 Position"],x["C3 Position"],x["C4 Position"],x["C5 Position"],x["C6 Position"],x["C7 Position"]])[0],axis=1)
          keyworddf["url competitor"]=keyworddf.apply(lambda x:get_best_competitor([x["C1Page"],x["C2Page"],x["C3Page"],x["C4Page"],x["C5Page"],x["C6Page"],x["C7Page"]],[x["C1 Position"],x["C2 Position"],x["C3 Position"],x["C4 Position"],x["C5 Position"],x["C6 Position"],x["C7 Position"]])[1],axis=1)
     def get_best_result(keyword):
          try:
               return resultdf[(resultdf["Keyword"]==keyword) & (resultdf["Group Rank"]==1)]["URL"].values.tolist()[0]
          except:
               return ""
     keyworddf["best page"]=keyworddf.apply(lambda x:get_best_result(x["Keyword"]),axis=1)
     keyworddf= keyworddf.drop_duplicates(subset=['Keyword'], keep='first', inplace=False)
     keyworddf.to_csv('keyworddata.csv')
     import base64

     def download_link(object_to_download, download_filename, download_link_text):
          if isinstance(object_to_download,pd.DataFrame):
               object_to_download = object_to_download.to_csv(index=False)

          # some strings <-> bytes conversions necessary here
          b64 = base64.b64encode(object_to_download.encode()).decode()

          return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


     tmp_download_link = download_link(sitedf, 'keyworddata.csv', 'Click here to download your data!')
     st.markdown(tmp_download_link, unsafe_allow_html=True)
     #st.table(keyworddf)
     st.table(keyworddf[["Keyword","Group Rank","URL","best competitor","url competitor"]])
     #for index,row in sitedf.iterrows():
          #st.write(row[0],row[4],row[9])
