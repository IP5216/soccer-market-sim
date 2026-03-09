# Project Mercato: Soccer Transfer Market Simulator

## What is this?
Project Mercato is a Python-based simulation that looks at how soccer teams spend their money to build the best possible squad. Instead of just picking players randomly, I built "Agent Personalities" that use math to decide if a player is worth the price.

I wanted to see if a "Moneyball" team (buying value) could actually beat a "Global Giant" (buying superstars) over multiple seasons.

## How it Works (The Logic)
1. **The Auction Engine:** Every player is sold in a "Second-Price Auction." The winner pays a small premium over the second-highest bidder, mimicking how real negotiations work.
2. **Marginal Utility:** Teams don't just look at a player's skill. They look at how much that player improves their current average skill. If a team already has a great Goalkeeper, they won't bid high on another one.
3. **Strategic Personalities:** 
    - **WIN_NOW:** These teams will overpay for top-tier talent to get immediate results.
    - **REBUILD:** These teams focus on younger players with better long-term value.
4. **The Feedback Loop:** After the transfer window, teams play a "season." The higher they finish, the more prize money they get for next year’s window.
5. **Aging & Retirement:** Players get older every season. Once they hit 35, they retire, forcing teams to constantly update their strategy.

## Tech Used
- **Python**: Core logic and simulation.
- **CSV**: Data storage for all transfer history.
- **Math/Statistics**: Used Gaussian distributions for player generation and non-linear decay for aging.

## What I Learned
Building this showed me that a "perfect" player isn't always a good investment. If a superstar costs 90% of your budget, you might fail to field a full team, causing your "Team Strength" to drop. The best teams are usually the most balanced ones.