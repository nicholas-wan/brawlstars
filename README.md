# Brawl Stars Club Statistics
This script obtains the information of all players in a Brawl Stars club given the Club Tag. 

# Installation
Create a virtual environment with Python==3.7. Install the Python library `brawlstats`
```
conda create -n brawlstars python==3.7
conda activate brawlstars
pip install brawlstats
```

# Usage

Insert your Brawl Stars Developer API Key after registering for an account at https://developer.brawlstars.com/ into `api_key.txt`
```
python get_brawlers.py
```
# Output
Outputs a CSV file of the all player statistics (of a particular club), alphabetically sorted by names (player columns), and alphabetically sorted within (brawlers_11) column.

```
+---+----------+-----------+----------+----------+-----------+-----------+------------------------+----------+
|   |  player  |    tag    | trophies | level_9s | level_10s | level_11s |      brawlers_11       |   date   |
+---+----------+-----------+----------+----------+-----------+-----------+------------------------+----------+
| 0 |  player1 | #12345678 |  31309   |    36    |    16     |     4     | BELLE, EMZ, GALE, TARA | 06/15/22 |
| 1 |  player2 | #23456789 |  19403   |    23    |     6     |     2     |       SPIKE, RICO      | 06/15/22 |
| 2 |  player3 | #34567890 |  25407   |    29    |     9     |     1     |          LEON          | 06/15/22 |
+---+----------+-----------+----------+----------+-----------+-----------+------------------------+----------+
```
