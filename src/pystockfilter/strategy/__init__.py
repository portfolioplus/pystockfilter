from enum import Enum
from pystockfilter.strategy.base_strategy import BaseStrategy
from pystockfilter.strategy.uo_strategy import UltimateStrategy
from pystockfilter.strategy.uo_ema_cross_ema_strategy import UltimateEmaCrossEmaStrategy
from pystockfilter.strategy.uo_ema_cross_close_strategy import UltimateEmaCrossCloseStrategy
from pystockfilter.strategy.ema_cross_close_strategy import EmaCrossCloseStrategy
from pystockfilter.strategy.ema_cross_ema_strategy import EmaCrossEmaStrategy
from pystockfilter.strategy.ema_cross_sma_strategy import EmaCrossSmaStrategy
from pystockfilter.strategy.rsi_strategy import RSIStrategy
from pystockfilter.strategy.sma_cross_sma_strategy import SmaCrossSmaStrategy
from pystockfilter.strategy.sma_cross_close_strategy import SmaCrossCloseStrategy
class StrategyName(Enum):
    ECCS = "eccs"
    ECES = "eces"
    ECSS = "ecss"
    RSIS = "rsis"
    SCCS = "sccs"
    SCSS = "scss"
    UECCS = "ueccs"
    UECES = "ueces"
    UO = "uo"

def strategy_from_name(strategy_name: StrategyName) -> BaseStrategy:
    strategy_map = {
        StrategyName.ECCS: EmaCrossCloseStrategy,
        StrategyName.ECES: EmaCrossEmaStrategy,
        StrategyName.ECSS: EmaCrossSmaStrategy,
        StrategyName.RSIS: RSIStrategy,
        StrategyName.SCSS: SmaCrossSmaStrategy,
        StrategyName.SCCS: SmaCrossCloseStrategy,
        StrategyName.UECCS: UltimateEmaCrossCloseStrategy,
        StrategyName.UECES: UltimateEmaCrossEmaStrategy,
        StrategyName.UO: UltimateStrategy,
    }
    strategy = strategy_map.get(strategy_name)
    assert strategy is not None, f"Strategy {strategy_name} not found"
    return strategy
