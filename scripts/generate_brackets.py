"""Generate bracket JSON files for 2022-2025 NCAA tournaments."""
import json
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRACKETS_DIR = os.path.join(PROJECT_DIR, "data", "brackets")

ROUND_NAMES = {
    0: "Round of 64",
    1: "Round of 32",
    2: "Sweet 16",
    3: "Elite 8",
    4: "Final Four",
    5: "Championship",
}


def game(game_id, round_num, t1_name, t1_seed, t2_name, t2_seed, winner):
    return {
        "game_id": game_id,
        "round_num": round_num,
        "round": ROUND_NAMES[round_num],
        "team1": {"name": t1_name, "seed": t1_seed},
        "team2": {"name": t2_name, "seed": t2_seed},
        "winner": winner,
    }


def make_2022():
    g = game
    games = [
        # === EAST REGION (1 Baylor) === Round of 64 (games 0-7)
        g(0,  0, "Baylor", 1, "Norfolk State", 16, "Baylor"),
        g(1,  0, "North Carolina", 8, "Marquette", 9, "North Carolina"),
        g(2,  0, "Saint Mary's", 5, "Indiana", 12, "Saint Mary's"),
        g(3,  0, "UCLA", 4, "Akron", 13, "UCLA"),
        g(4,  0, "Texas", 6, "Virginia Tech", 11, "Texas"),
        g(5,  0, "Purdue", 3, "Yale", 14, "Purdue"),
        g(6,  0, "Murray State", 7, "San Francisco", 10, "Murray State"),
        g(7,  0, "Kentucky", 2, "Saint Peter's", 15, "Saint Peter's"),
        # === MIDWEST REGION (1 Kansas) === Round of 64 (games 8-15)
        g(8,  0, "Kansas", 1, "Texas Southern", 16, "Kansas"),
        g(9,  0, "San Diego State", 8, "Creighton", 9, "Creighton"),
        g(10, 0, "Iowa", 5, "Richmond", 12, "Richmond"),
        g(11, 0, "Providence", 4, "South Dakota State", 13, "Providence"),
        g(12, 0, "Louisiana State", 6, "Iowa State", 11, "Iowa State"),
        g(13, 0, "Wisconsin", 3, "Colgate", 14, "Wisconsin"),
        g(14, 0, "Southern California", 7, "Miami (FL)", 10, "Miami (FL)"),
        g(15, 0, "Auburn", 2, "Jacksonville State", 15, "Auburn"),
        # === SOUTH REGION (1 Arizona) === Round of 64 (games 16-23)
        g(16, 0, "Arizona", 1, "Wright State", 16, "Arizona"),
        g(17, 0, "Seton Hall", 8, "TCU", 9, "TCU"),
        g(18, 0, "Houston", 5, "UAB", 12, "Houston"),
        g(19, 0, "Illinois", 4, "Chattanooga", 13, "Illinois"),
        g(20, 0, "Colorado State", 6, "Michigan", 11, "Michigan"),
        g(21, 0, "Tennessee", 3, "Longwood", 14, "Tennessee"),
        g(22, 0, "Ohio State", 7, "Loyola (IL)", 10, "Ohio State"),
        g(23, 0, "Villanova", 2, "Delaware", 15, "Villanova"),
        # === WEST REGION (1 Gonzaga) === Round of 64 (games 24-31)
        g(24, 0, "Gonzaga", 1, "Georgia State", 16, "Gonzaga"),
        g(25, 0, "Boise State", 8, "Memphis", 9, "Memphis"),
        g(26, 0, "Connecticut", 5, "New Mexico State", 12, "New Mexico State"),
        g(27, 0, "Arkansas", 4, "Vermont", 13, "Arkansas"),
        g(28, 0, "Alabama", 6, "Notre Dame", 11, "Notre Dame"),
        g(29, 0, "Texas Tech", 3, "Montana State", 14, "Texas Tech"),
        g(30, 0, "Michigan State", 7, "Davidson", 10, "Michigan State"),
        g(31, 0, "Duke", 2, "Cal State Fullerton", 15, "Duke"),

        # === EAST Round of 32 (games 32-35) ===
        g(32, 1, "Baylor", 1, "North Carolina", 8, "North Carolina"),
        g(33, 1, "Saint Mary's", 5, "UCLA", 4, "UCLA"),
        g(34, 1, "Texas", 6, "Purdue", 3, "Purdue"),
        g(35, 1, "Murray State", 7, "Saint Peter's", 15, "Saint Peter's"),
        # === MIDWEST Round of 32 (games 36-39) ===
        g(36, 1, "Kansas", 1, "Creighton", 9, "Kansas"),
        g(37, 1, "Richmond", 12, "Providence", 4, "Providence"),
        g(38, 1, "Iowa State", 11, "Wisconsin", 3, "Iowa State"),
        g(39, 1, "Miami (FL)", 10, "Auburn", 2, "Miami (FL)"),
        # === SOUTH Round of 32 (games 40-43) ===
        g(40, 1, "Arizona", 1, "TCU", 9, "Arizona"),
        g(41, 1, "Houston", 5, "Illinois", 4, "Houston"),
        g(42, 1, "Michigan", 11, "Tennessee", 3, "Michigan"),
        g(43, 1, "Ohio State", 7, "Villanova", 2, "Villanova"),
        # === WEST Round of 32 (games 44-47) ===
        g(44, 1, "Gonzaga", 1, "Memphis", 9, "Gonzaga"),
        g(45, 1, "New Mexico State", 12, "Arkansas", 4, "Arkansas"),
        g(46, 1, "Notre Dame", 11, "Texas Tech", 3, "Texas Tech"),
        g(47, 1, "Michigan State", 7, "Duke", 2, "Duke"),

        # === EAST Sweet 16 (games 48-49) ===
        g(48, 2, "North Carolina", 8, "UCLA", 4, "North Carolina"),
        g(49, 2, "Purdue", 3, "Saint Peter's", 15, "Saint Peter's"),
        # === MIDWEST Sweet 16 (games 50-51) ===
        g(50, 2, "Kansas", 1, "Providence", 4, "Kansas"),
        g(51, 2, "Iowa State", 11, "Miami (FL)", 10, "Miami (FL)"),
        # === SOUTH Sweet 16 (games 52-53) ===
        g(52, 2, "Arizona", 1, "Houston", 5, "Houston"),
        g(53, 2, "Michigan", 11, "Villanova", 2, "Villanova"),
        # === WEST Sweet 16 (games 54-55) ===
        g(54, 2, "Gonzaga", 1, "Arkansas", 4, "Arkansas"),
        g(55, 2, "Texas Tech", 3, "Duke", 2, "Duke"),

        # === EAST Elite 8 (game 56) ===
        g(56, 3, "North Carolina", 8, "Saint Peter's", 15, "North Carolina"),
        # === MIDWEST Elite 8 (game 57) ===
        g(57, 3, "Kansas", 1, "Miami (FL)", 10, "Kansas"),
        # === SOUTH Elite 8 (game 58) ===
        g(58, 3, "Houston", 5, "Villanova", 2, "Villanova"),
        # === WEST Elite 8 (game 59) ===
        g(59, 3, "Arkansas", 4, "Duke", 2, "Duke"),

        # === Final Four (games 60-61) ===
        g(60, 4, "North Carolina", 8, "Duke", 2, "North Carolina"),
        g(61, 4, "Kansas", 1, "Villanova", 2, "Kansas"),

        # === Championship (game 62) ===
        g(62, 5, "Kansas", 1, "North Carolina", 8, "Kansas"),
    ]
    return {"year": 2022, "games": games, "total_games": len(games)}


