# -*- coding: utf-8 -*-
"""
Created on Tue Jun 22 10:39:56 2021

@author: 91959
"""


import streamlit as st
import pandas as pd
from statsbombpy import sb
import matplotlib.pyplot as plt
from mplsoccer.pitch import Pitch,VerticalPitch
import seaborn as sns


st.set_option('deprecation.showPyplotGlobalUse', False)

# @st.cache(allow_output_mutation = True)
# def load_data():
#     df_CL_17_18 = df_comp = sb.competitions()

#     return comps,gender,seasons
def get_match_id():

    df_comp = sb.competitions()
    # comps = get_competitions()
    st.sidebar.title('Football analysis Selection')
    gender = st.sidebar.selectbox("Select gender",df_comp['competition_gender'].unique())
    df_gender = df_comp[df_comp['competition_gender'] == gender]
    if len(df_gender) > 0:
        # st.dataframe(df_gender)
        league = st.sidebar.selectbox("Select Competition",df_gender['competition_name'].unique())
        df_league = df_gender[df_gender['competition_name'] == league]
        if len(df_league) > 0:
            # st.dataframe(df_league)
            season = st.sidebar.selectbox("Select Season",df_league['season_name'].unique())
            df_season = df_league[df_league['season_name'] == season]
            if len(df_season) > 0:
                # st.dataframe(df_season)
                # comp_gender = st.sidebar.selectbox("Competition",comps[comps['competition_gender'] == gender])
                # specific_comp = comps[comps['competition_name' == comp]]
                # season = st.sidebar.selectbox("Season",specific_comp['season_name'].unique())
                comp_id = df_season.iloc[0]['competition_id']
                season_id = df_season.iloc[0]['season_id']

                df_matches = sb.matches(competition_id = comp_id ,season_id =season_id )
                if len(df_matches) > 0:
                    # st.dataframe(df_matches)

                    round = st.sidebar.selectbox('Choose the round you want to view',df_matches['competition_stage'].unique())
                    df_round = df_matches[df_matches['competition_stage'] == round]
                    if len(df_round) > 0:
                        # st.dataframe(df_round[['match_id','home_team','away_team','competition_stage']])
                        match = st.sidebar.selectbox('Select the match you want to analyze',[df_round.iloc[i]['home_team'] + '-' + df_round.iloc[i]['away_team'] for i in range(len(df_round))])
                        teams = match.split('-')
                        # st.write(teams)
                        chosen_match = df_round[(df_round['home_team'] == teams[0]) & (df_round['away_team'] == teams[1])]
                        st.dataframe(chosen_match)
                        match_id = chosen_match.iloc[0]['match_id']
                        
                        return match_id

def main():
   
    st.title("Football viz")
    st.header('Football analysis')
    match_id = get_match_id()
    st.write(match_id)
    df_events = events = sb.events(match_id=match_id)
    
    # st.dataframe(df_events.head())
    team = st.selectbox('Select the team you want to analyze',df_events['team'].unique())
    task = st.selectbox('Select viz',['Pass','Shots','Player heat map'])
    if task == 'Pass':
        df_pass = df_events[(df_events['team'] == team) & (df_events['type'] == 'Pass')].sort_values('minute').reset_index()
        df_pass['pass_outcome'] = df_pass['pass_outcome'].fillna('Success')
        df_pass[['x','y']] = df_pass['location'].apply(pd.Series)
        df_pass[['end_x','end_y']] = df_pass['pass_end_location'].apply(pd.Series)

        player = st.selectbox('Enter the player name',df_pass['player'].unique())

        fig, ax = plt.subplots(figsize=(13.5,8))
        fig.set_facecolor('#22312b')
        ax.patch.set_facecolor('#22312b')
        pitch = Pitch(pitch_type='statsbomb', orientation='horizontal',
                    pitch_color='#22312b', line_color='#c7d5cc', figsize=(16, 11),
                    constrained_layout=True, tight_layout=True)
        pitch.draw(ax =ax)
        # plt.gca().invert_yaxis()
        # st.pyplot(fig)


        player_pass = df_pass[(df_pass['player'] == player) & (df_pass['minute'] < 91)].reset_index(drop=True)

        for i in range(len(player_pass)):
            if player_pass['pass_outcome'][i] == 'Success':
                ax.plot((player_pass['x'][i],player_pass['end_x'][i]),(player_pass['y'][i],player_pass['end_y'][i]),color = 'green')
                ax.scatter(player_pass['x'][i],player_pass['y'][i],color ='green')
            if (player_pass['pass_outcome'][i] == 'Success') & (player_pass['pass_height'][i] == 'High Pass'):
                ax.plot((player_pass['x'][i],player_pass['end_x'][i]),(player_pass['y'][i],player_pass['end_y'][i]),ls = '--',color = 'green')
                ax.scatter(player_pass['x'][i],player_pass['y'][i],color ='green')
            if player_pass['pass_outcome'][i] == 'Incomplete':
                ax.plot((player_pass['x'][i],player_pass['end_x'][i]),(player_pass['y'][i],player_pass['end_y'][i]),color = 'red')
                ax.scatter(player_pass['x'][i],player_pass['y'][i],color ='red')
        st.pyplot(fig)

    if task == 'Shots':
        pass
    if task == 'Player heat map':
        df_team_events = df_events[(df_events['team'] == team)].sort_values('minute').reset_index(drop=True).dropna(subset=['player'])
        player = st.selectbox('Select player you want',df_team_events['player'].unique())
        df_pos = df_team_events[['player','location','minute','timestamp','team']].dropna(subset=['player','location']).reset_index(drop=True).sort_values('minute')
        # st.dataframe(df_pos[df_pos['player'] == player])
        # st.write(player)
        df_player_pos = df_pos[df_pos['player'] == player]
        df_player_pos[['x','y']] = df_player_pos['location'].apply(pd.Series)
        pitch = VerticalPitch(pitch_color='#22312b', line_color='#c7d5cc', figsize=(7, 4),tight_layout =True)
        fig,ax = pitch.draw()
        fig.set_facecolor('#22312b')
        sns.kdeplot(df_player_pos['x'],df_player_pos['y'],cmap='coolwarm',shade=True,shade_lowest=False,alpha = 0.7,thresh=0.4,levels=100,vertical=True,linewidth=0)
        plt.xlim(0,80)
        plt.ylim(0,120)
        # fig.size = (8,5)
        st.pyplot(fig)

if __name__ == '__main__':
    main()