import random
import csv
import os

class Player:
    def __init__(self, name, skill, age, position):
        self.name = name
        self.skill = skill 
        self.age = age
        self.position = position 
        self.base_value = (self.skill * (35 - self.age)) * 50000

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
    def __init__(self, name, budget, strategy):
        self.name = name
        self.budget = budget
        self.strategy = strategy 
        self.roster = []
        self.squad_quality = {"ST": 60.0, "MID": 60.0, "DEF": 60.0, "GK": 60.0}
        self.targets = {"GK": 1, "DEF": 4, "MID": 3, "ST": 3}
        self.roster_cap = 28

    def sell_players(self):
        """Strategic selling to manage roster cap and aging players."""
        sold_count = 0
        recouped = 0
        
        # 1. Sell if over cap (Sell weakest first)
        self.roster.sort(key=lambda x: x.skill)
        while len(self.roster) > self.roster_cap:
            p = self.roster.pop(0)
            sale_price = p.base_value * 0.6
            self.budget += sale_price
            recouped += sale_price
            sold_count += 1
            
        # 2. Sell veterans (over 33) to make room for youth
        kept_roster = []
        for p in self.roster:
            if p.age > 33 and len(self.roster) > 15:
                sale_price = p.base_value * 0.4
                self.budget += sale_price
                recouped += sale_price
                sold_count += 1
            else:
                kept_roster.append(p)
        self.roster = kept_roster
        return sold_count, recouped

    def get_hunger_multiplier(self, position):
        if len(self.roster) >= self.roster_cap:
            return 0 # Full squad, no more buying

        current_count = len([p for p in self.roster if p.position == position])
        target_count = self.targets.get(position, 0)

        if current_count == 0: return 2.5
        if current_count < target_count: return 1.5
        return 0.3 ** (current_count - target_count + 1)

    def update_squad_quality(self):
        for pos in self.squad_quality:
            pos_players = [p.skill for p in self.roster if p.position == pos]
            if pos_players:
                self.squad_quality[pos] = sum(pos_players) / len(pos_players)

    def calculate_internal_valuation(self, player, scarcity_mid):
        if len(self.roster) >= self.roster_cap: return 0

        # Pacing: Limit spend per player based on roster size
        max_spend_ratio = 0.20 if len(self.roster) < 11 else 0.5
        max_bid = self.budget * max_spend_ratio

        pos_count = len([p for p in self.roster if p.position == player.position])
        baseline = self.squad_quality.get(player.position, 60) if pos_count > 0 else 40.0
        marginal_gain = max(1.0, player.skill - baseline)
        
        if self.strategy == "WIN_NOW":
            utility_score = marginal_gain * 1.5 
        else:
            age_factor = max(0.1, (35 - player.age) / 15)
            utility_score = marginal_gain * age_factor

        hunger_mid = self.get_hunger_multiplier(player.position)
        valuation = utility_score * 2_000_000 * scarcity_mid * hunger_mid
        return min(valuation, max_bid)
    
class League:
    def __init__(self, teams):
        self.teams = teams

    def calculate_team_strength(self, team):
        counts = {"GK": 0, "DEF": 0, "MID": 0, "ST": 0}
        for p in team.roster:
            counts[p.position] += 1
        
        is_legal = (counts["GK"] >= 1 and counts["DEF"] >= 4 and 
                    counts["MID"] >= 3 and counts["ST"] >= 3)
        
        if not is_legal: return 10.0
            
        # Strength is average of top 11
        team.roster.sort(key=lambda x: x.skill, reverse=True)
        top_11 = team.roster[:11]
        return sum(p.skill for p in top_11) / 11

    def run_season(self):
        standings = []
        for team in self.teams:
            strength = self.calculate_team_strength(team)
            performance = strength + random.uniform(-3, 3)
            standings.append((team, performance))
        standings.sort(key=lambda x: x[1], reverse=True)
        return standings

    def distribute_rewards(self, standings):
        prize_pool = [100_000_000, 75_000_000, 50_000_000, 25_000_000]
        for i, (team, performance) in enumerate(standings):
            reward = prize_pool[i] if i < len(prize_pool) else 10_000_000
            team.budget += reward
            print(f"{team.name} finished #{i+1} and earned ${reward:,}")

def run_auction(player, teams, market, season_num):
    scarcity_mid = market.get_scarcity_multiplier(player.position)
    bids = []
    for team in teams:
        max_val = team.calculate_internal_valuation(player, scarcity_mid)
        if max_val > 0: bids.append((max_val, team))

    if not bids: return None
    bids.sort(key=lambda x: x[0], reverse=True)
    winner_val, winner_team = bids[0]
    
    reserve_price = player.base_value * 0.5
    runner_up_val = bids[1][0] if len(bids) > 1 else reserve_price
    final_price = min(winner_val, max(reserve_price, runner_up_val))

    if final_price <= winner_team.budget and final_price > 0:
        winner_team.budget -= final_price
        winner_team.roster.append(player)
        winner_team.update_squad_quality()
        return {
            "season": season_num, "player_name": player.name, "skill": player.skill, 
            "position": player.position, "buyer": winner_team.name, "price": round(final_price, 2)
        }
    return None

def generate_random_players(count):
    players = []
    positions = ["ST", "MID", "DEF", "GK"]
    names = ["Silva", "Müller", "Jones", "Mbappe", "Kane", "Rossi", "Zhang", "Hernandez"]
    for _ in range(count):
        players.append(Player(f"{random.choice(names)} {random.randint(100, 999)}", 
                              max(60, min(99, int(random.gauss(75, 8)))), 
                              random.randint(18, 33), random.choice(positions)))
    return players

if __name__ == "__main__":
    clubs = [
        Team("Global Giants", 400_000_000, "WIN_NOW"),
        Team("London Blue", 300_000_000, "WIN_NOW"),
        Team("Ajax-Style Academy", 150_000_000, "REBUILD"),
        Team("Moneyball FC", 100_000_000, "REBUILD")
    ]
    all_transfers = []
    summary = []
    league = League(clubs)

    for season in range(1, 6):
        print(f"\n--- SEASON {season} ---")
        for team in clubs:
            sold, recouped = team.sell_players()
            if sold > 0:
                print(f"{team.name} sold {sold} players for ${recouped:,.0f}")
            team.roster = [p for p in team.roster if (p.age + 1) < 35]
            for p in team.roster: p.age += 1
            team.update_squad_quality()

        all_players = generate_random_players(100)
        market = Market(all_players)
        all_players.sort(key=lambda x: x.skill, reverse=True)

        for p in all_players:
            t = run_auction(p, clubs, market, season)
            if t: all_transfers.append(t)

        results = league.run_season()
        for rank, (team, perf) in enumerate(results, 1):
            avg_skill = sum(p.skill for p in team.roster)/len(team.roster) if team.roster else 0
            summary.append({
                "Season": season, "Team": team.name, "Finish": rank,
                "Avg_Skill": round(avg_skill, 1), "Budget": round(team.budget, 0),
                "Squad_Size": len(team.roster)
            })
        league.distribute_rewards(results)

    # Save logic
    with open('transfer_data.csv', 'w', newline='') as f:
        dw = csv.DictWriter(f, fieldnames=all_transfers[0].keys())
        dw.writeheader()
        dw.writerows(all_transfers)
    with open('season_summary.csv', 'w', newline='') as f:
        dw = csv.DictWriter(f, fieldnames=summary[0].keys())
        dw.writeheader()
        dw.writerows(summary)

    print("\nSimulation Complete. Files saved.")