def make_2023():
    g = game
    games = [
        # === EAST REGION (1 Purdue) === Round of 64 (games 0-7)
        g(0,  0, "Purdue", 1, "FDU", 16, "FDU"),
        g(1,  0, "Memphis", 8, "Florida Atlantic", 9, "Florida Atlantic"),
        g(2,  0, "Duke", 5, "Oral Roberts", 12, "Duke"),
        g(3,  0, "Tennessee", 4, "Louisiana", 13, "Tennessee"),
        g(4,  0, "Kentucky", 6, "Providence", 11, "Kentucky"),
        g(5,  0, "Kansas State", 3, "Montana State", 14, "Kansas State"),
        g(6,  0, "Michigan State", 7, "Southern California", 10, "Michigan State"),
        g(7,  0, "Marquette", 2, "Vermont", 15, "Marquette"),
        # === MIDWEST REGION (1 Houston) === Round of 64 (games 8-15)
        g(8,  0, "Houston", 1, "Northern Kentucky", 16, "Houston"),
        g(9,  0, "Iowa", 8, "Auburn", 9, "Auburn"),
        g(10, 0, "Miami (FL)", 5, "Drake", 12, "Miami (FL)"),
        g(11, 0, "Indiana", 4, "Kent State", 13, "Indiana"),
        g(12, 0, "Iowa State", 6, "Pittsburgh", 11, "Pittsburgh"),
        g(13, 0, "Xavier", 3, "Kennesaw State", 14, "Xavier"),
        g(14, 0, "Texas A&M", 7, "Penn State", 10, "Penn State"),
        g(15, 0, "Texas", 2, "Colgate", 15, "Texas"),
        # === SOUTH REGION (1 Alabama) === Round of 64 (games 16-23)
        g(16, 0, "Alabama", 1, "Texas A&M-Corpus Christi", 16, "Alabama"),
        g(17, 0, "Maryland", 8, "West Virginia", 9, "Maryland"),
        g(18, 0, "San Diego State", 5, "College of Charleston", 12, "San Diego State"),
        g(19, 0, "Virginia", 4, "Furman", 13, "Furman"),
        g(20, 0, "Creighton", 6, "NC State", 11, "Creighton"),
        g(21, 0, "Baylor", 3, "UC Santa Barbara", 14, "Baylor"),
        g(22, 0, "Missouri", 7, "Utah State", 10, "Missouri"),
        g(23, 0, "Arizona", 2, "Princeton", 15, "Princeton"),
        # === WEST REGION (1 Kansas) === Round of 64 (games 24-31)
        g(24, 0, "Kansas", 1, "Howard", 16, "Kansas"),
        g(25, 0, "Arkansas", 8, "Illinois", 9, "Arkansas"),
        g(26, 0, "Saint Mary's", 5, "Virginia Commonwealth", 12, "Saint Mary's"),
        g(27, 0, "Connecticut", 4, "Iona", 13, "Connecticut"),
        g(28, 0, "TCU", 6, "Arizona State", 11, "TCU"),
        g(29, 0, "Gonzaga", 3, "Grand Canyon", 14, "Gonzaga"),
        g(30, 0, "Northwestern", 7, "Boise State", 10, "Northwestern"),
        g(31, 0, "UCLA", 2, "UNC Asheville", 15, "UCLA"),

        # === EAST Round of 32 (games 32-35) ===
        g(32, 1, "FDU", 16, "Florida Atlantic", 9, "Florida Atlantic"),
        g(33, 1, "Duke", 5, "Tennessee", 4, "Tennessee"),
        g(34, 1, "Kentucky", 6, "Kansas State", 3, "Kansas State"),
        g(35, 1, "Michigan State", 7, "Marquette", 2, "Michigan State"),
        # === MIDWEST Round of 32 (games 36-39) ===
        g(36, 1, "Houston", 1, "Auburn", 9, "Houston"),
        g(37, 1, "Miami (FL)", 5, "Indiana", 4, "Miami (FL)"),
        g(38, 1, "Pittsburgh", 11, "Xavier", 3, "Xavier"),
        g(39, 1, "Penn State", 10, "Texas", 2, "Texas"),
        # === SOUTH Round of 32 (games 40-43) ===
        g(40, 1, "Alabama", 1, "Maryland", 8, "Alabama"),
        g(41, 1, "San Diego State", 5, "Furman", 13, "San Diego State"),
        g(42, 1, "Creighton", 6, "Baylor", 3, "Creighton"),
        g(43, 1, "Missouri", 7, "Princeton", 15, "Princeton"),
        # === WEST Round of 32 (games 44-47) ===
        g(44, 1, "Kansas", 1, "Arkansas", 8, "Arkansas"),
        g(45, 1, "Saint Mary's", 5, "Connecticut", 4, "Connecticut"),
        g(46, 1, "TCU", 6, "Gonzaga", 3, "Gonzaga"),
        g(47, 1, "Northwestern", 7, "UCLA", 2, "UCLA"),

        # === EAST Sweet 16 (games 48-49) ===
        g(48, 2, "Florida Atlantic", 9, "Tennessee", 4, "Florida Atlantic"),
        g(49, 2, "Kansas State", 3, "Michigan State", 7, "Kansas State"),
        # === MIDWEST Sweet 16 (games 50-51) ===
        g(50, 2, "Houston", 1, "Miami (FL)", 5, "Miami (FL)"),
        g(51, 2, "Xavier", 3, "Texas", 2, "Texas"),
        # === SOUTH Sweet 16 (games 52-53) ===
        g(52, 2, "Alabama", 1, "San Diego State", 5, "San Diego State"),
        g(53, 2, "Creighton", 6, "Princeton", 15, "Creighton"),
        # === WEST Sweet 16 (games 54-55) ===
        g(54, 2, "Arkansas", 8, "Connecticut", 4, "Connecticut"),
        g(55, 2, "Gonzaga", 3, "UCLA", 2, "Gonzaga"),

        # === EAST Elite 8 (game 56) ===
        g(56, 3, "Florida Atlantic", 9, "Kansas State", 3, "Florida Atlantic"),
        # === MIDWEST Elite 8 (game 57) ===
        g(57, 3, "Miami (FL)", 5, "Texas", 2, "Miami (FL)"),
        # === SOUTH Elite 8 (game 58) ===
        g(58, 3, "San Diego State", 5, "Creighton", 6, "San Diego State"),
        # === WEST Elite 8 (game 59) ===
        g(59, 3, "Connecticut", 4, "Gonzaga", 3, "Connecticut"),

        # === Final Four (games 60-61) ===
        g(60, 4, "Florida Atlantic", 9, "San Diego State", 5, "San Diego State"),
        g(61, 4, "Connecticut", 4, "Miami (FL)", 5, "Connecticut"),

        # === Championship (game 62) ===
        g(62, 5, "Connecticut", 4, "San Diego State", 5, "Connecticut"),
    ]
    return {"year": 2023, "games": games, "total_games": len(games)}


