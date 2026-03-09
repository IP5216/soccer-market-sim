import random
import csv

class Player:
    def __init__(self, name, skill, age, position):
        self.name = name
        self.skill = skill 
        self.age = age
        self.position = position # "ST", "MID", "DEF, GK"
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
        # New: Tracking current skill levels
        self.squad_quality = {"ST": 60.0, "MID": 60.0, "DEF": 60.0, "GK": 60.0}
        
        # New: Position Hunger (Target number of players per position)
        self.targets = {"ST": 2, "MID": 4, "DEF": 4, "GK": 1}

    def get_hunger_multiplier(self, position):
        """
        Calculates how 'desperate' a team is for a position.
        If they have met their target, valuation drops significantly.
        """
        current_count = len([p for p in self.roster if p.position == position])
        target_count = self.targets.get(position, 1)

        if current_count == 0:
            return 1.3  # 30% Desperation Premium
        if current_count < target_count:
            return 1.0  # Standard Value
        
        # Diminishing Utility: Every player above target reduces valuation by 40%
        return 0.6 ** (current_count - target_count + 1)

    def update_squad_quality(self):
        """Recalculates the baseline skill for each position group."""
        for pos in self.squad_quality:
            pos_players = [p.skill for p in self.roster if p.position == pos]
            if pos_players:
                self.squad_quality[pos] = sum(pos_players) / len(pos_players)

    def calculate_internal_valuation(self, player, scarcity_mid):
        # 1. Marginal Utility (WPA)
        current_avg = self.squad_quality.get(player.position, 60)
        marginal_gain = max(0, player.skill - current_avg)
        
        # 2. Strategy & Age Scaling
        if self.strategy == "WIN_NOW":
            utility_score = marginal_gain * 1.5 
        else:
            age_factor = max(0.1, (35 - player.age) / 15)
            utility_score = marginal_gain * age_factor

        # 3. New: Apply Position Hunger
        hunger_mid = self.get_hunger_multiplier(player.position)
        
        # 4. Final Valuation
        valuation = utility_score * 5_000_000 * scarcity_mid * hunger_mid
        return min(valuation, self.budget)
    
def run_auction(player, teams, market):
    scarcity_mid = market.get_scarcity_multiplier(player.position)
    bids = []
    
    for team in teams:
        # Each team bids based on their current roster and hunger
        max_val = team.calculate_internal_valuation(player, scarcity_mid)
        bids.append((max_val, team))

    bids.sort(key=lambda x: x[0], reverse=True)
    winner_val, winner_team = bids[0]
    
    # Second-price auction logic (5% above runner-up)
    reserve_price = player.base_value * 0.7  # The 'Floor' price
    runner_up_val = bids[1][0] if len(bids) > 1 else reserve_price
    final_price = max(reserve_price, runner_up_val * 1.05)

    if final_price <= winner_val and final_price <= winner_team.budget:
        winner_team.budget -= final_price
        winner_team.roster.append(player)
        
        # CRITICAL: Update team state so they aren't 'hungry' for this position anymore
        winner_team.update_squad_quality() 
        
        return {
            "player_name": player.name,
            "skill": player.skill,
            "position": player.position,
            "buyer": winner_team.name,
            "price": round(final_price, 2),
            "strategy_used": winner_team.strategy
        }
    return None

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
    all_players = generate_random_players(100)
    market = Market(all_players)
    clubs = [
        Team("Global Giants", 800000000, "WIN_NOW"),
        Team("London Blue", 600000000, "WIN_NOW"),
        Team("Ajax-Style Academy", 200000000, "REBUILD"),
        Team("Moneyball FC", 150000000, "REBUILD")
    ]

    all_players.sort(key=lambda x: x.skill, reverse=True)
    
    # Store all transaction records here
    transfer_history = []

    for p in all_players:
        transaction = run_auction(p, clubs, market)
        if transaction:
            transfer_history.append(transaction)

    if len(transfer_history) > 0:
        keys = transfer_history[0].keys()
        with open('transfer_data.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(transfer_history)
        print(f"\nSimulation Complete. {len(transfer_history)} transfers saved to 'transfer_data.csv'.")
    else:
        print("\nSimulation Complete, but NO transfers were made. Check your budget and valuations.")