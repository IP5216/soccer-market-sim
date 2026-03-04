import random

class Player:
    def __init__(self, name, skill, age):
        self.name = name
        self.skill = skill  # 1-100
        self.age = age
        # Base Market Value: High skill + Young age = High price
        self.base_value = (self.skill * (35 - self.age)) * 50000

class Team:
    def __init__(self, name, budget, strategy):
        self.name = name
        self.budget = budget
        self.strategy = strategy # "WIN_NOW" or "REBUILD"
        self.roster = []

    def calculate_internal_valuation(self, player):
        """
        GAME THEORY ENGINE: Calculates the 'Utility' of a player 
        to THIS specific team. This is the 'Max Bid'.
        """
        if self.strategy == "WIN_NOW":
            # Values immediate impact (Skill) over long-term (Age)
            multiplier = (player.skill / 50) 
        else:
            # Values potential (Low Age) over immediate impact
            multiplier = (40 - player.age) / 10
        
        max_bid = player.base_value * multiplier
        return min(max_bid, self.budget) # Can't bid more than they have

def run_auction(player, teams):
    print(f"\n--- Auction for {player.name} (Skill: {player.skill}, Age: {player.age}) ---")
    
    bids = []
    for team in teams:
        max_valuation = team.calculate_internal_valuation(player)
        bids.append((max_valuation, team))
        print(f"{team.name} ({team.strategy}) values player at: ${max_valuation:,.2f}")

    # Sort bids highest to lowest
    bids.sort(key=lambda x: x[0], reverse=True)
    
    winner_val, winner_team = bids[0]
    runner_up_val, _ = bids[1]

    # The winner pays slightly more than what the 2nd place team was willing to pay
    # This simulates a 'Bidding War' price discovery.
    final_price = runner_up_val * 1.05 

    if final_price <= winner_val and final_price <= winner_team.budget:
        winner_team.budget -= final_price
        winner_team.roster.append(player)
        print(f"SUCCESS: {winner_team.name} wins {player.name} for ${final_price:,.2f}!")
    else:
        print(f"FAILED: No team could reach the reserve price or agreement.")

# --- EXECUTION ---
if __name__ == "__main__":
    # 1. Setup the Market
    talents = [
        Player("Wonderkid Haaland", 88, 19),
        Player("Veteran Ramos", 85, 34),
        Player("Mid-tier Squad Player", 75, 26)
    ]

    clubs = [
        Team("Real Wealth", 500000000, "WIN_NOW"),
        Team("Future FC", 200000000, "REBUILD"),
        Team("Budget United", 100000000, "REBUILD")
    ]

    # 2. Run the Simulations
    for p in talents:
        run_auction(p, clubs)

    # 3. Final Report
    print("\n--- Final Transfer Report ---")
    for team in clubs:
        players_bought = [p.name for p in team.roster]
        print(f"{team.name} Remaining Budget: ${team.budget:,.2f} | Roster: {players_bought}")