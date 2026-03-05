import random

class Player:
    def __init__(self, name, skill, age, position):
        self.name = name
        self.skill = skill 
        self.age = age
        self.position = position # "ST", "MID", "DEF"
        # Base Market Value calculation
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
        """
        The fewer players in a position, the higher the multiplier.
        If only 1 player exists, price jumps by 50%.
        """
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

    def calculate_internal_valuation(self, player, scarcity_mid):
        # 1. Base Strategy Logic
        if self.strategy == "WIN_NOW":
            val = player.base_value * (player.skill / 60)
        else:
            val = player.base_value * ((40 - player.age) / 10)
        
        # 2. Apply Scarcity (The Economic Hook)
        final_valuation = val * scarcity_mid
        return min(final_valuation, self.budget)

def run_auction(player, teams, market):
    print(f"\n--- Auction: {player.name} ({player.position}) | Skill: {player.skill} ---")
    
    scarcity_mid = market.get_scarcity_multiplier(player.position)
    if scarcity_mid > 1.0:
        print(f"!!! SCARCITY ALERT: {player.position} supply is low. Prices inflated by {int((scarcity_mid-1)*100)}% !!!")

    bids = []
    for team in teams:
        max_val = team.calculate_internal_valuation(player, scarcity_mid)
        bids.append((max_val, team))

    bids.sort(key=lambda x: x[0], reverse=True)
    
    winner_val, winner_team = bids[0]
    runner_up_val = bids[1][0] if len(bids) > 1 else player.base_value * 0.8
    
    final_price = runner_up_val * 1.05 

    if final_price <= winner_val and final_price <= winner_team.budget:
        winner_team.budget -= final_price
        winner_team.roster.append(player)
        print(f"SOLD: {winner_team.name} paid ${final_price:,.2f}")
    else:
        print("RESULT: No deal reached (Price exceeded budget/valuation)")

import random

# --- (Keep your Player, Team, and Market classes from the previous step) ---

def generate_random_players(count):
    players = []
    positions = ["ST", "MID", "DEF", "GK"]
    names = ["Silva", "Müller", "Jones", "Mbappe", "Kane", "Rossi", "Zhang", "Hernandez"]
    
    for _ in range(count):
        name = f"{random.choice(names)} {random.randint(100, 999)}"
        # Gaussian distribution: Most players are skill 70-75, few are 90+
        skill = int(random.gauss(75, 8)) 
        skill = max(60, min(99, skill)) # Clamp between 60-99
        
        age = random.randint(18, 34)
        pos = random.choice(positions)
        
        players.append(Player(name, skill, age, pos))
    return players

# --- EXECUTION ---
if __name__ == "__main__":
    # 1. Generate 100 Random Players
    all_players = generate_random_players(100)
    market = Market(all_players)

    # 2. Create various Team Personas
    clubs = [
        Team("Oil Money United", 800000000, "WIN_NOW"),
        Team("London Blue", 600000000, "WIN_NOW"),
        Team("Ajax-Style Academy", 200000000, "REBUILD"),
        Team("Moneyball FC", 150000000, "REBUILD"),
        Team("Relegation Fighters", 800000000, "WIN_NOW")
    ]

    # 3. Sort players by skill so the 'Best' are auctioned first
    all_players.sort(key=lambda x: x.skill, reverse=True)

    # 4. Run the Market Window
    print(f"MARKET OPEN: {len(all_players)} players available.")
    print(f"Supply Levels: {market.position_counts}")
    
    for p in all_players:
        run_auction(p, clubs, market)

    # 5. The "Quant" Summary
    print("\n" + "="*40)
    print("FINAL MARKET RECAP")
    print("="*40)
    for team in clubs:
        print(f"{team.name: <20} | Budget Left: ${team.budget/1e6: >6.1f}M | Players: {len(team.roster)}")