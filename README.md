# Project Mercato: Multi-Agent Game-Theoretic Simulation

## 01. Logic Architecture
Project Mercato is a high-fidelity simulation of professional transfer markets, focusing on **Marginal Utility** and **Resource Scarcity**. Unlike standard simulators, this engine treats players as assets whose value is derived from their **Win-Probability-Added (WPA)** relative to an agent's existing roster quality.

## 02. Key Engineering Milestones

### A. Dynamic Position Hunger (Diminishing Marginal Utility)
Implemented a non-linear decay function for asset valuation. As an agent approaches its roster target for a specific position (e.g., "ST" or "GK"), the internal valuation of additional assets in that class drops exponentially. 
* **Impact:** Prevents capital-rich agents from monopolizing the market and forces strategic "exit" behaviors.

### B. Subjective Value & Strategy-Based Scaling
Agents are assigned distinct financial personalities:
* **WIN_NOW:** Prioritizes immediate skill gain with a 1.5x utility multiplier.
* **REBUILD:** Applies a Time-Value-of-Asset discount, penalizing older players regardless of high skill ratings.

### C. Second-Price Auction with Reserve Logic
Simulates realistic market-clearing prices. The winner pays a 5% premium over the runner-up's maximum "walk-away" point, ensuring that prices are determined by **market competition** rather than arbitrary fixed tags.

## 03. Technical Stack & Modeling
* **Algorithm:** Multi-Agent Sealed-Bid Auction.
* **Stochastic Modeling:** Gaussian Distribution (Normal) for talent scarcity (Skill $\mu=75, \sigma=8$).
* **Data Persistence:** Automated CSV logging of transaction history, strategy utilization, and capital flow.

## 04. System Analysis (The "Quant" View)
This project serves as a testbed for answering: *“Is it mathematically optimal to acquire one superstar or three average assets?”* By modeling **Opportunity Cost**, the simulator demonstrates that the 'highest skill' choice is rarely the 'highest ROI' choice under budget constraints.