@ECHO OFF 
TITLE Execute python script on anaconda environment
ECHO Please Wait...
:: Section 1: Activate the environment.
ECHO ============================
ECHO Conda Activate
ECHO ============================
@CALL "C:\Users\nicho\anaconda3\Scripts\activate.bat" brawlstars
:: Section 2: Execute python script.
ECHO ============================
ECHO Python top_pl_players.py
ECHO ============================
python C:\Users\nicho\OneDrive\Desktop\brawlstars\top_pl_players.py >> C:\Users\nicho\OneDrive\Desktop\brawlstars\logs\top_pl_players.txt
python C:\Users\nicho\OneDrive\Desktop\brawlstars\generate_infographics_pro.py >> C:\Users\nicho\OneDrive\Desktop\brawlstars\logs\generate_infographics_pro.txt

ECHO ============================
ECHO End
ECHO ============================

PAUSE