import random
import csv
import os

class Player:
    def __init__(self, name, skill, age, position):
        self.name = name
        self.skill = skill
        self.age = age
        self.position = position
        # Potential allows for long-term "Moneyball" growth
        self.potential = skill + random.randint(5, 15)
        # Exponential market value scaling
        self.market_value = (self.skill ** 2.8) * 50

class Market:
    def __init__(self, players):
        self.players = players
        self.position_counts = self._count_positions()

    def _count_positions(self):
        counts = {"ST": 0, "MID": 0, "DEF": 0, "GK": 0}
        for p in self.players:
            counts[p.position] += 1
        return counts

    def get_scarcity_multiplier(self, position):
        count = self.position_counts.get(position, 1)
        if count <= 1: return 1.5
        if count <= 3: return 1.2
        return 1.0

class Team:
    def __init__(self, name, budget, strategy, start_skill):
        self.name = name
        self.budget = budget
        self.strategy = strategy
        self.roster = []
        self.targets = {"GK": 1, "DEF": 4, "MID": 3, "ST": 3}
        self.roster_cap = 28
        self.last_season_rank = 1 
        self._generate_initial_squad(start_skill)

    def _generate_initial_squad(self, avg_skill):
        for pos, count in self.targets.items():
            for i in range(count):
                skill = int(random.gauss(avg_skill, 4))
                p = Player(f"{self.name}_Starter_{pos}_{i}", skill, random.randint(22, 30), pos)
                self.roster.append(p)

    def develop_players(self):
        """Handles youth growth and veteran decline."""
        for p in self.roster:
            p.age += 1
            if p.age < 25 and p.skill < p.potential:
                p.skill += random.randint(1, 3)
            elif p.age > 30:
                p.skill -= random.randint(1, 3)
            p.skill = max(10, min(99, p.skill))

    def sell_players(self):
        """FIX: Improved logic to protect top stars and maintain squad depth."""
        sold_count = 0
        recouped = 0
        
        # Sort LOWEST to HIGHEST skill so we cut the worst players first
        self.roster.sort(key=lambda x: x.skill)
        
        # Cut worst players only if over the cap
        while len(self.roster) > self.roster_cap:
            p = self.roster.pop(0) # Remove lowest skill
            sale_price = p.market_value * 0.5
            self.budget += sale_price
            recouped += sale_price
            sold_count += 1
            
        kept_roster = []
        for p in self.roster:
            # Retire players at 35 (no value) or sell aging vets if we have depth
            if p.age >= 35:
                sold_count += 1 
            elif p.age > 32 and len(self.roster) > 18: # Only sell vets if squad is deep
                sale_price = p.market_value * 0.3
                self.budget += sale_price
                recouped += sale_price
                sold_count += 1
            else:
                kept_roster.append(p)
        self.roster = kept_roster
        return sold_count, recouped

    def calculate_internal_valuation(self, player, scarcity_mid):
        if len(self.roster) >= self.roster_cap: return 0

        pos_players = [p.skill for p in self.roster if p.position == player.position]
        current_best = max(pos_players) if pos_players else 50
        
        # Moneyball logic: REBUILD strategy values potential
        if self.strategy == "REBUILD":
            valuation_score = (player.potential * 0.7) + (player.skill * 0.3)
        else:
            valuation_score = player.skill

        improvement = max(0.5, valuation_score - (current_best - 3))
        satisfaction = max(0.1, (100 - current_best) / 50)
        
        # Desperation: Last place gets a bid boost (55% vs 35%)
        max_bid_pct = 0.55 if self.last_season_rank >= 4 else 0.35
        
        valuation = improvement * 12_000_000 * scarcity_mid * satisfaction
        return min(valuation, self.budget * max_bid_pct)

class League:
    def __init__(self, teams):
        self.teams = teams

    def run_season(self):
        standings = []
        for team in self.teams:
            team.roster.sort(key=lambda x: x.skill, reverse=True)
            # Performance is based on the top 11 players
            avg_skill = sum(p.skill for p in team.roster[:11]) / 11
            
            # FIX: Tightened variance (±3.5) so skill matters more than pure luck
            performance = avg_skill + random.uniform(-3.5, 3.5)
            standings.append((team, performance))
        
        standings.sort(key=lambda x: x[1], reverse=True)
        
        for i, (team, perf) in enumerate(standings):
            team.last_season_rank = i + 1
            
        return standings

    def distribute_rewards(self, standings):
        prize_pool = [120_000_000, 80_000_000, 40_000_000, 10_000_000]
        for i, (team, performance) in enumerate(standings):
            reward = prize_pool[i] if i < 4 else 5_000_000
            team.budget += reward
            print(f"{team.name} Rank #{i+1} | Skill: {performance:.1f} | Budget: ${team.budget/1_000_000:,.0f}M")

def run_auction(player, teams, market, season_num):
    scarcity_mid = market.get_scarcity_multiplier(player.position)
    bids = []
    for team in teams:
        val = team.calculate_internal_valuation(player, scarcity_mid)
        if val >= player.market_value:
            bids.append((val, team))

    if not bids: return None
    
    bids.sort(key=lambda x: x[0], reverse=True)
    winner_val, winner_team = bids[0]
    
    runner_up_val = bids[1][0] if len(bids) > 1 else player.market_value
    final_price = max(player.market_value, runner_up_val)

    if final_price <= winner_team.budget:
        winner_team.budget -= final_price
        winner_team.roster.append(player)
        return {
            "season": season_num, "player_name": player.name, "skill": player.skill, 
            "potential": player.potential, "buyer": winner_team.name, "price": round(final_price, 2)
        }
    return None

def generate_random_players(count, season):
    players = []
    names = ["Silva", "Müller", "Jones", "Mbappe", "Kane", "Rossi", "Zhang", "Hernandez", "Bellingham", "Musiala"]
    for i in range(count):
        players.append(Player(f"{random.choice(names)}_{season}_{i}", 
                              max(60, min(99, int(random.gauss(74, 7)))), 
                              random.randint(18, 31), 
                              random.choice(["ST", "MID", "DEF", "GK"])))
    return players

if __name__ == "__main__":
    clubs = [
        Team("Global Giants", 500_000_000, "WIN_NOW", 80),
        Team("London Blue", 350_000_000, "WIN_NOW", 76),
        Team("Ajax Academy", 200_000_000, "REBUILD", 72),
        Team("Moneyball FC", 120_000_000, "REBUILD", 68)
    ]
    
    summary_data = []
    league = League(clubs)

    for season in range(1, 6):
        print(f"\n--- SEASON {season} ---")
        for team in clubs:
            sold, cash = team.sell_players()
            team.develop_players()

        market_players = generate_random_players(100, season)
        market = Market(market_players)
        market_players.sort(key=lambda x: x.skill, reverse=True)

        for p in market_players:
            run_auction(p, clubs, market, season)

        results = league.run_season()
        for rank, (team, perf) in enumerate(results, 1):
            summary_data.append({
                "Season": season, "Team": team.name, "Rank": rank,
                "Avg_Skill": round(perf, 1), "Budget": round(team.budget, 0)
            })
        league.distribute_rewards(results)

    print("\nSimulation complete. Review 'season_summary.csv' for the final trajectory.")