"""Generate bracket JSON files for 2018, 2019, 2021 NCAA tournaments."""
import json, os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRACKETS_DIR = os.path.join(PROJECT_DIR, "data", "brackets")
ROUND_NAMES = {0: "Round of 64", 1: "Round of 32", 2: "Sweet 16", 3: "Elite 8", 4: "Final Four", 5: "Championship"}

def g(gid, rnd, t1, s1, t2, s2, winner):
    return {"game_id": gid, "round_num": rnd, "round": ROUND_NAMES[rnd],
            "team1": {"name": t1, "seed": s1}, "team2": {"name": t2, "seed": s2}, "winner": winner}


def make_2018():
    """2018: Villanova won championship. UMBC 16-over-1 upset of Virginia. Loyola Chicago Cinderella run."""
    games = [
        # === EAST (1 Villanova) R64 ===
        g(0, 0, "Villanova", 1, "Radford", 16, "Villanova"),
        g(1, 0, "Virginia Tech", 8, "Alabama", 9, "Alabama"),
        g(2, 0, "West Virginia", 5, "Murray State", 12, "West Virginia"),
        g(3, 0, "Wichita State", 4, "Marshall", 13, "Marshall"),
        g(4, 0, "Florida", 6, "St. Bonaventure", 11, "Florida"),
        g(5, 0, "Texas Tech", 3, "Stephen F. Austin", 14, "Texas Tech"),
        g(6, 0, "Arkansas", 7, "Butler", 10, "Butler"),
        g(7, 0, "Purdue", 2, "Cal State Fullerton", 15, "Purdue"),
        # === SOUTH (1 Virginia) R64 ===
        g(8, 0, "Virginia", 1, "Maryland-Baltimore County", 16, "Maryland-Baltimore County"),
        g(9, 0, "Creighton", 8, "Kansas State", 9, "Kansas State"),
        g(10, 0, "Kentucky", 5, "Davidson", 12, "Kentucky"),
        g(11, 0, "Arizona", 4, "Buffalo", 13, "Buffalo"),
        g(12, 0, "Miami (FL)", 6, "Loyola (IL)", 11, "Loyola (IL)"),
        g(13, 0, "Tennessee", 3, "Wright State", 14, "Tennessee"),
        g(14, 0, "Nevada", 7, "Texas", 10, "Nevada"),
        g(15, 0, "Cincinnati", 2, "Georgia State", 15, "Cincinnati"),
        # === MIDWEST (1 Kansas) R64 ===
        g(16, 0, "Kansas", 1, "Pennsylvania", 16, "Kansas"),
        g(17, 0, "Seton Hall", 8, "NC State", 9, "Seton Hall"),
        g(18, 0, "Clemson", 5, "New Mexico State", 12, "Clemson"),
        g(19, 0, "Auburn", 4, "College of Charleston", 13, "Auburn"),
        g(20, 0, "TCU", 6, "Syracuse", 11, "Syracuse"),
        g(21, 0, "Michigan State", 3, "Bucknell", 14, "Michigan State"),
        g(22, 0, "Rhode Island", 7, "Oklahoma", 10, "Rhode Island"),
        g(23, 0, "Duke", 2, "Iona", 15, "Duke"),
        # === WEST (1 Xavier) R64 ===
        g(24, 0, "Xavier", 1, "Texas Southern", 16, "Xavier"),
        g(25, 0, "Missouri", 8, "Florida State", 9, "Florida State"),
        g(26, 0, "Ohio State", 5, "South Dakota State", 12, "Ohio State"),
        g(27, 0, "Gonzaga", 4, "UNC Greensboro", 13, "Gonzaga"),
        g(28, 0, "Houston", 6, "San Diego State", 11, "Houston"),
        g(29, 0, "Michigan", 3, "Montana", 14, "Michigan"),
        g(30, 0, "Texas A&M", 7, "Providence", 10, "Texas A&M"),
        g(31, 0, "North Carolina", 2, "Lipscomb", 15, "North Carolina"),
        # === EAST R32 ===
        g(32, 1, "Villanova", 1, "Alabama", 9, "Villanova"),
        g(33, 1, "West Virginia", 5, "Marshall", 13, "West Virginia"),
        g(34, 1, "Florida", 6, "Texas Tech", 3, "Texas Tech"),
        g(35, 1, "Butler", 10, "Purdue", 2, "Purdue"),
        # === SOUTH R32 ===
        g(36, 1, "Maryland-Baltimore County", 16, "Kansas State", 9, "Kansas State"),
        g(37, 1, "Kentucky", 5, "Buffalo", 13, "Kentucky"),
        g(38, 1, "Loyola (IL)", 11, "Tennessee", 3, "Loyola (IL)"),
        g(39, 1, "Nevada", 7, "Cincinnati", 2, "Nevada"),
        # === MIDWEST R32 ===
        g(40, 1, "Kansas", 1, "Seton Hall", 8, "Kansas"),
        g(41, 1, "Clemson", 5, "Auburn", 4, "Clemson"),
        g(42, 1, "Syracuse", 11, "Michigan State", 3, "Syracuse"),
        g(43, 1, "Rhode Island", 7, "Duke", 2, "Duke"),
        # === WEST R32 ===
        g(44, 1, "Xavier", 1, "Florida State", 9, "Florida State"),
        g(45, 1, "Ohio State", 5, "Gonzaga", 4, "Gonzaga"),
        g(46, 1, "Houston", 6, "Michigan", 3, "Michigan"),
        g(47, 1, "Texas A&M", 7, "North Carolina", 2, "North Carolina"),
        # === EAST S16 ===
        g(48, 2, "Villanova", 1, "West Virginia", 5, "Villanova"),
        g(49, 2, "Texas Tech", 3, "Purdue", 2, "Texas Tech"),
        # === SOUTH S16 ===
        g(50, 2, "Kansas State", 9, "Kentucky", 5, "Kansas State"),
        g(51, 2, "Loyola (IL)", 11, "Nevada", 7, "Loyola (IL)"),
        # === MIDWEST S16 ===
        g(52, 2, "Kansas", 1, "Clemson", 5, "Kansas"),
        g(53, 2, "Syracuse", 11, "Duke", 2, "Duke"),
        # === WEST S16 ===
        g(54, 2, "Florida State", 9, "Gonzaga", 4, "Gonzaga"),
        g(55, 2, "Michigan", 3, "North Carolina", 2, "Michigan"),
        # === EAST E8 ===
        g(56, 3, "Villanova", 1, "Texas Tech", 3, "Villanova"),
        # === SOUTH E8 ===
        g(57, 3, "Kansas State", 9, "Loyola (IL)", 11, "Loyola (IL)"),
        # === MIDWEST E8 ===
        g(58, 3, "Kansas", 1, "Duke", 2, "Kansas"),
        # === WEST E8 ===
        g(59, 3, "Gonzaga", 4, "Michigan", 3, "Michigan"),
        # === FF ===
        g(60, 4, "Villanova", 1, "Kansas", 1, "Villanova"),
        g(61, 4, "Loyola (IL)", 11, "Michigan", 3, "Michigan"),
        # === NC ===
        g(62, 5, "Villanova", 1, "Michigan", 3, "Villanova"),
    ]
    return {"year": 2018, "games": games, "total_games": len(games)}


