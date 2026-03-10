What is this?
This project is a Python-based economic simulation that tests how different soccer teams spend their money over 5 years. I wanted to see if teams that spend hundreds of millions on superstars actually perform better than "Moneyball" teams that use data to find cheap, young talent.

How it Works
The simulation runs 5 full seasons. Each season has two main parts:

** The Transfer Window (The Auction):** 150 new players are generated with different skills and ages. Teams bid against each other to sign them.

** The League Season:** Teams play games based on their "Squad Strength." The better the players, the higher the team finishes in the ranks.

The Rules (The Logic)
To make the simulation realistic, I programmed in several "constraints" (rules the computer must follow):

The 1-4-3-3 Rule: Every team is required to have at least 1 Goalkeeper, 4 Defenders, 3 Midfielders, and 3 Strikers. If they don't meet this requirement, they "forfeit" and finish in last place.

Aging & Retirement: Players get older every year. Once a player hits age 35, they retire and disappear from the team’s roster. Teams have to constantly buy new players to replace the old ones.

Smart Bidding: Teams won't just spend all their money on one person. If they have fewer than 11 players, they are limited to spending only 25% of their budget at a time so they don't go bankrupt before filling their roster.

The Teams
I created four teams with different "personalities" (strategies):

Global Giants ($800M): The richest team. They try to buy the best players right now, regardless of age.

London Blue ($600M): A wealthy team that also focuses on winning immediately.

Ajax-Style Academy ($200M): A poorer team that focuses on "Rebuilding." They prefer young players who will get better over time.

Moneyball FC ($150M): The underdog. They use a strict value-based strategy to find the most "skill per dollar."

Data & Results
The simulation generates two CSV files that can be opened in Excel or Google Sheets:

transfer_data.csv: A receipt of every single player bought, who bought them, and how much they paid.

season_summary.csv: A leaderboard showing where each team finished each year, their average team skill, and how much money they had left.

What I’m looking for in the graphs:
Can money buy happiness? Does the team with the $800M budget always finish #1?

The Rebuild Success: Does "Moneyball FC" start in 4th place in Season 1 but climb to 1st place by Season 5 once their young players grow up?

The Bankruptcy Risk: Do any teams run out of money and fail to field 11 players?

How to Run It
Make sure you have Python installed.

Download mercato-sim.py.

Run the script in your terminal: python mercato-sim.py.

Open the .csv files to see the results of the 5-year experiment!