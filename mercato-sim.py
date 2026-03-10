import random
import csv
import os

# --- STRATEGIC SIMULATION CONFIGURATION ---
CONFIG = {
    "ROSTER_CAP": 28,
    "MIN_SQUAD": {"GK": 1, "DEF": 4, "MID": 3, "ST": 3},
    "RETIREMENT_AGE": 35,
    "DECLINE_AGE": 30,
    "GROWTH_LIMIT": 25,
    "LUXURY_TAX_THRESHOLD": 600_000_000,
    "TAX_RATE": 0.50,
    "PERFORMANCE_VARIANCE": 4.0,   # Increased to allow for "Underdog" seasons
    "TV_REVENUE_BASE": 65_000_000,  # Base floor to keep small teams viable
    "WAGE_COEFFICIENT": 28.5,       # High penalty for elite squad maintenance
    "SCOUTING_ERROR_RANGE": 10      # High base error for non-Moneyball teams
}

class Player:
    def __init__(self, name, skill, age, position):
        self.name = name
        self.skill = skill
        self.age = age
        self.position = position
        self.potential = skill + random.randint(5, 18)
        # Market value uses a power law: stars are exponentially expensive
        self.market_value = (self.skill ** 3.0) * 40

class Team:
    def __init__(self, name, budget, strategy, start_skill):
        self.name = name
        self.budget = budget
        self.strategy = strategy
        self.roster = []
        self.last_season_rank = 1
        # Moneyball Advantage: Higher scouting accuracy and specific rebuild focus
        self.scouting_accuracy = 0.95 if strategy == "REBUILD" else 0.70
        self._generate_initial_squad(start_skill)

    def _generate_initial_squad(self, avg_skill):
        for pos, count in CONFIG["MIN_SQUAD"].items():
            for i in range(count + 1):
                p = Player(f"{self.name}_Init_{pos}_{i}", int(random.gauss(avg_skill, 5)), random.randint(21, 28), pos)
                self.roster.append(p)

    def pay_wages(self):
        """Strategic Outflow: Punishes hoarding high-skill players."""
        # Elite players demand exponentially higher wages
        total_bill = sum([(p.skill ** 2.6) * CONFIG["WAGE_COEFFICIENT"] for p in self.roster])
        self.budget -= total_bill
        return total_bill

    def develop_players(self):
        """Aging & Realistic Decline logic."""
        for p in self.roster:
            p.age += 1
            if p.age < CONFIG["GROWTH_LIMIT"]:
                p.skill += random.randint(1, 4)
            elif p.age > CONFIG["DECLINE_AGE"]:
                p.skill -= random.randint(1, 3)
            p.skill = max(10, min(99, p.skill))

    def sell_players(self):
        """Moneyball Arbitrage: Selling stars at peak value."""
        self.roster.sort(key=lambda x: x.skill)
        sold, recouped = 0, 0
        updated_roster = []
        for p in self.roster:
            pos_count = len([x for x in self.roster if x.position == p.position])
            # Sell if over cap OR if Rebuild strategy hits a 'Sell High' target (Skill 86+)
            if (len(self.roster) > CONFIG["ROSTER_CAP"] or (self.strategy == "REBUILD" and p.skill >= 86)) and pos_count > CONFIG["MIN_SQUAD"][p.position]:
                self.budget += p.market_value * 0.85
                recouped += p.market_value * 0.85
                sold += 1
            else:
                updated_roster.append(p)
        self.roster = updated_roster
        return sold, recouped

    def calculate_valuation(self, player, scarcity_multiplier):
        """Incorporate Scouting Uncertainty & Desperation Budgeting."""
        perceived_pot = (player.potential * self.scouting_accuracy) + (player.skill * (1 - self.scouting_accuracy))
        
        # Rebuild teams value potential; Win-Now teams value current skill
        if self.strategy == "REBUILD":
            base_score = (perceived_pot * 0.8) + (player.skill * 0.2)
        else:
            base_score = (player.skill * 0.9) + (perceived_pot * 0.1)
            
        # Desperation factor for bottom-ranked teams
        desperation = 1.4 if self.last_season_rank == 4 else 1.0
        
        valuation = (base_score ** 2.9) * 35 * desperation * scarcity_multiplier
        # Limit bid to a percentage of remaining budget
        max_bid_pct = 0.6 if self.last_season_rank == 4 else 0.4
        return min(valuation, self.budget * max_bid_pct)

