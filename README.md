# Project Mercato: Game-Theoretic Transfer Simulator

## Overview
Project Mercato is a Python-based simulation engine designed to model the economic complexities of professional soccer transfer markets. Unlike standard sports games that use static "if/then" logic, this project utilizes **Utility Functions** and **Agent-Based Modeling** to simulate rational decision-making among competing entities.

## Core Engineering Principles
* **Subjective Value Theory:** Each "Team" agent evaluates players based on internal strategic goals (e.g., 'Win Now' vs. 'Rebuild') rather than fixed market prices.
* **Strategic Bidding:** Implements a variation of a Second-Price Auction, where market clearing prices are determined by the competition's "Maximum Walk-away Point."
* **Resource Allocation:** Simulates the trade-offs between immediate skill acquisition and long-term asset appreciation.
* **Dynamic Scarcity Engine:** Includes a supply-side modifier that inflates player valuations when specific asset classes (positions) are under-represented in the market pool.
## Technical Stack
* **Language:** Python 3.x
* **Methodology:** Object-Oriented Programming (OOP)
* **Concepts:** Game Theory (Nash Equilibrium), Economic Modeling, Discrete Event Simulation.

## Future Roadmap
- **Phase 2:** Integrate `scipy` for multi-variable optimization.
- **Phase 3:** Implement Monte Carlo simulations to calculate the ROI of different financial strategies over 1,000 seasons.