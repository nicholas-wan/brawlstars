# Brawl Stars Club Statistics
This script obtains the information of players or clubs given the respective tag.

# Installation
Create a virtual environment with Python==3.7. Install the Python library `brawlstats`. Run each line individually.
```
conda create -n brawlstars python==3.7
conda activate brawlstars
pip install brawlstats tqdm pandas tabulate pandasql xlsxwriter selenium IPython imgkit pillow undetected_chromedriver Jinja2 seaborn
```

# Scripts

## main.py 
Pulls club level data from Brawl Stars API to create the following 3 files.
1. /output/c6aurac_brawler_levels.csv
2. /output/c9aurac_brawler_levels.csv
3. /output/comparison.py

## aura.py
Formats c6 and c9 team statistics by combining with team numbers from google sheets. Also creates team average level statistics. Run `main.py` before running this file. Outputs the following 4 files.

1. /output/c6_team_averages.csv
2. /output/c9_team_averages.csv
3. /output/c6_aurac_brawler_levels.xlsx
4. /output/c9_aurac_brawler_levels.xlsx

## maps/best_brawlers.py
Uses selenium to web scrape brawlify website to generate infographics. Has 2 important parameters.
```
-- refresh_maps (yes/no)
# Used to generate list of map urls in `maps/maps.csv`. Needed whenever power league maps change. If not working, check if brawlify website https://brawlify.com/league/ is correctly showing the maps.

-- refresh_stats (yes/no)
# Visits each of the map urls in `maps/maps.csv` to download the latest win rate data. Will refresh by default when running this script
```

Outputs infographics in `/maps/infographics`



# Usage

Insert your Brawl Stars Developer API Key after registering for an account at https://developer.brawlstars.com/ into `api_key.txt`

There are 2 forms of usage, player & club tag. Key in the tag as an argument, seperated by space and the code will automatically detect if it is a club or player. 
Hashtag before the tags (#) is not necessary but will be accepted.

A mix of player and club tags can be accepted as well, but players and clubs can share the same tag. Priority would be checking for clubs.

## 1. Player Tag example
```
# Input Player tags with the -t argument, with a space in between tags. More than 1 player tag can be accepted. 
# e.g python main.py -t PLAYERTAG1 PLAYERTAG2 PLAYERTAG3

>>> python main.py -t 2YQUPUYJ C9LR0R0V
+---+----------+----------+----------+----------+-----------+-----------+-----------------------------------------------------------+
|   |  player  |   tag    | trophies | level_9s | level_10s | level_11s |                        brawlers_11                        |
+---+----------+----------+----------+----------+-----------+-----------+-----------------------------------------------------------+
| 0 | ZSilverZ | 2YQUPUYJ |  33791   |    32    |    14     |     8     | ASH, BELLE, BROCK, COLONEL RUFFS, EVE, GENE, SPIKE, SURGE |
| 1 |   Blue   | C9LR0R0V |  30558   |    44    |     6     |     4     |                 BYRON, CROW, SANDY, SPIKE                 |
+---+----------+----------+----------+----------+-----------+-----------+-----------------------------------------------------------+

# CSV saved to ./output/players.csv

```
## 2. Club Tag Example

```
# Input Club tags with the -t argument, with a space in between tags. More than 1 club tag can be accepted. 
# e.g python main.py -t CLUBTAG1 CLUBTAG2 CLUBTAG3 -s
 
>>> python -i main.py -t 202VGURG0 90JC22UQ 2GGGLQC98 2LUJ0G99U 2GRU08QGL P0Q9LPL0 2GV20JCPV 2R020C0VL 20J9LRP0V 
+---+-----------------+-----------+----------------+-------------+--------------+-------------------+--------------------+--------------------+
|   |      Club       | Club Tag  | Total Trophies | Num Members | Avg Trophies | Avg 9s per member | Avg 10s per member | Avg 11s per member |
+---+-----------------+-----------+----------------+-------------+--------------+-------------------+--------------------+--------------------+
| 2 |  HONRA BRAWL    | 2GGGLQC98 |     934421     |     30      |    31147     |       33.7        |        9.8         |        2.7         |
| 8 | BlackSoldiers🥷  | 20J9LRP0V |     926136     |     30      |    30871     |       27.2        |        9.1         |        3.0         |
| 4 | Club House Star | 2GRU08QGL |     919603     |     30      |    30653     |       36.7        |        10.6        |        2.8         |
| 0 |  Mage Knights   | 202VGURG0 |     833472     |     30      |    27782     |       27.7        |        10.3        |        4.6         |
| 3 |      Axiom      | 2LUJ0G99U |     829977     |     30      |    27665     |       29.6        |        6.0         |        2.0         |
| 6 |  Brawl Club l   | 2GV20JCPV |     820675     |     30      |    27355     |       31.4        |        6.3         |        1.7         |
| 7 |  BR|VeteranoS   | 2R020C0VL |     701606     |     27      |    25985     |       24.1        |        5.2         |        2.2         |
| 5 |     DuocUC      | P0Q9LPL0  |     698777     |     30      |    23292     |       31.2        |        6.0         |        1.6         |
| 1 | Mage Knights 2  | 90JC22UQ  |     607951     |     30      |    20265     |       15.5        |        3.2         |        2.4         |
+---+-----------------+-----------+----------------+-------------+--------------+-------------------+--------------------+--------------------+

# CSV file saved to ./output/comparison.csv

```

## 3. Getting Brawler Levels of all players in a specific Club
Use the -s argument, with clubs seperated by space

```
# e.g python main.py -t CLUBTAG1 CLUBTAG2 CLUBTAG3 -s CLUBTAG 1
# Generates comparison statistics for the 3 clubs, but only saves the brawler levels for the first club to CSV

>>> python -i main.py -t 202VGURG0 90JC22UQ -s 202VGURG0

# A CSV of this format will be generated in the output folder, but will not be printed
+---+----------+-----------+----------+----------+-----------+-----------+------------------------+----------+
|   |  player  |    tag    | trophies | level_9s | level_10s | level_11s |      brawlers_11       |   date   |
+---+----------+-----------+----------+----------+-----------+-----------+------------------------+----------+
| 0 |  player1 | #12345678 |  31309   |    36    |    16     |     4     | BELLE, EMZ, GALE, TARA | 06/15/22 |
| 1 |  player2 | #23456789 |  19403   |    23    |     6     |     2     |       SPIKE, RICO      | 06/15/22 |
| 2 |  player3 | #34567890 |  25407   |    29    |     9     |     1     |          LEON          | 06/15/22 |
+---+----------+-----------+----------+----------+-----------+-----------+------------------------+----------+

# CSV file saved to ./output/<CLUB_NAME>_brawler_levels.csv

```
