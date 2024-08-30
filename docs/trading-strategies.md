# Trading Strategies for Cryptocurrency Exchange Arbitrage

## Introduction

This document outlines the unique trading strategies employed by our Cryptocurrency Exchange Arbitrage Tool. Our approach, affectionately dubbed the "Mahdiable" method, combines algorithmic analysis with creatively named execution strategies inspired by martial arts and boxing.

## The Mahdiable Algorithm

The core of our arbitrage strategy is the Mahdiable Algorithm. This algorithm analyzes the limit order books (LOBs) of the same cryptocurrency on both the source and destination exchanges to determine arbitrage opportunities.

### Algorithm Overview

```
FUNCTION MahdiableAlgorithm(src_lob, dst_lob, withdrawal_fee):
    Initialize trading_volume, spent_money, earned_money, withdrawal_fee_paid to 0
    src_stack ← convert to stack(src_lob)
    dst_stack ← convert to stack(dst_lob)
    
    WHILE src_stack is not empty AND dst_stack is not empty:
        source_order = src_stack.pop()
        destination_order = dst_stack.pop()
        
        IF destination_order[price] <= source_order[price]:
            BREAK  // No more profitable trades possible
        
        trade_volume = MIN(source_order[volume], destination_order[volume])
        
        Update withdrawal_fee_paid based on trade_volume and source_order[price]
        
        trading_volume += trade_volume
        spent_money += trade_volume * source_order[price]
        earned_money += trade_volume * destination_order[price]
        
        // Update remaining volumes
        source_order[volume] -= trade_volume
        destination_order[volume] -= trade_volume
        
        IF source_order has remaining volume:
            src_stack.push(source_order)
        IF destination_order has remaining volume:
            dst_stack.push(destination_order)
    
    RETURN trading_volume, spent_money, earned_money, withdrawal_fee_paid
```

### Symbol Evaluation

For each cryptocurrency C available on both exchanges (Ex_1 and Ex_2):

1. Calculate price difference: `price_diff = price(C, Ex_1) - price(C, Ex_2)`
2. Retrieve order books: `LOB(C, Ex_1)` and `LOB(C, Ex_2)`
3. Determine source and destination exchanges based on price difference
4. Calculate arbitrage potential: `Score(C) = MahdiableAlgorithm(src_lob, dst_lob, withdrawal_fee(C on src))`
5. Rank and return potential cryptocurrencies based on their scores

## Execution Strategies (Punches)

Once the Mahdiable Algorithm identifies profitable arbitrage opportunities, we employ various execution strategies, playfully named after boxing and martial arts moves.

### Basic Operations

- `BUY (X_i, Ex_u)`: Buy cryptocurrency X_i on exchange Ex_u
- `WITHDRAW (X_i, Ex_u, Ex_v)`: Withdraw cryptocurrency X_i from exchange Ex_u to exchange Ex_v
- `WAIT (X_i, Ex_v)`: Wait for cryptocurrency X_i to be deposited in exchange Ex_v
- `SELL (X_i, Ex_v)`: Sell cryptocurrency X_i on exchange Ex_v

### Strategy Types

1. **Cross Punch**
   - The most straightforward strategy
   - Sequence: `BUY (C, Ex_1) → WITHDRAW (C, Ex_1, Ex_2) → WAIT → SELL(C, Ex_2)`
   - Used when it's profitable to buy on Ex_1 and sell on Ex_2

2. **Hook Punch**
   - A more complex strategy used when you already hold the expensive cryptocurrency on the selling exchange
   - Part 1: `BUY (D, Ex_2) → WITHDRAW (D, Ex_2, Ex_1) → WAIT(D, Ex_1) → SELL(D, Ex_1)`
   - Part 2: `BUY (C, Ex_1) → WITHDRAW (C, Ex_1, Ex_2) → WAIT(C, Ex_2) → SELL(C, Ex_2)`
   - D is a different cryptocurrency that's cheaper to transfer between exchanges

3. **Kung Fu Punch**
   - A placeholder strategy
   - Used when the system needs to run a "punch" due to implementation mechanisms, but no actual trading is required

## Strategy Selection

The choice of which "punch" to use depends on several factors:

1. Current holdings on each exchange
2. Withdrawal fees for different cryptocurrencies
3. Transfer times between exchanges
4. Liquidity on both exchanges for the cryptocurrencies involved

The system dynamically selects the most appropriate strategy based on these factors and the current market conditions as analyzed by the Mahdiable Algorithm.

## Conclusion

The combination of the Mahdiable Algorithm for opportunity identification and the various "punch" strategies for execution allows our Cryptocurrency Exchange Arbitrage Tool to flexibly and efficiently capitalize on price discrepancies across exchanges. 

Remember, while these strategies are designed to identify and exploit arbitrage opportunities, cryptocurrency markets are highly volatile and unpredictable. Always use this tool responsibly and be aware of the risks involved in cryptocurrency trading.
