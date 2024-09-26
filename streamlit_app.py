import streamlit as st
import json
import requests as r
import numpy as np
import pandas as pd
import plotly.express as px

#########################
# API COVID DATA ########
#########################

apiKey = 'BT2KC0xm+UHgWAr5kw889A==UlFfvOOZFfy9BkEp'
baseUrl = 'https://api.api-ninjas.com/v1/covid19?country=Netherlands'
#GET request
response = r.get(baseUrl, headers = { 'X-Api-Key' : apiKey}) 
#Selecteer met index [-1] de laatste dictionary in de lijst, dit zijn de cijfers voor heel Nederland, zonder caribische gemeenten
data = json.loads(response.text)[-1]
#Laad de data in een panda's dataframe.
df_covid = pd.DataFrame(data) #DEZE VEREIST NOG AANPASSING

########################################################
# VERKEERSINTENSITEIT DATA LADEN EN FEATURES TOEVOEGEN #
########################################################

@st.cache_data
def load_daily_data():

    df = pd.read_csv('intensiteit_daily_average.csv')

    return df

df_daily = load_daily_data()

@st.cache_data
def load_weekly_data(year):
    df = pd.read_csv(f'intensiteit{year}_weekly.csv')
    return df

# Cache individual DataFrames
df19 = load_weekly_data(2019)
df20 = load_weekly_data(2020)
df21 = load_weekly_data(2021)
df22 = load_weekly_data(2022)
df23 = load_weekly_data(2023)
df24 = load_weekly_data(2024)

###################################
# INTRODUCTIE EN COVID PLOT #######
###################################

#COVID API
#De covid API van api-ninjas.com geeft de COVID cijfers per dag aan.
#De API is openbaar en gratis maar er is wel een Key vereist. Deze key heb ik in de code gezet zodat iedereen het kan runnen.
#Het land van interesse kan worden aangepaste door de parameter ?country=Land aan te passen. Hier hebben we hem op Netherlands gezet.
#De API response is een lijst van dictionaries, elke met een regio van het land. In dit geval betekent het aparte cijfers voor
#de caribische gemeenten van het koninkrijk. Deze zijn zodanig klein dat ze verwaarloosbaar zijn.
apiKey = 'BT2KC0xm+UHgWAr5kw889A==UlFfvOOZFfy9BkEp'
baseUrl = 'https://api.api-ninjas.com/v1/covid19?country=Netherlands'
#GET request
response = r.get(baseUrl, headers = { 'X-Api-Key' : apiKey})
#Selecteer met index [-1] de laatste dictionary in de lijst, dit zijn de cijfers voor heel Nederland, zonder caribische gemeenten
data = json.loads(response.text)[-1]
#Laadt de data in een panda's dataframe.
df_covid = pd.DataFrame(data)
 
# Splits de 'cases' kolom in twee nieuwe kolommen: 'Total Cases' en 'New Cases'
df_covid['Total Cases'] = df_covid['cases'].apply(lambda x: x['total'])
df_covid['New Cases'] = df_covid['cases'].apply(lambda x: x['new'])
 
# Verwijder de oorspronkelijke 'cases' kolom als je die niet meer nodig hebt
df_covid = df_covid.drop(columns=['cases'])
# verwijder de kolom 'region'
df_covid = df_covid.drop(columns=["region"])
# Zet de index (datums) om in een aparte kolom genaamd 'Date'
df_covid = df_covid.reset_index()
# Zet de index om in een aparte kolom genaamd 'Date'
df_covid = df_covid.rename(columns={'index': 'Date'})
 
#Histogram van nieuwe COVID gevallen per week
# Zorg ervoor dat de 'Date' kolom in datetime-formaat staat
df_covid['Date'] = pd.to_datetime(df_covid['Date'])
 
# Groepeer de data per week en sommeer de nieuwe gevallen per week
df_weekly_new = df_covid.resample('W', on='Date').sum().reset_index()
 
# Maak een histogram van de nieuwe gevallen per week
fig_hist = px.bar(df_weekly_new, x='Date', y='New Cases',
                  title='COVID-19 gevallen per week in Nederland 2020-2023',
                  labels={'New Cases': 'Nieuwe Gevallen', 'Date': 'Datum'},
                  template='plotly_dark', color_discrete_sequence=['#F23E2E'])
 
