# BGG-Play-Dashboard
Pull your Boardgamegeek.com play data and visualize it.

![Example Dashboard](https://github.com/Dubya850/BGG-Play-Dashboard/blob/master/dashboard_example.PNG)

Run BGGGetData_plays.py to create a file with your play data:

`python BGGGetData_plays.py -u my_bgg_user_name`

Open "BGG Play Dashboard.twb" in tableau and point it to your new play_data.csv file.

[Tableau Public Dashboard](https://public.tableau.com/profile/michael8307#!/vizhome/BGGPlayDashboard/Dashboard1?publish=yes)

-Doesn't look great on mobile.

## Options
* `-u [str]`       BGG User Name
* `-pages [int]`   Number of pages of play data to pull (~100 plays = 3 pages). Defaults to 50.
* `-detail [bool]` Print detailed running info.
