"""
NBA Player Stats Combiner
Fetches and analyzes player data
"""

# Import all necessary data
from math import floor
from NBA_API.src.nba_api.stats.endpoints import playergamelog
from NBA_API.src.nba_api.stats.library import data
import pandas as pd

# Website for API and data https://github.com/swar/nba_api/blob/master/src/nba_api/library/


def find_index_of_id_by_name(lst, value):
    """Find index of ID by player name"""
    for i, sublist in enumerate(lst):
        if value in sublist:
            return i, sublist.index(value)
    return -1, -1


def menu():
    """
    Display menu to select a player by first name letter.
    Ask user for what letter, can be upper or lower case,
    Then print all the players that are active whose names start with this letter
    """
    letter = input("Enter letter of first name: ").upper()

    for i, sublist in enumerate(data.players):
        if sublist[3][0] == letter and sublist[4]:
            print(i, "-", sublist[3])

    player_id = int(input("Choose Player Number: "))
    return player_id


def fetch_game_log(player_id, season):
    """
    Fetch game log for a player for a given season.
    Returns the game log object.
    """
    return playergamelog.PlayerGameLog(player_id, season)


def extract_game_data(game_log):
    """
    Extract all relevant game data from the game log.
    Returns a dictionary with all the extracted data series.
    """
    df = game_log.get_data_frames()[0]

    game_data = {
        'game_date': df['GAME_DATE'].str[:6],
        'matchup': df['MATCHUP'],
        'win_loss': df['WL'],
        'points': df['PTS'],
        'rebounds': df['REB'],
        'assists': df['AST'],
        'threes': df['FG3M'],
        'steals': df['STL'],
        'blocks': df['BLK'],
        'minutes': df['MIN'],
        'personal_fouls': df['PF']
    }

    return game_data


def calculate_combined_stats(game_data):
    """
    Calculate combined statistics (PAR, PA, PR) and per-minute stats.
    Returns a dictionary with calculated stats.
    """
    points = game_data['points']
    assists = game_data['assists']
    rebounds = game_data['rebounds']
    minutes = game_data['minutes']

    # Calculate combined stats
    PAR = points + assists + rebounds
    PA = points + assists
    PR = points + rebounds

    # Calculate per-minute stats
    par_per_minute = round((points + assists + rebounds) / minutes, 3)
    pa_per_minute = round((points + assists) / minutes, 3)
    pr_per_minute = round((points + rebounds) / minutes, 3)

    return {
        'PAR': PAR,
        'PA': PA,
        'PR': PR,
        'par_per_minute': par_per_minute,
        'pa_per_minute': pa_per_minute,
        'pr_per_minute': pr_per_minute
    }


def calculate_season_averages(game_data, combined_stats):
    """
    Calculate season averages for all statistics.
    Returns a dictionary with all season averages.
    """
    points = game_data['points']
    assists = game_data['assists']
    rebounds = game_data['rebounds']
    minutes = game_data['minutes']
    PAR = combined_stats['PAR']
    PA = combined_stats['PA']
    PR = combined_stats['PR']

    num_games = len(points)

    averages = {
        'ppg': round(sum(points) / num_games, 1),
        'ast': round(sum(assists) / num_games, 1),
        'reb': round(sum(rebounds) / num_games, 1),
        'par': round(sum(PAR) / num_games, 1),
        'pa': round(sum(PA) / num_games, 1),
        'pr': round(sum(PR) / num_games, 1),
        'min': round(sum(minutes) / num_games, 3)
    }

    # Calculate per-minute averages
    averages['par_per_min'] = round(averages['par'] / averages['min'], 3)
    averages['pa_per_min'] = round(averages['pa'] / averages['min'], 3)
    averages['pr_per_min'] = round(averages['pr'] / averages['min'], 3)

    return averages


def create_game_log_dataframe(game_data, combined_stats):
    """
    Create a pandas DataFrame with all game log data.
    Returns the formatted DataFrame.
    """
    return pd.DataFrame({
        'Game Date:': game_data['game_date'],
        'Match Up:': game_data['matchup'],
        'Win/Loss:': game_data['win_loss'],
        'Minutes': game_data['minutes'],
        'Points:': game_data['points'],
        'Rebounds:': game_data['rebounds'],
        'Assists:': game_data['assists'],
        'Pts+Asts+Rebs:': combined_stats['PAR'],
        'Pts+Asts:': combined_stats['PA'],
        'Pts+Rebs:': combined_stats['PR'],
        'PAR/Min:': combined_stats['par_per_minute'],
        'PA/Min': combined_stats['pa_per_minute'],
        'PR/Min': combined_stats['pr_per_minute'],
        'Threes Made:': game_data['threes'],
        'Blocks:': game_data['blocks'],
        'Steals:': game_data['steals'],
        'Personal Fouls:': game_data['personal_fouls']
    })