def make_2019():
    """2019: Virginia won championship (redemption after UMBC loss). Texas Tech runner-up."""
    games = [
        # === EAST (1 Duke) R64 ===
        g(0, 0, "Duke", 1, "North Dakota State", 16, "Duke"),
        g(1, 0, "Virginia Commonwealth", 8, "Central Florida", 9, "Central Florida"),
        g(2, 0, "Mississippi State", 5, "Liberty", 12, "Liberty"),
        g(3, 0, "Virginia Tech", 4, "Saint Louis", 13, "Virginia Tech"),
        g(4, 0, "Maryland", 6, "Belmont", 11, "Maryland"),
        g(5, 0, "Louisiana State", 3, "Yale", 14, "Louisiana State"),
        g(6, 0, "Louisville", 7, "Minnesota", 10, "Minnesota"),
        g(7, 0, "Michigan State", 2, "Bradley", 15, "Michigan State"),
        # === SOUTH (1 Virginia) R64 ===
        g(8, 0, "Virginia", 1, "Gardner-Webb", 16, "Virginia"),
        g(9, 0, "Mississippi", 8, "Oklahoma", 9, "Oklahoma"),
        g(10, 0, "Wisconsin", 5, "Oregon", 12, "Oregon"),
        g(11, 0, "Kansas State", 4, "UC Irvine", 13, "UC Irvine"),
        g(12, 0, "Villanova", 6, "Saint Mary's", 11, "Villanova"),
        g(13, 0, "Purdue", 3, "Old Dominion", 14, "Purdue"),
        g(14, 0, "Cincinnati", 7, "Iowa", 10, "Iowa"),
        g(15, 0, "Tennessee", 2, "Colgate", 15, "Tennessee"),
        # === MIDWEST (1 North Carolina) R64 ===
        g(16, 0, "North Carolina", 1, "Iona", 16, "North Carolina"),
        g(17, 0, "Utah State", 8, "Washington", 9, "Washington"),
        g(18, 0, "Auburn", 5, "New Mexico State", 12, "Auburn"),
        g(19, 0, "Kansas", 4, "Northeastern", 13, "Kansas"),
        g(20, 0, "Iowa State", 6, "Ohio State", 11, "Ohio State"),
        g(21, 0, "Houston", 3, "Georgia State", 14, "Houston"),
        g(22, 0, "Wofford", 7, "Seton Hall", 10, "Wofford"),
        g(23, 0, "Kentucky", 2, "Abilene Christian", 15, "Kentucky"),
        # === WEST (1 Gonzaga) R64 ===
        g(24, 0, "Gonzaga", 1, "FDU", 16, "Gonzaga"),
        g(25, 0, "Syracuse", 8, "Baylor", 9, "Baylor"),
        g(26, 0, "Marquette", 5, "Murray State", 12, "Murray State"),
        g(27, 0, "Florida State", 4, "Vermont", 13, "Florida State"),
        g(28, 0, "Buffalo", 6, "Arizona State", 11, "Buffalo"),
        g(29, 0, "Texas Tech", 3, "Northern Kentucky", 14, "Texas Tech"),
        g(30, 0, "Nevada", 7, "Florida", 10, "Florida"),
        g(31, 0, "Michigan", 2, "Montana", 15, "Michigan"),
        # === EAST R32 ===
        g(32, 1, "Duke", 1, "Central Florida", 9, "Duke"),
        g(33, 1, "Liberty", 12, "Virginia Tech", 4, "Virginia Tech"),
        g(34, 1, "Maryland", 6, "Louisiana State", 3, "Louisiana State"),
        g(35, 1, "Minnesota", 10, "Michigan State", 2, "Michigan State"),
        # === SOUTH R32 ===
        g(36, 1, "Virginia", 1, "Oklahoma", 9, "Virginia"),
        g(37, 1, "Oregon", 12, "UC Irvine", 13, "Oregon"),
        g(38, 1, "Villanova", 6, "Purdue", 3, "Purdue"),
        g(39, 1, "Iowa", 10, "Tennessee", 2, "Tennessee"),
        # === MIDWEST R32 ===
        g(40, 1, "North Carolina", 1, "Washington", 9, "North Carolina"),
        g(41, 1, "Auburn", 5, "Kansas", 4, "Auburn"),
        g(42, 1, "Ohio State", 11, "Houston", 3, "Houston"),
        g(43, 1, "Wofford", 7, "Kentucky", 2, "Kentucky"),
        # === WEST R32 ===
        g(44, 1, "Gonzaga", 1, "Baylor", 9, "Gonzaga"),
        g(45, 1, "Murray State", 12, "Florida State", 4, "Florida State"),
        g(46, 1, "Buffalo", 6, "Texas Tech", 3, "Texas Tech"),
        g(47, 1, "Florida", 10, "Michigan", 2, "Michigan"),
        # === EAST S16 ===
        g(48, 2, "Duke", 1, "Virginia Tech", 4, "Duke"),
        g(49, 2, "Louisiana State", 3, "Michigan State", 2, "Michigan State"),
        # === SOUTH S16 ===
        g(50, 2, "Virginia", 1, "Oregon", 12, "Virginia"),
        g(51, 2, "Purdue", 3, "Tennessee", 2, "Purdue"),
        # === MIDWEST S16 ===
        g(52, 2, "North Carolina", 1, "Auburn", 5, "Auburn"),
        g(53, 2, "Houston", 3, "Kentucky", 2, "Kentucky"),
        # === WEST S16 ===
        g(54, 2, "Gonzaga", 1, "Florida State", 4, "Gonzaga"),
        g(55, 2, "Texas Tech", 3, "Michigan", 2, "Texas Tech"),
        # === EAST E8 ===
        g(56, 3, "Duke", 1, "Michigan State", 2, "Michigan State"),
        # === SOUTH E8 ===
        g(57, 3, "Virginia", 1, "Purdue", 3, "Virginia"),
        # === MIDWEST E8 ===
        g(58, 3, "Auburn", 5, "Kentucky", 2, "Auburn"),
        # === WEST E8 ===
        g(59, 3, "Gonzaga", 1, "Texas Tech", 3, "Texas Tech"),
        # === FF ===
        g(60, 4, "Michigan State", 2, "Texas Tech", 3, "Texas Tech"),
        g(61, 4, "Virginia", 1, "Auburn", 5, "Virginia"),
        # === NC ===
        g(62, 5, "Virginia", 1, "Texas Tech", 3, "Virginia"),
    ]
    return {"year": 2019, "games": games, "total_games": len(games)}