fig_hist.update_layout(
    title={
        'text': "COVID-19 gevallen per week in Nederland 2020-2023",
        'x': 0.5, 
        'xanchor': 'center',  
        'yanchor': 'top'  
    }
)
st.title('''Verkeers intensiteit voor, na en tijdens Corona''')

if st.checkbox('Toon regressielijn'):
    fig_hist.add_trace(px.line(df_weekly_new, x='Date', y='New Cases', color_discrete_sequence=['blue']).data[0])
 
if st.checkbox('Toon alleen data na vaccinatie'):
    df_filtered = df_weekly_new[df_weekly_new['Date'] >= '2021-01-06']
    fig_hist = px.bar(df_filtered, x='Date', y='New Cases',
        title='COVID-19 gevallen na vaccinatie',
        labels={'New Cases': 'Nieuwe Gevallen', 'Date': 'Datum'},
        template='plotly_dark', color_discrete_sequence=['#F23E2E'])
    
fig_hist.update_xaxes(dtick="M1", tickformat="%b %Y", tickangle=-45)
 
 
fig_hist.update_layout(
    autosize=False,
    width=1000,  
    height=500,  
    yaxis_range=[0, max(df_weekly_new['New Cases']) * 1.1],  
    margin=dict(l=40, r=40, t=50, b=80) 
)
 
# Voeg annotaties toe voor moment lockdown
fig_hist.add_vline(x='2020-03-15', line_width=2, line_dash="dash", line_color="yellow")
fig_hist.add_annotation(x='2020-03-15', y=700000, text="Start lockdown", showarrow=True, arrowhead=1)
 
# Meer annotaties toe voor moment vaccinaties
fig_hist.add_vline(x='2021-01-06', line_width=2, line_dash="dash", line_color="yellow")
fig_hist.add_annotation(x='2021-01-06', y=700000, text="Vaccinatie gestart", showarrow=True, arrowhead=1)
 
 
st.plotly_chart(fig_hist)

###################################
# PLOTS VAN THOMAS MET UITLEG #####
###################################
df_grouped = pd.read_csv('intensiteit_daily_average.csv')

#data per jaar filteren
data = {
    2019: df_grouped[df_grouped['jaar'] == 2019],
    2020: df_grouped[df_grouped['jaar'] == 2020],
    2021: df_grouped[df_grouped['jaar'] == 2021],
    2022: df_grouped[df_grouped['jaar'] == 2022],
    2023: df_grouped[df_grouped['jaar'] == 2023],
    2024: df_grouped[df_grouped['jaar'] == 2024]
}

st.write('''Met behulp van open datasets van NDW kan er inzicht verkregen worden in de intensiteit van verkeer op de A10 in Amsterdam. 
        In de onderstaande box kan gekozen worden tussen verschillende jaren. ''')

#selectbox maken om het jaar te selecteren
year = st.selectbox("Selecteer een jaar", range(2019,2025))
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

#barplot maken van de data
weekFig = px.bar(data[year], 
             x='dag', 
             y='gem_intensiteit',
             title=f"Intensiteit verkeerstromen in {year} (per week)", 
             labels={'dag': 'Dag van de week', 'gem_intensiteit': 'Aantal * 1000'}, 
             color='dag',
             category_orders={'dag': day_order},
             color_discrete_sequence=['salmon'],
             opacity=0.7)

#labels aanpassen
weekFig.update_layout(xaxis_title='Dag van de week',
                  yaxis_title='Aantal',
                  hovermode='x unified')

#figuur laten zien
st.plotly_chart(weekFig, use_container_width=True)

#select box 2:  jaarlijkse data 
st.write('''Met de volgende box kan een keuze gemaakt worden voor elke dag van de week. Voor elke dag worden de verschillende jaren naast
         elkaar geplot. Zo ontstaat er een duidelijk beeld welk jaar er het meeste verkeer was.''')

#alle jaren selecteren
all_years_data = df_grouped.groupby(['dag', 'jaar'])['gem_intensiteit'].mean().reset_index()
selected_day = st.selectbox("Selecteer een dag", day_order)
filtered_data = all_years_data[all_years_data['dag']==selected_day]

