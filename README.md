# IMC_PROSPERITY_3_2025

## Project Title

IMC Prosperity 3 Trading Challenge 2025 — Code & Analysis

---

## Introduction

Welcome to the repository for **MMMetrics**’s first participation in the IMC Prosperity 3 Trading Challenge 2025. Over five intense rounds, our team [(me) Paranjay, Christopher, and Andreas] tackled both algorithmic and manual trading problems, developing and refining strategies under real-time constraints. This README outlines each challenge, summarizes our approach, and links to the code and notebooks we used.

#Quick Highlights:

15 days, 5 rounds, 12,620 teams, 2 formats: algorithmic & manual.

## MMMetrics Rankings: UK Rank 45 | Algo 288 | Overall 477 | Manual 1183.


---

## Table of Contents

- [Algorithmic Challenges](#algorithmic-challenges)
  - [Round 1](#round-1)
  - [Round 2](#round-2)
  - [Round 3](#round-3)
  - [Round 4](#round-4)
  - [Round 5](#round-5)
- [Manual Challenges](#manual-challenges)
  - [Round 1](#manual-round-1)
  - [Round 2](#manual-round-2)
  - [Round 3](#manual-round-3)
  - [Round 4](#manual-round-4)
  - [Round 5](#manual-round-5)
- [Contributing](#contributing)

---

## Algorithmic Challenges

Each round’s algorithmic solution is implemented in Python scripts located in this repo itself.

### Round 1
**Summary & Logic:**
- **Products Traded:** Rainforest Resin (stable), Kelp (volatile), Squid Ink (patterned).
- **Strategy:** Market-making for Rainforest Resin and Kelp by placing buy/sell orders around a calculated fair price. Explored arbitrage on Rainforest Resin when favorable spreads appeared. Squid Ink was skipped due to complex patterns needing deeper analysis.

### Round 2
**Summary & Logic:**
- **Assets:** Picnic baskets composed of croissants, jams, and djembes alongside standalone goods.
- **Strategy:** Identified price discrepancies via normalized spreads between related assets (e.g., Picnic Basket 1 vs. Croissants). Traded these spreads while enforcing position limits, also arbitraging between standalone goods to maximize profit.

### Round 3
**Summary & Logic:**
- **Instruments:** Volcanic Rock Vouchers with specific strike prices.
- **Strategy:** Applied the Black–Scholes model to estimate theoretical prices. Bought undervalued and sold overvalued vouchers relative to model price, incorporating risk and inventory constraints.

### Round 4
**Summary & Logic:**
- **Product:** Magnificent Macarons, price influenced by sunlight, sugar prices, tariffs.
- **Strategy:** Trained a linear regression on observable factors to predict fair price. Executed a market-making algorithm placing orders around this estimate, managing position and conversion limits.

### Round 5
**Summary & Logic:**
- **Enhancements:** Integrated counterparty information to refine thresholds for Volcanic Rock Voucher trades. Continued using regression-based pricing for Macarons and dynamic conversion management based on average P&L with counterparties.

---

## Manual Challenges

Our manual challenge analyses are provided as Jupyter notebooks under `manuals/`.

### Manual Round 1
**Notebook:** [round1_manual.ipynb](https://colab.research.google.com/drive/1ml7Kb3FU4hBnK5ksxMXipbJbVVyAyvGO?usp=sharing)

**Summary & Logic:**
- **Objective:** Maximize SeaShells through a series of currency conversions across island currencies in up to five trades.
- **Approach:** Employed depth-first search to enumerate all conversion sequences, tracking the path yielding the highest final shell count.

### Manual Round 2
**Notebook:** [round2_manual.ipynb](https://colab.research.google.com/drive/1PObQOfA3HKPnB3rqRDNs5rGbFs3D9Ovc?usp=sharing)

**Summary & Logic:**
- **Objective:** Choose up to two shipping containers with hidden treasures, accounting for popularity and second-container costs.
- **Approach:** Evaluated all container combinations, computing expected profit using a formula incorporating treasure multipliers, participant counts, popularity, and extra costs. Ranked choices to identify optimal and suboptimal containers.

### Manual Round 3
**Notebook:** [round3_manual.ipynb](https://colab.research.google.com/drive/1KN8yyezpNHLZNMIXXFIZGgoPOUuZCTU0?usp=sharing)

**Summary & Logic:**
- **Objective:** Bid on Flippers from Sea Turtles considering segmented reserve prices and competitor bid distributions.
- **Approach:** Ran Monte Carlo simulations over bid pairs, adjusting success probability based on relative position to competitor averages. Selected bids that maximized expected profit.

### Manual Round 4
**Notebook:** [round4_manual.ipynb](https://colab.research.google.com/drive/1sRLZFBU8cXhf0PMpMUEKgYLliJap1XPy?usp=sharing)

**Summary & Logic:**
- **Objective:** Pick up to three suitcases with shared prizes among players and opening costs.
- **Approach:** Trained a Gradient Boosting Regressor on previous-round data to predict selection probabilities. Computed expected profit for combinations, adjusting for sharing and fees to identify the best picks.

### Manual Round 5
**Notebook:** N/A (manual, one-day event)

**Summary & Logic:**
- **Objective:** Exclusive one-day trading event using real-time news to trade foreign goods.
- **Approach:** Relied on manual analysis of news feeds, balancing trade sizes to optimize profit versus market impact, with no automated code.

---

## Contributing

We welcome improvements to strategies, bug fixes, and optimization ideas.

---