def create_season_summary_dataframe(season_averages):
    """
    Create a DataFrame summarizing season statistics.
    Returns the summary DataFrame.
    """
    return pd.DataFrame({
        "Avg Min Season:": [season_averages['min']],
        "Avg PPG Season:": [season_averages['ppg']],
        "Avg AST Season:": [season_averages['ast']],
        "Avg REB Season:": [season_averages['reb']],
        "Avg PAR Season:": [season_averages['par']],
        "Avg PR Season:": [season_averages['pr']],
        "Avg PA Season:": [season_averages['pa']],
        "Avg PAR/min Season:": [season_averages['par_per_min']],
        "Avg PR/min Season:": [season_averages['pr_per_min']],
        "Avg PA/min Season:": [season_averages['pa_per_min']]
    })


def print_season_averages(season_averages):
    """Print season averages to console."""
    print("\nAverages for the Season: ")
    print(f"Avg PPG: {season_averages['ppg']}")
    print(f"Avg AST: {season_averages['ast']}")
    print(f"Avg REB: {season_averages['reb']}")
    print(f"Avg PAR: {season_averages['par']}")
    print(f"Avg PR: {season_averages['pr']}")
    print(f"Avg PA: {season_averages['pa']}")
    print(f"Avg Min: {season_averages['min']}")
    print(f"Avg PAR/min: {season_averages['par_per_min']}")
    print(f"Avg PR/min: {season_averages['pr_per_min']}")
    print(f"Avg PA/min: {season_averages['pa_per_min']}")


def calculate_game_window_averages(game_data, combined_stats, num_games):
    """
    Calculate averages for a specific number of recent games.

    Args:
        game_data: Dictionary of game data
        combined_stats: Dictionary of combined statistics
        num_games: Number of recent games to analyze

    Returns:
        DataFrame with the calculated averages
    """
    points = game_data['points'][:num_games]
    assists = game_data['assists'][:num_games]
    rebounds = game_data['rebounds'][:num_games]
    minutes = game_data['minutes'][:num_games]
    PAR = combined_stats['PAR'][:num_games]
    PA = combined_stats['PA'][:num_games]
    PR = combined_stats['PR'][:num_games]

    avg_ppg = round(sum(points) / num_games, 1)
    avg_ast = round(sum(assists) / num_games, 1)
    avg_reb = round(sum(rebounds) / num_games, 1)
    avg_par = round(sum(PAR) / num_games, 1)
    avg_pa = round(sum(PA) / num_games, 1)
    avg_pr = round(sum(PR) / num_games, 1)
    avg_min = round(sum(minutes) / num_games, 3)
    avg_par_per_min = round(avg_par / avg_min, 3)
    avg_pr_per_min = round(avg_pr / avg_min, 3)
    avg_pa_per_min = round(avg_pa / avg_min, 3)

    # Print to console
    print(f"\nAverages for last {num_games} games:")
    print(f"Avg Min: {avg_min}")
    print(f"Avg PPG: {avg_ppg}")
    print(f"Avg AST: {avg_ast}")
    print(f"Avg REB: {avg_reb}")
    print(f"Avg PAR: {avg_par}")
    print(f"Avg PR: {avg_pr}")
    print(f"Avg PA: {avg_pa}")
    print(f"Avg PAR/min: {avg_par_per_min}")
    print(f"Avg PR/min: {avg_pr_per_min}")
    print(f"Avg PA/min: {avg_pa_per_min}")

    # Create DataFrame
    return pd.DataFrame({
        "Num Games:": [num_games],
        "Avg Min:": [avg_min],
        "Avg PPG:": [avg_ppg],
        "Avg AST:": [avg_ast],
        "Avg REB:": [avg_reb],
        "Avg PAR:": [avg_par],
        "Avg PR:": [avg_pr],
        "Avg PA:": [avg_pa],
        "Avg PAR/min:": [avg_par_per_min],
        "Avg PR/min:": [avg_pr_per_min],
        "Avg PA/min:": [avg_pa_per_min]
    })


def calculate_american_odds(percentage):
    """
    Calculate American odds from a percentage.

    Args:
        percentage: Win probability as a decimal (0-1)

    Returns:
        American odds as integer or string
    """
    if percentage <= 0:
        return 0
    if percentage >= 1.0:
        return "XX-XX"

    percentage_value = percentage * 100

    if percentage_value < 50:
        return floor((100 / (percentage_value / 100)) - 100)
    else:
        return floor((percentage_value / (1 - (percentage_value / 100))) * -1)


