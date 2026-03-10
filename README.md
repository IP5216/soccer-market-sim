# Soccer Market Efficiency Simulation

## What is this?
This project is a Python simulation that tests different economic strategies in a professional sports market. I wanted to see if "Moneyball" (buying undervalued potential) can actually beat "Win Now" teams (buying expensive current stars) over a 5-year period.

## How it Works
The simulation runs through 5 seasons. Each year, teams must navigate two main phases:
1. **The Transfer Window:** 150 new players are generated. Teams bid based on their specific strategy and budget constraints.
2. **The League Season:** Teams compete based on their squad strength. I've added a **Variance Factor** so that the best team doesn't always win, allowing for "underdog" stories.

## Key Logic & Features

### 1. The Moneyball Logic (Potential vs. Skill)
I realized that just buying "good" players isn't realistic. Now, every player has a **Potential** rating. 
* **Rebuilding Teams:** Focus 70% of their valuation on a player's potential. They are willing to pay a premium for a 19-year-old who *will* be a star.
* **Win-Now Teams:** Focus on current skill. They want the 28-year-old who is at his peak today.

### 2. Player Aging & Realistic Decline
Players no longer stay at the same skill level until they retire. 
* **Youth Growth:** Players under 25 gain skill points every season as they train.
* **Veteran Decline:** Once a player hits 30, they lose 1–3 skill points per year. This creates "Market Churn," forcing teams to constantly look for replacements before their stars become useless.

### 3. Desperation Budgeting
In the real world, if a team finishes in last place, the owners get desperate. 
* If a team finishes in the bottom of the league, their **Max Bid Percentage** increases from 40% to 60%. 
* This forces struggling teams to stop hoarding cash and actually spend money to save their season.

### 4. Performance Variance
To prevent the simulation from being too predictable, I increased the performance randomness to **±6**. This means a team with an average skill of 75 can actually lose to a team with a 70 if they have a "bad day" or the smaller team has a "miracle season."

## How to Run
Run `python mercato-sim.py` to see the results of the 5-year simulation. The data will export to `season_summary.csv` for analysis.