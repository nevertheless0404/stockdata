import streamlit as st
import FinanceDataReader as fdr 
import mplfinance as mpf
import json
import matplotlib.pyplot as plt
from streamlit_lottie import st_lottie
from datetime import datetime, timedelta

def loadJSON(path):
    f = open(path, 'r')
    res = json.load(f)
    f.close()
    return res

col1, col2 = st.columns([1, 2])
with col1:
    lottie = loadJSON('lottie-stock-candle-loading.json')
    st_lottie(lottie, speed=1, loop=True, width=150, height=150)

with col2:
    ''
    ''
    st.title('주식 정보 시각화')

@st.cache_data
def getData(code, datestart, dateend):
    df = fdr.DataReader(code, datestart, dateend).drop(columns='Change')
    return df

@st.cache_data
def getStmbols(market='KOSPI', sort='Marcap'):
    df = fdr.StockListing(market)
    ascending = False if sort == 'Marcap' else True
    df.sort_values(by=[sort], ascending = ascending, inplace=True)
    return df [ ['Code', 'Name', 'Market'] ]

if 'ndays' not in st.session_state:
    st.session_state['ndays'] = 30

if 'code_index' not in st.session_state:
    st.session_state['code_index'] = 0

if 'chart_style' not in st.session_state:
    st.session_state['chart_style'] = 'default'

if 'volume' not in st.session_state:
    st.session_state['volume'] = True

with st.sidebar.form(key="chartsetting", clear_on_submit=True):
    st.header('차트 설정')
    ''
    ''
    symbols = getStmbols()
    choices = zip(symbols.Code, symbols.Name, symbols.Market)
    choices = [ ' : '.join(x) for x in choices ]
    choice = st.selectbox(label='종목', options = choices, index=st.session_state['code_index'])
    code_index = choices.index(choice)
    code = choice.split()[0]
    ''
    ''
    ndays = st.slider(
        label='기간 (days):',
        min_value= 5,
        max_value= 365,
        value=st.session_state['ndays'],
        step=1
    )
    ''
    ''
    chart_styles = ['default', 'binance', 'blueskies', 'brasil', 'charles', 'checkers', 'classic', 'yahoo', 'mike', 'nightclouds', 'sas', 'starsandstripes']
    chart_style = st.selectbox(label='차트 스타일:', options=chart_styles, index=chart_styles.index(st.session_state['chart_style']))
    ''
    ''
    volume = st.checkbox('거래량', value=st.session_state['volume'])

    if st.form_submit_button(label="OK"):
        st.session_state['ndays'] = ndays
        st.session_state['code_index'] = code_index
        st.session_state['chart_style'] = chart_style
        st.session_state['volume'] = volume
        st.rerun()

def plotChart(data):

    chart_style = st.session_state['chart_style'] 
    marketcolors = mpf.make_marketcolors(up='red', down='blue')
    mpf_style = mpf.make_mpf_style(base_mpf_style=chart_style, marketcolors=marketcolors)

    fig, ax = mpf.plot(
        data=data,
        volume= st.session_state['volume'], 
        type='candle',
        style=mpf_style,
        figsize=(10,7),
        fontscale=1.1,
        mav=(5,10,30),
        mavcolors=('red', 'green', 'blue'),
        returnfig=True
    )

    st.pyplot(fig)


code = '005930'
# date_end = datetime.today().date()
date_start = (datetime.today() - timedelta(days=st.session_state['ndays'])).date()
df = getData(code, date_start, datetime.today().date())
chart_title = choices[st.session_state['code_index']]
st.markdown(f'<h3 style="text-align: center; color: red;">{chart_title}</h3>', unsafe_allow_html=True)

plotChart(df)

st.write('##### 이동평균선: :red[5일], :green[10일], :blue[30일].')
