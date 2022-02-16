import streamlit as st
import pandas as pd
import nltk
import plotly.express as px
nltk.download('stopwords')
from nltk.corpus import stopwords
st.title("Search Console Query Analyzer")
st.markdown("Use this application to get more insights out of your search console data")

search_console_file = st.file_uploader("Upload your search console query export")

if(search_console_file is not None):
	consoledf = pd.read_csv(search_console_file)

    #analysistype = st.selectbox('Which kind of analysis would you like?',['N-gram','Machine learning CTR','Potential #1 Clicks','Group by search intent'])
	stopwords_language=st.selectbox('Main language',["english","dutch","french","german"])
	#branded=st.text_input('Enter brand name')
	numberwords = st.number_input('Number of words', min_value=1, max_value=50, value=25, step=1)
	if(st.button('Run 1-gram analysis')):
		analysis=1
		stopwords = stopwords.words(stopwords_language)

		words=[]
		for index,row in consoledf.iterrows():
			new_words = row["Top queries"].split(" ")
			for word in new_words:
				if(word not in stopwords and word not in words):
					words.append([word,row["Clicks"],row["Impressions"],row['Top queries']])
		statsdf = pd.DataFrame(words,columns=["1-Gram","Clicks","Impressions","Word"])   
		clicksdf = statsdf.sort_values(by=['Clicks'],ascending=False)
		groupdf = clicksdf.groupby('1-Gram').sum().sort_values(by=['Impressions'],ascending=False)
		groupdf["CTR"]=groupdf.apply(lambda x:round(x["Clicks"]*100/x["Impressions"],2),axis=1)
		groupdf = groupdf.head(numberwords)
		groupdf["1-Gram"]=groupdf.index
		fig = px.bar(groupdf, x="1-Gram", y="Impressions", color='CTR', barmode='group', title="1-Gram Analysis Impressions",text_auto=True)
		#fig.show()
		st.plotly_chart(fig, use_container_width=True)
		st.write("performing 1-gram analysis")
else:
	st.write("Upload your file!")