def calculate_threshold_statistics(game_data, combined_stats, threshold, num_games, player_name):
    """
    Calculate statistics for games above a threshold.

    Args:
        game_data: Dictionary of game data
        combined_stats: Dictionary of combined statistics
        threshold: The threshold value to compare against
        num_games: Number of recent games to analyze
        player_name: Name of the player

    Returns:
        DataFrame with threshold statistics and odds
    """
    # Get data for specified number of games
    points = game_data['points'][:num_games]
    assists = game_data['assists'][:num_games]
    rebounds = game_data['rebounds'][:num_games]
    PAR = combined_stats['PAR'][:num_games]
    PA = combined_stats['PA'][:num_games]
    PR = combined_stats['PR'][:num_games]

    # Calculate counts above threshold
    count_above_ppg = (points >= threshold).sum()
    count_above_reb = (rebounds >= threshold).sum()
    count_above_ast = (assists >= threshold).sum()
    count_above_par = (PAR >= threshold).sum()
    count_above_pa = (PA >= threshold).sum()
    count_above_pr = (PR >= threshold).sum()

    # Print to console
    print(
        f"\nGames [{num_games}] above Threshold [{threshold}] including: Count, Percentage, Decimal Odds, and American Odds:")

    categories = [
        ('Points', count_above_ppg),
        ('Assists', count_above_ast),
        ('Rebounds', count_above_reb),
        ('PAR', count_above_par),
        ('PR', count_above_pr),
        ('PA', count_above_pa)
    ]

    for cat_name, count in categories:
        percentage = round(count / num_games * 100)
        decimal_odds = round(1 / ((count / num_games * 100) / 100), 2) if count > 0 else 0
        american_odds = calculate_american_odds(count / num_games)
        print(f"{cat_name}: {count} {percentage}% {decimal_odds} {american_odds}")

    # Create DataFrame
    data_dict = {
        player_name: [" ", " ", " ", " ", " ", " "],
        'Category': ['Points', 'Assists', 'Rebounds', 'PAR', 'PR', 'PA'],
        'Amount of Games': [str(num_games)] * 6,
        'Threshold': [str(threshold)] * 6,
        'Count': [count_above_ppg, count_above_ast, count_above_reb, count_above_par, count_above_pr, count_above_pa],
        'Percentage': [],
        'Decimal Odds': [],
        'American Odds': []
    }

    # Calculate percentage, decimal odds, and American odds for each category
    for count in [count_above_ppg, count_above_ast, count_above_reb, count_above_par, count_above_pr, count_above_pa]:
        percentage = round(count / num_games * 100)
        data_dict['Percentage'].append(f"{percentage}%")
        data_dict['Decimal Odds'].append(round(1 / ((count / num_games * 100) / 100), 2) if count > 0 else 0)
        data_dict['American Odds'].append(calculate_american_odds(count / num_games))

    return pd.DataFrame(data_dict)


def save_output_files(game_log_df, season_summary_df, games_summary_df, odds_df):
    """Save all output DataFrames to CSV files."""
    game_log_df.to_csv("output/GameLog.csv", index=False)
    season_summary_df.to_csv("output/SeasonSummarized.csv", index=False)
    games_summary_df.to_csv("output/GamesSummarized.csv", index=False)
    odds_df.to_csv("output/OddsSummarized.csv", index=False)
    print("\nAll files saved to output/ directory")


def main():
    """Main function to run the NBA stats analyzer."""
    # Configure pandas display options
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    # Select player
    player_index = menu()
    player_name = data.players[player_index][3]
    player_id = data.players[player_index][0]
    print(f"\n -> Player Selected: {player_name} <- ")

    # Set season
    season = "2025-26"

    # Fetch game log
    game_log = fetch_game_log(player_id, season)

    # Check if data exists
    if game_log.get_data_frames()[0].empty or len(game_log.get_data_frames()[0]) == 0:
        print(f"\nNo games found for {player_name} in the {season} season.")
        print("This player may not have played any games yet this season.")
        return

    # Extract and calculate data
    game_data = extract_game_data(game_log)
    combined_stats = calculate_combined_stats(game_data)
    season_averages = calculate_season_averages(game_data, combined_stats)

    # Create and display game log DataFrame
    game_log_df = create_game_log_dataframe(game_data, combined_stats)
    print(game_log_df)

    # Display season averages
    print_season_averages(season_averages)

    # Create season summary DataFrame
    season_summary_df = create_season_summary_dataframe(season_averages)

    # Calculate averages for different game windows
    games_5 = calculate_game_window_averages(game_data, combined_stats, 5)
    games_10 = calculate_game_window_averages(game_data, combined_stats, 10)
    games_25 = calculate_game_window_averages(game_data, combined_stats, 25)

    # Combine game window summaries
    games_summary_df = pd.concat([games_5, games_10, games_25], ignore_index=True)

    print("\n============================================================")

    # Get thresholds from user
    thresholds = list(map(int, input("Input thresholds (separated by only a space): ").split()))

    # Calculate threshold statistics for all combinations
    all_odds_df = pd.DataFrame()

    for threshold in thresholds:
        odds_5 = calculate_threshold_statistics(game_data, combined_stats, threshold, 5, player_name)
        odds_10 = calculate_threshold_statistics(game_data, combined_stats, threshold, 10, player_name)
        odds_25 = calculate_threshold_statistics(game_data, combined_stats, threshold, 25, player_name)

        combined_odds = pd.concat([odds_5, odds_10, odds_25], ignore_index=True)
        all_odds_df = pd.concat([all_odds_df, combined_odds], ignore_index=True)

    # Save all output files
    save_output_files(game_log_df, season_summary_df, games_summary_df, all_odds_df)


if __name__ == "__main__":
    main()

