import pandas as pd
import plotly.express as px
from dash import Dash, html, dash_table, dcc

app = Dash()
server = app.server

import numpy as np

#startgroup = 1

def readtodf(csvfile):
    runrsDf = pd.read_csv(csvfile)
    return runrsDf

def dfprep(df: pd.DataFrame):
    df.replace({'-': pd.NA, '–': pd.NA},  inplace=True)
    df['TimeTotalDelta'] = pd.to_timedelta(df['TimeTotal'])
    df['duration_minutes'] = (df['TimeTotalDelta'].dt.total_seconds() / 60).round(2)

def totsumdf(df: pd.DataFrame):
    racestatuses = {rs : list() for rs in df['RaceStatus'].unique()}
    for rs in racestatuses:
        racestatuses[rs].append(sum(df['RaceStatus'] == rs))
    racestatuses['Signed up'] = len(df.index)
    allrunersStatus = pd.DataFrame.from_dict(racestatuses)
    return allrunersStatus

def renderdash(df):
    global app
    rstatDf = totsumdf(df)

    startedfig = px.histogram(df, x='RaceStatus', nbins=4, color='StartGroup', barmode='group', title="Status per startgrupp, klicka legend till höger för att filtrera grupper",
                              labels={"RaceStatus": "Status", "count": "Number of Participants"})

    combfig = px.histogram(df, x="duration_minutes", nbins=300, color="StartGroup", title=f"Antal åkare som gick i mål samtidigt* per startgrupp  (* inom 2 minuter). Klicka legend för filtrering")
    combfig.add_vline(x=705, line_width=1, line_dash='dash', line_color='black')

    breakfig = px.histogram(df, x='LastSplit', nbins=11, color='StartGroup', barmode='group', category_orders={
        'LastSplit': ['Högsta punkten', 'Smågan', 'Mångsbodarna', 'Risberg', 'Evertsberg', 'Oxberg', 'Hökberg',
                      'Eldris', 'Finish']}, title="Antal åkare som senast passerade resp kontroll (har antingen brutit vid kontrollen, på väg till nästa eller inte klarat repet vid nästa). Klicka legend för att filtrera startgrupp")

    dfcnt = df.count()
    dfcnt = dfcnt.filter(like='time_day')
    newname = dict()
    for n, i in enumerate(dfcnt.index):
        indname = i.split('_')[0]
        newname[dfcnt.index[n]] = indname
    dfcnt.rename(newname, inplace=True)
    ctrlfig = px.line(dfcnt, labels={'index': 'Kontroll', 'value': 'Antal åkare som passerat'}, title="Antal åkare kvar i loppet efter respektive kontroll")
    print(f'\n= = = = = = = = = = = =\n_,-:::: Laying out ::::-,_\n= = = = = = = = = = = =\n'
    app.layout = [
            html.Div(children='Statistik från Öppet spår 90 söndag 2025'),
            dash_table.DataTable(data=rstatDf.to_dict('records')),
            dcc.Graph(figure=startedfig),
            dcc.Graph(figure=combfig),
            dcc.Graph(figure=breakfig),
            html.Img(src='assets/sparprofilmreptid.jpg', style={'width': '90%', 'margin-left': '25px'}),
            dcc.Graph(figure=ctrlfig)
            ]

if __name__ == '__main__':
    runrsDf = readtodf('assets/oppetSp25_allgrp.csv')
    dfprep(runrsDf)
    renderdash(runrsDf)
    app.run(host='0.0.0.0', port=10000)