all_years_fig = px.bar(filtered_data, 
                        x='jaar', 
                        y='gem_intensiteit',
                        color='jaar',
                        title="Gemiddelde intensiteit per dag over alle jaren",
                        labels={'dag': 'Dag van de Week', 'gem_intensiteit': 'Aantal * 1000'},
                        category_orders={'dag': day_order},
                        opacity=0.7)

                
#figuur aanpassen
all_years_fig.update_layout(barmode='group',
                            xaxis_title='Dag van de Week',
                             yaxis_title='Aantal',
                             hovermode='x unified')
all_years_fig.update_xaxes(type='category')

st.plotly_chart(all_years_fig, use_container_width=True)

###################################
# PLOT VAN WEEKDAG PER JAAR #######
###################################

#Dagelijkse data laden
@st.cache_data
def load_daily_data():

    df = pd.read_csv('intensiteit_daily_average.csv')

    return df

df_daily = load_daily_data()

#Dropdown box maken en filteren op dag
st.write('''Wat was het effect van de COVID-19 pandemie op de verdeling van verkeersintensiteit binnen een dag?
          Daarvoor wordt gekeken naar de onderstaande grafiek. Te zien is de berekende gemiddelde verkeersintensiteit per weekdag per jaar.
         Wat op valt is dat de oude vetrouwde spitsuren niet zijn opgeschoven of uitgespreid, 
         wat het geval zou zijn als er een stijging was in het aannemen van flexibele werktijden. 
         Wel is te zien dat over het algemeen de verkeerintensiteit sterk daalde na de start van de COVID-19 pandemie. 
         Kijkende naar de lijnen van 2023 en 2024, blijkt ook dat deze daling in verkeersintensiteit nog niet genihileerd is.
         Mogelijk door het aanhouden van de thuiswerkcultuur.''')

#Dagelijkse data laden
@st.cache_data
def load_daily_data():

    df = pd.read_csv('intensiteit_daily_average.csv')

    return df

df_daily = load_daily_data()

#Dropdown box maken en filteren op dag
st.write('''Wat was het effect van de COVID-19 pandemie op de verdeling van verkeersintensiteit binnen een dag?
          Daarvoor kijken we naar onderstaande grafiek. Te zien is de berekende gemiddelde verkeersintensiteit per weekdag per jaar.
         Wat op valt is dat de oude vetrouwde spitsuren niet zijn opgeschoven of uitgespreid, 
         wat het geval zou zijn als er een stijging was in het aannemen van flexibele werktijden. 
         Wel is te zien dat over het algemeen de verkeerintensiteit sterk daalde na de start van de COVID-19 pandemie. 
         Kijkende naar de lijnen van 2023 en 2024, blijkt ook dat deze daling in verkeersintensiteit nog niet genihileerd is.
         Mogelijk door het aanhouden van de thuiswerkcultuur.''')

weekday = st.selectbox('Selecteer een dag', df_daily['dag'].unique())

dailyData = df_daily[df_daily['dag'] == weekday]

#Plot
dayFig = px.line(dailyData, x='tijd', y='gem_intensiteit', color='jaar',
              title=f'Intensiteit verkeersstromen op {weekday} - Vergelijking 2019-2024',
              labels={'tijd': 'Time', 'gem_intensiteit': 'Gemiddelde Intensiteit ()', 'year': 'Year'})

dayFig.update_xaxes(rangeslider_visible=True)
dayFig.update_layout(xaxis_title='Time of Day', yaxis_title='Average Intensity', hovermode='x')
   
st.plotly_chart(dayFig, use_container_width=True)


###################################
# CONCLUSIE? ######################
###################################

st.write('''De analyse toont aan dat de verkeersintensiteit tijdens de pandemie significant lager was. Er waren minder files.
         Terugkijkend op deze periode, is het belangrijk om lessen te trekken uit de verandering in mobiliteit. 
         De afname in files en de verbeterde luchtkwaliteit die tijdens de pandemie zichtbaar werden kunnen als voorbeeld dienen voor toekomstig beleid.''')

st.write('''Door flexibele werktijden en thuiswerken te stimuleren kunnen de pieken in de verkeersdrukte afvlakken.
         Dit zorgt voor minder verkeersdrukte en daarmee ook minder file. 
         Werkgevers kunnen een belangrijke rol spelen door flexibel werken toe te staan. Dit zal de mobiliteit en de leefbaarheid van stedelijke gebieden aanzienlijk verbeteren.''')