class League:
    def __init__(self, teams):
        self.teams = teams

    def apply_financial_parity(self):
        """Luxury Tax logic to redistribute wealth."""
        tax_pool = 0
        for t in self.teams:
            if t.budget > CONFIG["LUXURY_TAX_THRESHOLD"]:
                tax = (t.budget - CONFIG["LUXURY_TAX_THRESHOLD"]) * CONFIG["TAX_RATE"]
                t.budget -= tax
                tax_pool += tax
        # Redistribute 50% of the tax to the bottom two teams
        share = tax_pool / 2
        bottom_two = sorted(self.teams, key=lambda x: x.last_season_rank, reverse=True)[:2]
        for t in bottom_two:
            t.budget += share / 2

    def run_season(self):
        results = []
        for t in self.teams:
            t.roster.sort(key=lambda x: x.skill, reverse=True)
            top_11_avg = sum([p.skill for p in t.roster[:11]]) / 11
            perf = top_11_avg + random.uniform(-CONFIG["PERFORMANCE_VARIANCE"], CONFIG["PERFORMANCE_VARIANCE"])
            results.append((t, perf))
        results.sort(key=lambda x: x[1], reverse=True)
        for i, (t, _) in enumerate(results):
            t.last_season_rank = i + 1
        return results

def run_auction(player, teams, season_num, scarcity_multiplier):
    bids = []
    for t in teams:
        val = t.calculate_valuation(player, scarcity_multiplier)
        if val >= player.market_value:
            bids.append((val, t))
    
    if not bids: return None
    bids.sort(key=lambda x: x[0], reverse=True)
    winner_val, winner_team = bids[0]
    # Price is the second-highest bid or the market value
    second_price = bids[1][0] if len(bids) > 1 else player.market_value
    final_price = max(player.market_value, second_price)

    if winner_team.budget >= final_price:
        winner_team.budget -= final_price
        winner_team.roster.append(player)
        return {"season": season_num, "player": player.name, "skill": player.skill, "buyer": winner_team.name, "price": final_price}
    return None

if __name__ == "__main__":
    clubs = [
        Team("Global Giants", 550_000_000, "WIN_NOW", 82),
        Team("London Blue", 400_000_000, "WIN_NOW", 78),
        Team("Ajax Academy", 250_000_000, "REBUILD", 74),
        Team("Moneyball FC", 150_000_000, "REBUILD", 70)
    ]
    
    league = League(clubs)
    summary_logs, transfer_logs = [], []
    
    for season in range(1, 6):
        print(f"\n--- SEASON {season} ---")
        league.apply_financial_parity()
        
        for team in clubs:
            team.budget += CONFIG["TV_REVENUE_BASE"]
            team.sell_players()
            team.develop_players()
            # Unique wages for each team
            wages = team.pay_wages()

        # Scarcity Logic integrated
        players = [Player(f"Gen_{season}_{i}", int(random.gauss(73, 8)), random.randint(18, 30), random.choice(["ST", "MID", "DEF", "GK"])) for i in range(100)]
        players.sort(key=lambda x: x.skill, reverse=True)
        
        for p in players:
            # Simple scarcity: if fewer of that position, price goes up
            pos_count = len([x for x in players if x.position == p.position])
            scarcity_mult = 1.3 if pos_count < 20 else 1.0
            tx = run_auction(p, clubs, season, scarcity_mult)
            if tx: transfer_logs.append(tx)

        standings = league.run_season()
        prizes = [150_000_000, 100_000_000, 50_000_000, 20_000_000]
        for i, (team, perf) in enumerate(standings):
            team.budget += prizes[i]
            summary_logs.append({
                "Season": season, "Team": team.name, "Rank": i+1, 
                "Skill": round(perf, 1), "Budget": round(team.budget, 0), "Wages": round(wages, 0)
            })
            print(f"Rank {i+1}: {team.name} (Avg Skill: {perf:.1f})")

    # Export CSVs
    with open('season_summary.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=summary_logs[0].keys())
        writer.writeheader()
        writer.writerows(summary_logs)
    
    with open('transfer_data.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=transfer_logs[0].keys())
        writer.writeheader()
        writer.writerows(transfer_logs)