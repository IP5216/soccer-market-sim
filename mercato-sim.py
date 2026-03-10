import random
import csv
import os

class Player:
    def __init__(self, name, skill, age, position):
        self.name = name
        self.skill = skill
        self.age = age
        self.position = position
        # AGENT FLOOR: Scaled exponentially (Skill^2.8 * 50)
        # Prevents elite players from being bought for "thousands"
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
        # FIX: Pre-seed teams so they always meet the 1-4-3-3 requirement
        self._generate_initial_squad(start_skill)

    def _generate_initial_squad(self, avg_skill):
        """Creates the starting 11 players based on team tier."""
        for pos, count in self.targets.items():
            for i in range(count):
                # Starters are slightly older to encourage teams to buy youth later
                skill = int(random.gauss(avg_skill, 4))
                p = Player(f"{self.name}_Starter_{pos}_{i}", skill, random.randint(24, 30), pos)
                self.roster.append(p)

    def sell_players(self):
        """Strategic selling: Recoup budget while maintaining roster cap."""
        sold_count = 0
        recouped = 0
        
        # 1. Sell worst players if over 28-man cap
        self.roster.sort(key=lambda x: x.skill)
        while len(self.roster) > self.roster_cap:
            p = self.roster.pop(0)
            sale_price = p.market_value * 0.5 # 50% resale value
            self.budget += sale_price
            recouped += sale_price
            sold_count += 1
            
        # 2. Sell veterans over 33 to make room for youth
        kept_roster = []
        for p in self.roster:
            if p.age > 33 and len(self.roster) > 15: # Don't sell if squad is too thin
                sale_price = p.market_value * 0.4
                self.budget += sale_price
                recouped += sale_price
                sold_count += 1
            else:
                kept_roster.append(p)
        self.roster = kept_roster
        return sold_count, recouped

    def get_hunger_multiplier(self, position):
        if len(self.roster) >= self.roster_cap:
            return 0
        current_count = len([p for p in self.roster if p.position == position])
        target_count = self.targets.get(position, 0)
        
        # If we are below the 1-4-3-3 threshold, we are desperate
        if current_count < target_count:
            return 2.5
        # If we have the starters, we bid lower for depth/backups
        return 0.4

    def calculate_internal_valuation(self, player, scarcity_mid):
        if len(self.roster) >= self.roster_cap: return 0

        # UPGRADE LOGIC: Find current best in that position
        pos_players = [p.skill for p in self.roster if p.position == player.position]
        current_best = max(pos_players) if pos_players else 50
        
        # Only pay for a significant improvement or depth
        improvement = max(0.5, player.skill - (current_best - 3))
        
        # Satisfaction factor: The higher our quality, the less we pay for marginal gains
        satisfaction = max(0.1, (100 - current_best) / 50)

        if self.strategy == "WIN_NOW":
            utility = improvement * 1.5
        else:
            # Rebuild strategy favors youth
            age_factor = max(0.5, (35 - player.age) / 10)
            utility = improvement * age_factor

        hunger = self.get_hunger_multiplier(player.position)
        
        # Bid multiplier (12M to account for 'improvement' being a smaller delta than 'skill')
        valuation = utility * 12_000_000 * scarcity_mid * hunger * satisfaction
        
        # Cap bid at 40% of current budget to prevent instant bankruptcy
        return min(valuation, self.budget * 0.4)

class League:
    def __init__(self, teams):
        self.teams = teams

    def calculate_team_strength(self, team):
        # Calculate strength based on top 11 players
        team.roster.sort(key=lambda x: x.skill, reverse=True)
        top_11 = team.roster[:11]
        
        # Re-check 1-4-3-3 legality for safety
        counts = {"GK": 0, "DEF": 0, "MID": 0, "ST": 0}
        for p in team.roster: counts[p.position] += 1
        
        is_legal = (counts["GK"] >= 1 and counts["DEF"] >= 4 and 
                    counts["MID"] >= 3 and counts["ST"] >= 3)
        
        if not is_legal: return 10.0 # Massive penalty for failing formation
            
        return sum(p.skill for p in top_11) / 11

    def run_season(self):
        standings = []
        for team in self.teams:
            strength = self.calculate_team_strength(team)
            # Performance includes a "luck" factor
            performance = strength + random.uniform(-2, 2)
            standings.append((team, performance))
        standings.sort(key=lambda x: x[1], reverse=True)
        return standings

    def distribute_rewards(self, standings):
        prize_pool = [100_000_000, 75_000_000, 50_000_000, 25_000_000]
        for i, (team, performance) in enumerate(standings):
            reward = prize_pool[i] if i < 4 else 10_000_000
            team.budget += reward
            print(f"{team.name} finished #{i+1} (Strength: {performance:.1f}) and earned ${reward:,}")

