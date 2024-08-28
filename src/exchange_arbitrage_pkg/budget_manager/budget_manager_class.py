from typing import Optional, Type, Tuple, List


class SymbolImportance:
    def __init__(self, symbol: str, importance: float):
        self.symbol = symbol
        self.importance = importance

    def get_symbol(self):
        return self.symbol

    def get_importance(self):
        return self.importance


def generate_symbol_importance_pairs(symbol_importance_pairs: List[Tuple[str, float]]):
    return [SymbolImportance(pair[0], pair[1]) for pair in symbol_importance_pairs]


def normalize_weights(importance: [float]):
    total = sum(importance)
    return [weight / total for weight in importance]


def get_importance(symbol_importance_pairs: List[SymbolImportance]):
    return [pair.get_importance() for pair in symbol_importance_pairs]


class BudgetManager:
    def __init__(self, budget: Optional[float], is_uniform: bool = True):
        self.budget = budget
        self.budget_history = []
        self.symbol_budget_pairs = []
        self.symbol_weights = []
        self.is_uniform = is_uniform

    def set_budget(self, symbol_importance_pairs: List[SymbolImportance]):
        self.symbol_budget_pairs = symbol_importance_pairs
        importances = get_importance(symbol_importance_pairs)
        self.symbol_weights = normalize_weights(importances)

    def get_symbol_budget(self, total_budget: float, symbol: str):
        if self.is_uniform:
            return total_budget / len(self.symbol_budget_pairs)
        else:
            for pair in self.symbol_budget_pairs:
                if pair.get_symbol() == symbol:
                    return total_budget * pair.get_importance()
            raise ValueError(f"Symbol {symbol} not found in budget manager")

    def update_budget(self, new_budget: float):
        self.budget = new_budget
        self.budget_history.append(new_budget)

    def get_budget(self):
        return self.budget

    def get_budget_history(self):
        return self.budget_history


