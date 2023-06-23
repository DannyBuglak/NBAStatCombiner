#
# Main part of the code that does everything
#

# Import all necessary data
from math import floor

from nba_api.stats.endpoints import playergamelog
from nba_api.stats.library import data

import pandas as pd

# Website for API and data https://github.com/swar/nba_api/blob/master/src/nba_api/library/


# Function to find index of id by name in data
def find_index_of_id_by_name(lst, value):
    for i, sublist in enumerate(lst):
        if value in sublist:
            return i, sublist.index(value)
    return -1, -1


player_name = input("Enter Player Name EXACTLY as Spelled: ")

# Find the player index inside the large list of lists in data.py
playerIndex = find_index_of_id_by_name(data.players, player_name)

if playerIndex == (-1, -1):     # Player not found
    print("Error: Name not found.")
    print("Maybe player name is misspelled?")
    print("Rerun the program.")

else:
    # Find the player id
    playerId = data.players[playerIndex[0]][0]

    print("\nEnter a valid date.")
    print("Date must be 2000+ and format for years is date - date+1 (2019 -> 2019-20 season)")
    season = input("Season: ")

    pd.set_option('display.max_columns', None)          # Have all cols be available
    pd.set_option('display.max_rows', None)             # Have all rows be available

    # Get the game log for the inputted player for inputted season
    gameLog = playergamelog.PlayerGameLog(playerId, season)

    # Get all the needed data (Output w/o second set of brackets to find header values]
    gameDate = gameLog.get_data_frames()[0]['GAME_DATE']
    matchUp = gameLog.get_data_frames()[0]['MATCHUP']
    winLoss = gameLog.get_data_frames()[0]['WL']
    points = gameLog.get_data_frames()[0]['PTS']
    rebounds = gameLog.get_data_frames()[0]['REB']
    assists = gameLog.get_data_frames()[0]['AST']
    threes = gameLog.get_data_frames()[0]['FG3M']

    # A dataframe for points, assists, rebounds to calculate P+A+R
    PAR_Dataframe = pd.DataFrame({"points": points, "assists": assists, "rebounds": rebounds})
    # Calculate Points+Assists+Rebounds and add to data frame later
    PAR = PAR_Dataframe.sum(axis=1)

    # A dataframe for points, and assists to calculate P+A
    PA_Dataframe = pd.DataFrame({"points": points, "assists": assists})
    # Calculate Points+Assists and add to data frame later
    PA = PA_Dataframe.sum(axis=1)

    # A dataframe for points and rebounds to calculate P+R
    PR_Dataframe = pd.DataFrame({"points": points, "rebounds": rebounds})
    # Calculate Points+Rebounds and add to data frame later
    PR = PR_Dataframe.sum(axis=1)

    # Calculate the averages of everything and round to 2 decimal places
    averagePPG_Season = round(sum(points)/len(points), 1)
    averageAST_Season = round(sum(assists)/len(assists), 1)
    averageREB_Season = round(sum(rebounds)/len(rebounds), 1)
    averagePAR_Season = round(sum(PAR) / len(PAR_Dataframe), 1)
    averagePA_Season = round(sum(PA) / len(PA_Dataframe), 1)
    averagePR_Season = round(sum(PR) / len(PR_Dataframe), 1)

    # Create the pandas data frame and print, save for later for output
    outputDataFrame = pd.DataFrame({'Game Date:': gameDate, 'Match Up:': matchUp, 'Win/Loss:': winLoss,
                                    'Points:': points, 'Rebounds:': rebounds, 'Assists:': assists,
                                    'Threes Made': threes, 'Pts+Asts+Rebs:': PAR, 'Pts+Asts:': PA, 'Pts+Rebs:': PR})

    print(outputDataFrame)

    # Output the averages for the season
    print("\nAverages for the Season: ")
    print("Avg PPG:", averagePPG_Season,
          "\nAvg AST:", averageAST_Season,
          "\nAvg REB:", averageREB_Season,
          "\nAvg PAR:", averagePAR_Season,
          "\nAvg PR:", averagePR_Season,
          "\nAvg PA:", averagePA_Season)

    # This dataframe will have the Season summarized info in it
    summarizedSeasonDataFrame = pd.DataFrame({"Avg PPG Season": [averagePPG_Season],
                    "Avg AST Season:": [averageAST_Season],
                    "Avg REB Season:": [averageREB_Season],
                    "Avg PAR Season:": [averagePAR_Season],
                    "Avg PR Season:": [averagePR_Season],
                    "Avg PA Season:": [averagePA_Season]})

    # Function to calculate all the averages for certain amount of games
    # @param val : the count of last games to be count, most likely 5, 10, 25
    def create_averages(val):
        avgPPG = round(sum(gameLog.get_data_frames()[0]['PTS'][:val]) / val, 1)
        avgAST = round(sum(gameLog.get_data_frames()[0]['AST'][:val]) / val, 1)
        avgREB = round(sum(gameLog.get_data_frames()[0]['REB'][:val]) / val, 1)
        avgPAR = round(sum(PAR[:val]) / val, 1)
        avgPA = round(sum(PA[:val]) / val, 1)
        avgPR = round(sum(PR[:val]) / val, 1)

        # Create a dataframe that will later be concatenated
        averagesGames = pd.DataFrame({
              "Num Games:": [val],
              "Avg PPG:": [avgPPG],
              "Avg AST:": [avgAST],
              "Avg REB:": [avgREB],
              "Avg PAR:": [avgPAR],
              "Avg PR:": [avgPR],
              "Avg PA:": [avgPA]})

        print("\n")
        print("Averages for last " + str(val) + " games: ",
              "\nAvg PPG:", avgPPG,
              "\nAvg AST:", avgAST,
              "\nAvg REB:", avgREB,
              "\nAvg PAR:", avgPAR,
              "\nAvg PR:", avgPR,
              "\nAvg PA:", avgPA)

        return averagesGames

    fiveGames = create_averages(5)
    tenGames = create_averages(10)
    twentyFiveGames = create_averages(25)

    # Concatenate a large data frame to store all the averages for the last 5 10 25 games
    summarizedGamesDataFrame = pd.concat([fiveGames, tenGames, twentyFiveGames], ignore_index=True)

    print("\n============================================================")

    # Take in a list of thresholds to calculate
    thresholds = map(int, (input("Input thresholds (separated by only a space): ")).split())

    # Calculate the american odds based off percentage
    # @param : percentage, the calculated percentage found from the count / val in next function
    def calculate_odds(percentage):
        if percentage <= 0:
            return 0
        if percentage >= 1.0:
            return "XX-XX"
        if percentage * 100 < 50:
            return floor((100 / ((percentage * 100) / 100)) - 100)
        else:
            return floor(((percentage * 100) / (1 - ((percentage * 100) / 100))) * -1)

    # Calculate amount of games above threshold for each category
    # @param thresh : amount to count above
    # @param val : the last amount of games, 5 10 or 25
    def calculate_above_threshold(thresh, val):
        # Calculate the count of games above this inputted threshold using pandas features
        countAbovePPG = (gameLog.get_data_frames()[0]['PTS'][:val] >= thresh).sum()
        countAboveREB = (gameLog.get_data_frames()[0]['REB'][:val] >= thresh).sum()
        countAboveAST = (gameLog.get_data_frames()[0]['AST'][:val] >= thresh).sum()
        countAbovePAR = (PAR[:val] >= thresh).sum()
        countAbovePA = (PA[:val] >= thresh).sum()
        countAbovePR = (PR[:val] >= thresh).sum()

        print("\n")

        # Print everything out in this order: Count, Percentage, Decimal Odds, American Odds
        print("Games [" + str(val) + "] above Threshold [" + str(threshold)
              + "] including: Count, Percentage, Decimal Odds, and American Odds: ",

              "\nPoints:", countAbovePPG, str(round(countAbovePPG / val * 100))+"%",
                    round(1 / ((countAbovePPG / val * 100) / 100), 2) if countAbovePPG > 0 else 0,
                    calculate_odds(countAbovePPG / val),

              "\nAssists:", countAboveAST, str(round(countAboveAST / val * 100))+"%",
                    round(1 / ((countAboveAST / val * 100) / 100), 2) if countAboveAST > 0 else 0,
                    calculate_odds(countAboveAST / val),

              "\nRebounds:", countAboveREB, str(round(countAboveREB / val * 100))+"%",
                    round(1 / ((countAboveREB / val * 100) / 100), 2) if countAboveREB > 0 else 0,
                    calculate_odds(countAboveREB / val),

              "\nPAR:", countAbovePAR, str(round(countAbovePAR / val * 100))+"%",
                    round(1 / ((countAbovePAR / val * 100) / 100), 2) if countAbovePAR > 0 else 0,
                    calculate_odds(countAbovePAR / val),

              "\nPR:", countAbovePR, str(round(countAbovePR / val * 100))+"%",
                    round(1 / ((countAbovePR / val * 100) / 100), 2) if countAbovePR > 0 else 0,
                    calculate_odds(countAbovePR / val),

              "\nPA:", countAbovePA, str(round(countAbovePA / val * 100))+"%",
                    round(1 / ((countAbovePA / val * 100) / 100), 2) if countAbovePA > 0 else 0,
                    calculate_odds(countAbovePA / val))

        # Create a dictionary that will later turn into a pandas dictionary
        data = {
            'Games & Threshold': [str(val) + "&" + str(threshold), str(val) + "&" + str(threshold),
                                  str(val) + "&" + str(threshold), str(val) + "&" + str(threshold),
                                  str(val) + "&" + str(threshold), str(val) + "&" + str(threshold)],
            'Category': ['Points', 'Assists', 'Rebounds', 'PAR', 'PR', 'PA'],
            'Count': [countAbovePPG, countAboveAST, countAboveREB, countAbovePAR, countAbovePR, countAbovePA],
            'Percentage': [str(round(countAbovePPG / val * 100))+"%", str(round(countAboveAST / val * 100))+"%",
                           str(round(countAboveREB / val * 100))+"%", str(round(countAbovePAR / val * 100))+"%",
                           str(round(countAbovePR / val * 100))+"%", str(round(countAbovePA / val * 100))+"%"],
            'Decimal Odds': [round(1 / ((countAbovePPG / val * 100) / 100), 2) if countAbovePPG > 0 else 0,
                             round(1 / ((countAboveAST / val * 100) / 100), 2) if countAboveAST > 0 else 0,
                             round(1 / ((countAboveREB / val * 100) / 100), 2) if countAboveREB > 0 else 0,
                             round(1 / ((countAbovePAR / val * 100) / 100), 2) if countAbovePAR > 0 else 0,
                             round(1 / ((countAbovePR / val * 100) / 100), 2) if countAbovePR > 0 else 0,
                             round(1 / ((countAbovePA / val * 100) / 100), 2) if countAbovePA > 0 else 0],
            'American Odds': [calculate_odds(countAbovePPG / val), calculate_odds(countAboveAST / val),
                              calculate_odds(countAboveREB / val), calculate_odds(countAbovePAR / val),
                              calculate_odds(countAbovePR / val), calculate_odds(countAbovePA / val)]
        }

        summarizedOddsDF = pd.DataFrame(data)

        return summarizedOddsDF

    allOddsDataFrame = pd.DataFrame()

    # Loop through inputted thresholds and output them
    for threshold in thresholds:
        # Get data frames for the current threshold and the 3 types of last games
        oddsDF5 = calculate_above_threshold(threshold, 5)
        oddsDF10 = calculate_above_threshold(threshold, 10)
        oddsDF25 = calculate_above_threshold(threshold, 25)

        # Combine into 1 data frame
        combinedDataFrame = pd.concat([oddsDF5, oddsDF10, oddsDF25], ignore_index=True)

        # Add it to the large dataframe
        allOddsDataFrame = allOddsDataFrame._append(combinedDataFrame)

    outputDataFrame.to_csv("GameLog.csv", index=False)
    summarizedSeasonDataFrame.to_csv("SeasonSummarized.csv", index=False)
    summarizedGamesDataFrame.to_csv("GamesSummarized.csv", index=False)
    allOddsDataFrame.to_csv("OddsSummarized.csv", index=False)