def run_auction(player, teams, market, season_num):
    scarcity_mid = market.get_scarcity_multiplier(player.position)
    bids = []
    for team in teams:
        val = team.calculate_internal_valuation(player, scarcity_mid)
        # Teams refuse to bid below the Player's Market Floor
        if val >= player.market_value:
            bids.append((val, team))

    if not bids: return None
    
    bids.sort(key=lambda x: x[0], reverse=True)
    winner_val, winner_team = bids[0]
    
    # Second-price auction style but with a hard Market Floor
    runner_up_val = bids[1][0] if len(bids) > 1 else player.market_value
    final_price = max(player.market_value, runner_up_val)

    if final_price <= winner_team.budget:
        winner_team.budget -= final_price
        winner_team.roster.append(player)
        return {
            "season": season_num, "player_name": player.name, "skill": player.skill, 
            "position": player.position, "buyer": winner_team.name, "price": round(final_price, 2)
        }
    return None

def generate_random_players(count, season):
    players = []
    names = ["Silva", "Müller", "Jones", "Mbappe", "Kane", "Rossi", "Zhang", "Hernandez", "Bellingham", "Musiala"]
    for i in range(count):
        players.append(Player(f"{random.choice(names)}_{season}_{i}", 
                              max(60, min(99, int(random.gauss(75, 8)))), 
                              random.randint(18, 32), 
                              random.choice(["ST", "MID", "DEF", "GK"])))
    return players

if __name__ == "__main__":
    # Initialize teams with starting squads based on their tier
    clubs = [
        Team("Global Giants", 400_000_000, "WIN_NOW", 78),   # Top tier
        Team("London Blue", 300_000_000, "WIN_NOW", 75),    # High tier
        Team("Ajax Academy", 150_000_000, "REBUILD", 70),   # Mid tier
        Team("Moneyball FC", 100_000_000, "REBUILD", 65)    # Underdog
    ]
    
    all_transfers = []
    summary_data = []
    league = League(clubs)

    for season in range(1, 6):
        print(f"\n--- SEASON {season} ---")
        
        # 1. Aging & Selling
        for team in clubs:
            sold, cash = team.sell_players()
            if sold > 0: print(f"{team.name} sold {sold} players, recouped ${cash:,.0f}")
            
            # Age players and retire them at 35
            team.roster = [p for p in team.roster if (p.age + 1) < 35]
            for p in team.roster: p.age += 1

        # 2. Market Phase
        market_players = generate_random_players(100, season)
        market = Market(market_players)
        market_players.sort(key=lambda x: x.skill, reverse=True)

        for p in market_players:
            t = run_auction(p, clubs, market, season)
            if t: all_transfers.append(t)

        # 3. Season Simulation
        results = league.run_season()
        for rank, (team, perf) in enumerate(results, 1):
            summary_data.append({
                "Season": season, "Team": team.name, "Rank": rank,
                "Avg_Skill": round(perf, 1), "Budget": round(team.budget, 0),
                "Squad_Size": len(team.roster)
            })
        league.distribute_rewards(results)

    # 4. Save results
    with open('transfer_data.csv', 'w', newline='') as f:
        dw = csv.DictWriter(f, fieldnames=all_transfers[0].keys())
        dw.writeheader()
        dw.writerows(all_transfers)
        
    with open('season_summary.csv', 'w', newline='') as f:
        dw = csv.DictWriter(f, fieldnames=summary_data[0].keys())
        dw.writeheader()
        dw.writerows(summary_data)

    print("\nSimulation complete. Outputs saved to CSV.")