def make_2021():
    """2021: Baylor won championship. Gonzaga undefeated until title game. UCLA 11-seed to FF."""
    games = [
        # === EAST (1 Michigan) R64 ===
        g(0, 0, "Michigan", 1, "Texas Southern", 16, "Michigan"),
        g(1, 0, "Louisiana State", 8, "St. Bonaventure", 9, "Louisiana State"),
        g(2, 0, "Colorado", 5, "Georgetown", 12, "Colorado"),
        g(3, 0, "Florida State", 4, "UNC Greensboro", 13, "Florida State"),
        g(4, 0, "Brigham Young", 6, "UCLA", 11, "UCLA"),
        g(5, 0, "Texas", 3, "Abilene Christian", 14, "Abilene Christian"),
        g(6, 0, "Connecticut", 7, "Maryland", 10, "Maryland"),
        g(7, 0, "Alabama", 2, "Iona", 15, "Alabama"),
        # === SOUTH (1 Baylor) R64 ===
        g(8, 0, "Baylor", 1, "Hartford", 16, "Baylor"),
        g(9, 0, "North Carolina", 8, "Wisconsin", 9, "Wisconsin"),
        g(10, 0, "Villanova", 5, "Winthrop", 12, "Villanova"),
        g(11, 0, "Purdue", 4, "North Texas", 13, "North Texas"),
        g(12, 0, "Texas Tech", 6, "Utah State", 11, "Texas Tech"),
        g(13, 0, "Arkansas", 3, "Colgate", 14, "Arkansas"),
        g(14, 0, "Florida", 7, "Virginia Tech", 10, "Florida"),
        g(15, 0, "Ohio State", 2, "Oral Roberts", 15, "Oral Roberts"),
        # === MIDWEST (1 Illinois) R64 ===
        g(16, 0, "Illinois", 1, "Drexel", 16, "Illinois"),
        g(17, 0, "Loyola (IL)", 8, "Georgia Tech", 9, "Loyola (IL)"),
        g(18, 0, "Tennessee", 5, "Oregon State", 12, "Oregon State"),
        g(19, 0, "Oklahoma State", 4, "Liberty", 13, "Oklahoma State"),
        g(20, 0, "San Diego State", 6, "Syracuse", 11, "Syracuse"),
        g(21, 0, "West Virginia", 3, "Morehead State", 14, "West Virginia"),
        g(22, 0, "Clemson", 7, "Rutgers", 10, "Rutgers"),
        g(23, 0, "Houston", 2, "Cleveland State", 15, "Houston"),
        # === WEST (1 Gonzaga) R64 ===
        g(24, 0, "Gonzaga", 1, "Norfolk State", 16, "Gonzaga"),
        g(25, 0, "Oklahoma", 8, "Missouri", 9, "Oklahoma"),
        g(26, 0, "Creighton", 5, "UC Santa Barbara", 12, "Creighton"),
        g(27, 0, "Virginia", 4, "Ohio", 13, "Ohio"),
        g(28, 0, "Southern California", 6, "Drake", 11, "Southern California"),
        g(29, 0, "Kansas", 3, "Eastern Washington", 14, "Kansas"),
        g(30, 0, "Oregon", 7, "Virginia Commonwealth", 10, "Oregon"),
        g(31, 0, "Iowa", 2, "Grand Canyon", 15, "Iowa"),
        # === EAST R32 ===
        g(32, 1, "Michigan", 1, "Louisiana State", 8, "Michigan"),
        g(33, 1, "Colorado", 5, "Florida State", 4, "Florida State"),
        g(34, 1, "UCLA", 11, "Abilene Christian", 14, "UCLA"),
        g(35, 1, "Maryland", 10, "Alabama", 2, "Alabama"),
        # === SOUTH R32 ===
        g(36, 1, "Baylor", 1, "Wisconsin", 9, "Baylor"),
        g(37, 1, "Villanova", 5, "North Texas", 13, "Villanova"),
        g(38, 1, "Texas Tech", 6, "Arkansas", 3, "Arkansas"),
        g(39, 1, "Florida", 7, "Oral Roberts", 15, "Oral Roberts"),
        # === MIDWEST R32 ===
        g(40, 1, "Illinois", 1, "Loyola (IL)", 8, "Loyola (IL)"),
        g(41, 1, "Oregon State", 12, "Oklahoma State", 4, "Oregon State"),
        g(42, 1, "Syracuse", 11, "West Virginia", 3, "Syracuse"),
        g(43, 1, "Rutgers", 10, "Houston", 2, "Houston"),
        # === WEST R32 ===
        g(44, 1, "Gonzaga", 1, "Oklahoma", 8, "Gonzaga"),
        g(45, 1, "Creighton", 5, "Ohio", 13, "Creighton"),
        g(46, 1, "Southern California", 6, "Kansas", 3, "Southern California"),
        g(47, 1, "Oregon", 7, "Iowa", 2, "Oregon"),
        # === EAST S16 ===
        g(48, 2, "Michigan", 1, "Florida State", 4, "Michigan"),
        g(49, 2, "UCLA", 11, "Alabama", 2, "UCLA"),
        # === SOUTH S16 ===
        g(50, 2, "Baylor", 1, "Villanova", 5, "Baylor"),
        g(51, 2, "Arkansas", 3, "Oral Roberts", 15, "Arkansas"),
        # === MIDWEST S16 ===
        g(52, 2, "Loyola (IL)", 8, "Oregon State", 12, "Oregon State"),
        g(53, 2, "Syracuse", 11, "Houston", 2, "Houston"),
        # === WEST S16 ===
        g(54, 2, "Gonzaga", 1, "Creighton", 5, "Gonzaga"),
        g(55, 2, "Southern California", 6, "Oregon", 7, "Southern California"),
        # === EAST E8 ===
        g(56, 3, "Michigan", 1, "UCLA", 11, "UCLA"),
        # === SOUTH E8 ===
        g(57, 3, "Baylor", 1, "Arkansas", 3, "Baylor"),
        # === MIDWEST E8 ===
        g(58, 3, "Oregon State", 12, "Houston", 2, "Houston"),
        # === WEST E8 ===
        g(59, 3, "Gonzaga", 1, "Southern California", 6, "Gonzaga"),
        # === FF ===
        g(60, 4, "UCLA", 11, "Gonzaga", 1, "Gonzaga"),
        g(61, 4, "Baylor", 1, "Houston", 2, "Baylor"),
        # === NC ===
        g(62, 5, "Gonzaga", 1, "Baylor", 1, "Baylor"),
    ]
    return {"year": 2021, "games": games, "total_games": len(games)}


def main():
    os.makedirs(BRACKETS_DIR, exist_ok=True)
    for year, maker in [(2018, make_2018), (2019, make_2019), (2021, make_2021)]:
        data = maker()
        assert len(data["games"]) == 63, f"{year}: expected 63 games, got {len(data['games'])}"
        path = os.path.join(BRACKETS_DIR, f"bracket_{year}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Wrote {path} ({len(data['games'])} games)")


if __name__ == "__main__":
    main()