def make_2024():
    g = game
    games = [
        # === EAST REGION (1 UConn) === Round of 64 (games 0-7)
        g(0,  0, "Connecticut", 1, "Stetson", 16, "Connecticut"),
        g(1,  0, "Florida Atlantic", 8, "Northwestern", 9, "Northwestern"),
        g(2,  0, "San Diego State", 5, "UAB", 12, "San Diego State"),
        g(3,  0, "Auburn", 4, "Yale", 13, "Yale"),
        g(4,  0, "Brigham Young", 6, "Duquesne", 11, "Duquesne"),
        g(5,  0, "Illinois", 3, "Morehead State", 14, "Illinois"),
        g(6,  0, "Washington State", 7, "Drake", 10, "Washington State"),
        g(7,  0, "Iowa State", 2, "South Dakota State", 15, "Iowa State"),
        # === MIDWEST REGION (1 Purdue) === Round of 64 (games 8-15)
        g(8,  0, "Purdue", 1, "Grambling", 16, "Purdue"),
        g(9,  0, "Utah State", 8, "TCU", 9, "Utah State"),
        g(10, 0, "Gonzaga", 5, "McNeese State", 12, "Gonzaga"),
        g(11, 0, "Kansas", 4, "Samford", 13, "Kansas"),
        g(12, 0, "South Carolina", 6, "Oregon", 11, "Oregon"),
        g(13, 0, "Creighton", 3, "Akron", 14, "Creighton"),
        g(14, 0, "Texas", 7, "Colorado State", 10, "Texas"),
        g(15, 0, "Tennessee", 2, "Saint Peter's", 15, "Tennessee"),
        # === SOUTH REGION (1 Houston) === Round of 64 (games 16-23)
        g(16, 0, "Houston", 1, "Longwood", 16, "Houston"),
        g(17, 0, "Nebraska", 8, "Texas A&M", 9, "Texas A&M"),
        g(18, 0, "Wisconsin", 5, "James Madison", 12, "James Madison"),
        g(19, 0, "Duke", 4, "Vermont", 13, "Duke"),
        g(20, 0, "Texas Tech", 6, "NC State", 11, "NC State"),
        g(21, 0, "Kentucky", 3, "Oakland", 14, "Oakland"),
        g(22, 0, "Florida", 7, "Colorado", 10, "Colorado"),
        g(23, 0, "Marquette", 2, "Western Kentucky", 15, "Marquette"),
        # === WEST REGION (1 North Carolina) === Round of 64 (games 24-31)
        g(24, 0, "North Carolina", 1, "Wagner", 16, "North Carolina"),
        g(25, 0, "Mississippi State", 8, "Michigan State", 9, "Michigan State"),
        g(26, 0, "Saint Mary's", 5, "Grand Canyon", 12, "Grand Canyon"),
        g(27, 0, "Alabama", 4, "College of Charleston", 13, "Alabama"),
        g(28, 0, "Clemson", 6, "New Mexico", 11, "Clemson"),
        g(29, 0, "Baylor", 3, "Colgate", 14, "Baylor"),
        g(30, 0, "Dayton", 7, "Nevada", 10, "Dayton"),
        g(31, 0, "Arizona", 2, "Long Beach State", 15, "Arizona"),

        # === EAST Round of 32 (games 32-35) ===
        g(32, 1, "Connecticut", 1, "Northwestern", 9, "Connecticut"),
        g(33, 1, "San Diego State", 5, "Yale", 13, "San Diego State"),
        g(34, 1, "Duquesne", 11, "Illinois", 3, "Illinois"),
        g(35, 1, "Washington State", 7, "Iowa State", 2, "Iowa State"),
        # === MIDWEST Round of 32 (games 36-39) ===
        g(36, 1, "Purdue", 1, "Utah State", 8, "Purdue"),
        g(37, 1, "Gonzaga", 5, "Kansas", 4, "Gonzaga"),
        g(38, 1, "Oregon", 11, "Creighton", 3, "Creighton"),
        g(39, 1, "Texas", 7, "Tennessee", 2, "Tennessee"),
        # === SOUTH Round of 32 (games 40-43) ===
        g(40, 1, "Houston", 1, "Texas A&M", 9, "Houston"),
        g(41, 1, "James Madison", 12, "Duke", 4, "Duke"),
        g(42, 1, "NC State", 11, "Oakland", 14, "NC State"),
        g(43, 1, "Colorado", 10, "Marquette", 2, "Marquette"),
        # === WEST Round of 32 (games 44-47) ===
        g(44, 1, "North Carolina", 1, "Michigan State", 9, "North Carolina"),
        g(45, 1, "Grand Canyon", 12, "Alabama", 4, "Alabama"),
        g(46, 1, "Clemson", 6, "Baylor", 3, "Clemson"),
        g(47, 1, "Dayton", 7, "Arizona", 2, "Arizona"),

        # === EAST Sweet 16 (games 48-49) ===
        g(48, 2, "Connecticut", 1, "San Diego State", 5, "Connecticut"),
        g(49, 2, "Illinois", 3, "Iowa State", 2, "Illinois"),
        # === MIDWEST Sweet 16 (games 50-51) ===
        g(50, 2, "Purdue", 1, "Gonzaga", 5, "Purdue"),
        g(51, 2, "Creighton", 3, "Tennessee", 2, "Tennessee"),
        # === SOUTH Sweet 16 (games 52-53) ===
        g(52, 2, "Houston", 1, "Duke", 4, "Duke"),
        g(53, 2, "NC State", 11, "Marquette", 2, "NC State"),
        # === WEST Sweet 16 (games 54-55) ===
        g(54, 2, "North Carolina", 1, "Alabama", 4, "Alabama"),
        g(55, 2, "Clemson", 6, "Arizona", 2, "Clemson"),

        # === EAST Elite 8 (game 56) ===
        g(56, 3, "Connecticut", 1, "Illinois", 3, "Connecticut"),
        # === MIDWEST Elite 8 (game 57) ===
        g(57, 3, "Purdue", 1, "Tennessee", 2, "Purdue"),
        # === SOUTH Elite 8 (game 58) ===
        g(58, 3, "Duke", 4, "NC State", 11, "NC State"),
        # === WEST Elite 8 (game 59) ===
        g(59, 3, "Alabama", 4, "Clemson", 6, "Alabama"),

        # === Final Four (games 60-61) ===
        g(60, 4, "Connecticut", 1, "Alabama", 4, "Connecticut"),
        g(61, 4, "Purdue", 1, "NC State", 11, "Purdue"),

        # === Championship (game 62) ===
        g(62, 5, "Connecticut", 1, "Purdue", 1, "Connecticut"),
    ]
    return {"year": 2024, "games": games, "total_games": len(games)}


