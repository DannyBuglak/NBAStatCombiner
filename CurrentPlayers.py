#
# Create CSV sheets that outputs all current NBA players who average 15+ minutes per game
#
# Website for API and data https://github.com/swar/nba_api/blob/master/src/nba_api/library/
#

# Imports
from math import floor

from nba_api.stats.endpoints import playergamelog
from nba_api.stats.library import data

import pandas as pd

pd.set_option('display.max_columns', None)          # Have all cols be available
pd.set_option('display.max_rows', None)             # Have all rows be available

# Store all current player's data in this list
currentPlayers = []

# Index for checking if player is current active
activeIndex = data.player_index_is_active

# Loop through all the players and check if they are currently playing,
# if so, add them to the Current Players list
for player in data.players:
    if player[activeIndex]:
        currentPlayers.append(player)

print(currentPlayers)

# Store all players who have above 15 minutes average in this list with their player ID
players = []

# Loop through the current players and get their data
for currPlayer in currentPlayers:
    playerID = currPlayer[0]
    playerName = currPlayer[3]
    gameLog = playergamelog.PlayerGameLog(playerID, "2023")

    if len(gameLog.get_data_frames()[0]['MIN']) > 0:
        avgMins = round(sum(gameLog.get_data_frames()[0]['MIN']) / len(gameLog.get_data_frames()[0]['MIN']), 3)

        if avgMins >= 15:
            players.append((playerID, playerName))

print(players)