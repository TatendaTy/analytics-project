import logging
import json
from airflow.hooks.base import BaseHook

def _get_db_connection():
    """Helper function to get database connection"""
    database_conn_id = 'analytics_database'
    connection = BaseHook.get_connection(database_conn_id)
    return connection.schema

def upsert_player_data(player_json):
    import sqlite3
    
    sqlite_db_path = _get_db_connection()
    
    if player_json:
        player_data = json.loads(player_json) # parse the JSON string into a Python dictionary
        # use a context manager for the SQLite connection
        with sqlite3.connect(sqlite_db_path) as conn:
            cursor = conn.cursor() # execute SQL commands using the cursor object
            
            # insert each player record into the 'player' table
            for player in player_data:
                # use a parameterized query to prevent SQL injection and ensure proper handling of data types, and implement error handling to log any issues that occur during the database operation
                try:
                    cursor.execute("""
                        INSERT INTO player (player_id, gsis_id, first_name, last_name, position, last_changed_date)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT(player_id) DO UPDATE SET
                            gsis_id=excluded.gsis_id,
                            first_name=excluded.first_name,
                            last_name=excluded.last_name,
                            position=excluded.position,
                            last_changed_date=excluded.last_changed_date
                    """, (
                        player['player_id'],
                        player['gsis_id'],
                        player['first_name'],
                        player['last_name'],
                        player['position'],
                        player['last_changed_date']
                    ))
                except Exception as e:
                    logging.error(f"Failed to insert player {player['player_id']}: {e}")
                    raise
    else:
        logging.warning("No player data found.")
        raise ValueError("No player data found. Task failed due to missing data.")

def upsert_league_data(league_json):
    import sqlite3
    
    sqlite_db_path = _get_db_connection()
    
    if league_json:
        league_data = json.loads(league_json)
        with sqlite3.connect(sqlite_db_path) as conn:
            cursor = conn.cursor()
            
            for league in league_data:
                try:
                    cursor.execute("""
                        INSERT INTO league (league_id, league_name, league_short_name)
                        VALUES (?, ?, ?)
                        ON CONFLICT(league_id) DO UPDATE SET
                            league_name=excluded.league_name,
                            league_short_name=excluded.league_short_name
                    """, (
                        league['league_id'],
                        league.get('league_name'),
                        league.get('league_short_name')
                    ))
                except Exception as e:
                    logging.error(f"Failed to insert league {league.get('league_id')}: {e}")
                    raise
    else:
        logging.warning("No league data found.")
        raise ValueError("No league data found. Task failed due to missing data.")

def upsert_team_data(team_json):
    import sqlite3
    
    sqlite_db_path = _get_db_connection()
    
    if team_json:
        team_data = json.loads(team_json)
        with sqlite3.connect(sqlite_db_path) as conn:
            cursor = conn.cursor()
            
            for team in team_data:
                try:
                    cursor.execute("""
                        INSERT INTO team (team_id, team_name, team_abbr)
                        VALUES (?, ?, ?)
                        ON CONFLICT(team_id) DO UPDATE SET
                            team_name=excluded.team_name,
                            team_abbr=excluded.team_abbr
                    """, (
                        team['team_id'],
                        team.get('team_name'),
                        team.get('team_abbr')
                    ))
                except Exception as e:
                    logging.error(f"Failed to insert team {team.get('team_id')}: {e}")
                    raise
    else:
        logging.warning("No team data found.")
        raise ValueError("No team data found. Task failed due to missing data.")

def upsert_performance_data(performance_json):
    import sqlite3
    
    sqlite_db_path = _get_db_connection()
    
    if performance_json:
        performance_data = json.loads(performance_json)
        with sqlite3.connect(sqlite_db_path) as conn:
            cursor = conn.cursor()
            
            for perf in performance_data:
                try:
                    cursor.execute("""
                        INSERT INTO performance (player_id, week, team, fantasy_points)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(player_id, week) DO UPDATE SET
                            team=excluded.team,
                            fantasy_points=excluded.fantasy_points
                    """, (
                        perf.get('player_id'),
                        perf.get('week'),
                        perf.get('team'),
                        perf.get('fantasy_points')
                    ))
                except Exception as e:
                    logging.error(f"Failed to insert performance for player {perf.get('player_id')}: {e}")
                    raise
    else:
        logging.warning("No performance data found.")
        raise ValueError("No performance data found. Task failed due to missing data.")

def upsert_week_data(week_json):
    import sqlite3
    
    sqlite_db_path = _get_db_connection()
    
    if week_json:
        week_data = json.loads(week_json)
        with sqlite3.connect(sqlite_db_path) as conn:
            cursor = conn.cursor()
            
            for week in week_data:
                try:
                    cursor.execute("""
                        INSERT INTO week (week_id, week_num, season, start_date, end_date)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(week_id) DO UPDATE SET
                            week_num=excluded.week_num,
                            season=excluded.season,
                            start_date=excluded.start_date,
                            end_date=excluded.end_date
                    """, (
                        week.get('week_id'),
                        week.get('week_num'),
                        week.get('season'),
                        week.get('start_date'),
                        week.get('end_date')
                    ))
                except Exception as e:
                    logging.error(f"Failed to insert week {week.get('week_id')}: {e}")
                    raise
    else:
        logging.warning("No week data found.")
        raise ValueError("No week data found. Task failed due to missing data.")