def make_2025():
    g = game
    games = [
        # === EAST REGION (1 Duke) === Round of 64 (games 0-7)
        g(0,  0, "Duke", 1, "Mount St. Mary's", 16, "Duke"),
        g(1,  0, "Mississippi State", 8, "Baylor", 9, "Baylor"),
        g(2,  0, "Oregon", 5, "Liberty", 12, "Oregon"),
        g(3,  0, "Arizona", 4, "Akron", 13, "Arizona"),
        g(4,  0, "Brigham Young", 6, "Virginia Commonwealth", 11, "Brigham Young"),
        g(5,  0, "Wisconsin", 3, "Montana", 14, "Wisconsin"),
        g(6,  0, "Saint Mary's", 7, "Vanderbilt", 10, "Saint Mary's"),
        g(7,  0, "Alabama", 2, "Robert Morris", 15, "Alabama"),
        # === MIDWEST REGION (1 Houston) === Round of 64 (games 8-15)
        g(8,  0, "Houston", 1, "SIU Edwardsville", 16, "Houston"),
        g(9,  0, "Gonzaga", 8, "Georgia", 9, "Gonzaga"),
        g(10, 0, "Clemson", 5, "McNeese State", 12, "McNeese State"),
        g(11, 0, "Purdue", 4, "High Point", 13, "Purdue"),
        g(12, 0, "Illinois", 6, "Xavier", 11, "Illinois"),
        g(13, 0, "Kentucky", 3, "Troy", 14, "Kentucky"),
        g(14, 0, "UCLA", 7, "Utah State", 10, "UCLA"),
        g(15, 0, "Tennessee", 2, "Wofford", 15, "Tennessee"),
        # === SOUTH REGION (1 Auburn) === Round of 64 (games 16-23)
        g(16, 0, "Auburn", 1, "Alabama State", 16, "Auburn"),
        g(17, 0, "Louisville", 8, "Creighton", 9, "Creighton"),
        g(18, 0, "Michigan", 5, "UC San Diego", 12, "Michigan"),
        g(19, 0, "Texas A&M", 4, "Yale", 13, "Texas A&M"),
        g(20, 0, "Mississippi", 6, "North Carolina", 11, "Mississippi"),
        g(21, 0, "Iowa State", 3, "Lipscomb", 14, "Iowa State"),
        g(22, 0, "Marquette", 7, "New Mexico", 10, "New Mexico"),
        g(23, 0, "Michigan State", 2, "Bryant", 15, "Michigan State"),
        # === WEST REGION (1 Florida) === Round of 64 (games 24-31)
        g(24, 0, "Florida", 1, "Norfolk State", 16, "Florida"),
        g(25, 0, "Connecticut", 8, "Oklahoma", 9, "Connecticut"),
        g(26, 0, "Memphis", 5, "Colorado State", 12, "Colorado State"),
        g(27, 0, "Maryland", 4, "Grand Canyon", 13, "Maryland"),
        g(28, 0, "Missouri", 6, "Drake", 11, "Drake"),
        g(29, 0, "Texas Tech", 3, "UNC Wilmington", 14, "Texas Tech"),
        g(30, 0, "Kansas", 7, "Arkansas", 10, "Arkansas"),
        g(31, 0, "St. John's (NY)", 2, "Omaha", 15, "St. John's (NY)"),

        # === EAST Round of 32 (games 32-35) ===
        g(32, 1, "Duke", 1, "Baylor", 9, "Duke"),
        g(33, 1, "Oregon", 5, "Arizona", 4, "Arizona"),
        g(34, 1, "Brigham Young", 6, "Wisconsin", 3, "Brigham Young"),
        g(35, 1, "Saint Mary's", 7, "Alabama", 2, "Alabama"),
        # === MIDWEST Round of 32 (games 36-39) ===
        g(36, 1, "Houston", 1, "Gonzaga", 8, "Houston"),
        g(37, 1, "McNeese State", 12, "Purdue", 4, "Purdue"),
        g(38, 1, "Illinois", 6, "Kentucky", 3, "Kentucky"),
        g(39, 1, "UCLA", 7, "Tennessee", 2, "Tennessee"),
        # === SOUTH Round of 32 (games 40-43) ===
        g(40, 1, "Auburn", 1, "Creighton", 9, "Auburn"),
        g(41, 1, "Michigan", 5, "Texas A&M", 4, "Michigan"),
        g(42, 1, "Mississippi", 6, "Iowa State", 3, "Mississippi"),
        g(43, 1, "New Mexico", 10, "Michigan State", 2, "Michigan State"),
        # === WEST Round of 32 (games 44-47) ===
        g(44, 1, "Florida", 1, "Connecticut", 8, "Florida"),
        g(45, 1, "Colorado State", 12, "Maryland", 4, "Maryland"),
        g(46, 1, "Drake", 11, "Texas Tech", 3, "Texas Tech"),
        g(47, 1, "Arkansas", 10, "St. John's (NY)", 2, "Arkansas"),

        # === EAST Sweet 16 (games 48-49) ===
        g(48, 2, "Duke", 1, "Arizona", 4, "Duke"),
        g(49, 2, "Brigham Young", 6, "Alabama", 2, "Alabama"),
        # === MIDWEST Sweet 16 (games 50-51) ===
        g(50, 2, "Houston", 1, "Purdue", 4, "Houston"),
        g(51, 2, "Kentucky", 3, "Tennessee", 2, "Tennessee"),
        # === SOUTH Sweet 16 (games 52-53) ===
        g(52, 2, "Auburn", 1, "Michigan", 5, "Auburn"),
        g(53, 2, "Mississippi", 6, "Michigan State", 2, "Michigan State"),
        # === WEST Sweet 16 (games 54-55) ===
        g(54, 2, "Florida", 1, "Maryland", 4, "Florida"),
        g(55, 2, "Texas Tech", 3, "Arkansas", 10, "Texas Tech"),

        # === EAST Elite 8 (game 56) ===
        g(56, 3, "Duke", 1, "Alabama", 2, "Duke"),
        # === MIDWEST Elite 8 (game 57) ===
        g(57, 3, "Houston", 1, "Tennessee", 2, "Houston"),
        # === SOUTH Elite 8 (game 58) ===
        g(58, 3, "Auburn", 1, "Michigan State", 2, "Auburn"),
        # === WEST Elite 8 (game 59) ===
        g(59, 3, "Florida", 1, "Texas Tech", 3, "Florida"),

        # === Final Four (games 60-61) ===
        g(60, 4, "Florida", 1, "Auburn", 1, "Florida"),
        g(61, 4, "Houston", 1, "Duke", 1, "Houston"),

        # === Championship (game 62) ===
        g(62, 5, "Florida", 1, "Houston", 1, "Florida"),
    ]
    return {"year": 2025, "games": games, "total_games": len(games)}


def main():
    os.makedirs(BRACKETS_DIR, exist_ok=True)

    for year, maker in [(2022, make_2022), (2023, make_2023), (2024, make_2024), (2025, make_2025)]:
        data = maker()
        assert len(data["games"]) == 63, f"{year}: expected 63 games, got {len(data['games'])}"
        path = os.path.join(BRACKETS_DIR, f"bracket_{year}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  Wrote {path} ({len(data['games'])} games)")


if __name__ == "__main__":
    main()
