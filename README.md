# cricket
Get live cricket scores for the Australian mens cricket team and display in menubar using [SwiftBar](https://github.com/swiftbar/SwiftBar)

It consists of two python programs, *cricket.py* which displays the live results  and the helper *find_match.py* which finds which matches are live or upcoming. *find_match.py* creates a *.cricket.config* file but generates no other output, so it can be run infrequently (*e.g.* once an hour) by [SwiftBar](https://github.com/swiftbar/SwiftBar) and it won't create its own menubar item. Alternatively cron could be used to run it on a fixed schedule.

Other cricket teams can be displayed instead by changing the *my_team* constant in *find_match.py* e.g. SA, BAN, PAK 
