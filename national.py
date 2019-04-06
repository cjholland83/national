# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 20:22:30 2019

@author: hollachr
"""

import pandas as pd
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import dc_stat_think as dcst
sns.set()

# read in the probability
df_sp = pd.read_csv('new_data.csv')

# calculate the implied probability and total market size
df_sp['imp_prob'] = 1/df_sp.price_exc
market_size = np.sum(df_sp.imp_prob)

# broadcast the normalised probability
df_sp['normalised_prob'] = df_sp.imp_prob / market_size

# read in the bets
df_bets = pd.read_csv('bet_no_lay.csv')

# calculate the total bets of players own money
total_money_wagered = np.sum(df_bets.stake)

# calculate the win payout multiplied by the stake noting that freebets identi
df_bets['win_payout'] = df_bets.price * df_bets.stake

# calculate the place payout price (1-5 and 1/4 odds) multiplied by the part stake
df_bets['ew_payout'] = ((df_bets.price - 1.0) / 4 + 1.0) * df_bets.stake

# calculate the liability for the win
df_bets['win_liability'] = (df_bets.lay_price - 1.0) * df_bets.lay

# set up empty list for results
results = []

# set up and empty list of winners
winners = []

# simulate n grand nationals
for n in range(10000):

    # Place according to estimated probability and reset index to simulated order
    simulated_race = df_sp.sample(frac=1, weights=df_sp.normalised_prob).reset_index(drop=True)

    # select winner
    winner = [simulated_race.horse[0]]
    
    # append to the winners list
    winners.append(winner[0])

    # check if winner was backed
    win_df = df_bets[df_bets.horse.isin(winner)]

    # sum the win payout
    win_payout = np.sum(win_df.win_payout) - np.sum(win_df.win_liability) - np.sum(win_df.lay)

    # select place (paying 5 places)
    place = simulated_race.iloc[1:5,0]

    # check if place was backed
    place_df = df_bets[df_bets.horse.isin(place)]

    # sum the place payout
    place_payout = np.sum(place_df.ew_payout) + np.sum(place_df.lay)
    
    # check if the horse did not place
    did_not_place_df = df_bets[np.logical_not(df_bets.horse.isin(place))]
    
    # sum the did not place payout
    did_not_place_payout = np.sum(did_not_place_df.lay)

    # calculate result
    result = win_payout + place_payout + did_not_place_payout - total_money_wagered

    # append the result
    results.append(result)

    # print to track number of nationals run
    #print('Number of nationals run: ',n+1)

mean_result = np.mean(results)
median_result = np.median(results)
ci_95 = np.percentile(results, [2.5,97.5])

fmt = '£{x:,.0f}'
tick = mtick.StrMethodFormatter(fmt)
fig, ax = plt.subplots(1,1)
_ = plt.plot(*dcst.ecdf(results), marker='.', linestyle='none')
ax.xaxis.set_major_formatter(tick)
_ = plt.xticks(rotation=25)
#_ = plt.axvline(x=mean_result,color='k')
#_ = plt.axvline(x=ci_95[0],color='g')
#_ = plt.axvline(x=ci_95[1],color='g')
_ = plt.xlabel('Net Return (£)')
_ = plt.ylabel('ECDF')
_ = plt.title('Grand National Simulated Returns')

plt.tight_layout()
plt.show()

print('''
      Mean expected return: £{0:,.2f}
      Median expected return: £{1:,.2f}
      95% CI: £{2:,.2f} to £{3:,.2f}'''.format(mean_result,median_result, *ci_95))
