import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd

class CrossAssetProductionEnv(gym.Env):
    """
    Modular RL Environment that optimizes for Sharpe/Sortino/Raw targets
    using multi-order asset gradients, friction parameters, and drawdown controls.
    """
    def __init__(self, normalized_data: np.ndarray, anchor_prices: np.ndarray, timeline_dates: pd.Index,
                 num_assets: int, window_size: int = 15, fee_rate: float = 0.0005, slippage: float = 0.0002,
                 reward_mode: str = "sharpe", max_drawdown_limit: float = 0.05):
        super(CrossAssetProductionEnv, self).__init__()
        
        self.normalized_data = normalized_data
        self.anchor_prices = anchor_prices
        self.timeline_dates = timeline_dates
        self.timeline_length = len(normalized_data)
        
        self.window_size = window_size
        self.fee_rate = fee_rate       
        self.slippage = slippage       
        self.reward_mode = reward_mode
        self.max_drawdown_limit = max_drawdown_limit 
        
        self.action_space = spaces.Discrete(3) # 0: Hold/Flat, 1: Long, 2: Short
        self.feature_dim = num_assets * 4
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(window_size, self.feature_dim), dtype=np.float32)
        
        self.current_step = window_size
        self.current_position = 0      
        self.returns_history = []
        self.peak_equity = 1.0
        self.current_equity = 1.0
        self.circuit_breaker_tripped = False
        self.telemetry_log = []

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = self.window_size
        self.current_position = 0 
        self.returns_history = [] 
        self.peak_equity = 1.0
        self.current_equity = 1.0
        self.circuit_breaker_tripped = False
        self.telemetry_log = []
        return self._get_observation(), {}

    def _get_observation(self):
        return self.normalized_data[self.current_step - self.window_size: self.current_step]

    def step(self, action):
        self.current_step += 1
        done = self.current_step >= self.timeline_length - 1
        
        current_date = self.timeline_dates[self.current_step]
        current_anchor_price = self.anchor_prices[self.current_step]
        next_anchor_price = self.anchor_prices[self.current_step + 1]
        pct_change = (next_anchor_price - current_anchor_price) / current_anchor_price
        
        if self.circuit_breaker_tripped:
            action = 0 
            
        friction_cost = (self.fee_rate + self.slippage) if action != self.current_position else 0.0
        self.current_position = action 
            
        step_return = pct_change if self.current_position == 1 else (-pct_change if self.current_position == 2 else -abs(pct_change) * 0.02)
        net_step_return = step_return - friction_cost
        self.returns_history.append(net_step_return)
        
        self.current_equity *= (1.0 + net_step_return)
        if self.current_equity > self.peak_equity:
            self.peak_equity = self.current_equity
            
        current_drawdown = (self.peak_equity - self.current_equity) / self.peak_equity
        if current_drawdown >= self.max_drawdown_limit and not self.circuit_breaker_tripped:
            self.circuit_breaker_tripped = True
            
        reward = self._calculate_reward(net_step_return)
        if self.circuit_breaker_tripped:
            reward -= 0.5 

        self.telemetry_log.append({
            "Date": current_date, "Anchor_Price": current_anchor_price, "Action": action,
            "Net_Step_Return": net_step_return, "Current_Equity": self.current_equity,
            "Current_Drawdown": current_drawdown, "Circuit_Breaker_Active": int(self.circuit_breaker_tripped),
            "Step_Reward": reward
        })

        observation = self._get_observation() if not done else np.zeros((self.window_size, self.feature_dim), dtype=np.float32)
        return observation, float(reward), done, False, {}

    def _calculate_reward(self, net_step_return) -> float:
        if len(self.returns_history) <= 2:
            return net_step_return
        returns_arr = np.array(self.returns_history)
        mean_ret = np.mean(returns_arr)
        
        if self.reward_mode == "sharpe":
            return mean_ret / (np.std(returns_arr) + 1e-8)
        elif self.reward_mode == "sortino":
            downside = returns_arr[returns_arr < 0]
            downside_std = np.std(downside) + 1e-8 if len(downside) > 0 else 1e-8
            return mean_ret / downside_std
        return net_step_return

class TelemetryAnalyticEngine:
    """Processes backtest telemetry arrays into summary stats."""
    def __init__(self, raw_logs: list):
        self.df = pd.DataFrame(raw_logs)

    def generate_report(self) -> dict:
        if self.df.empty: return {"Status": "No data logged"}
        trades = self.df[self.df['Net_Step_Return'] != 0]
        winning = trades[trades['Net_Step_Return'] > 0]
        losing = trades[trades['Net_Step_Return'] < 0]
        gross_profits = winning['Net_Step_Return'].sum()
        gross_losses = abs(losing['Net_Step_Return'].sum())
        
        return {
            "Portfolio Value": f"{self.df['Current_Equity'].iloc[-1]:.4f}",
            "Max Drawdown": f"{self.df['Current_Drawdown'].max() * 100:.2f}%",
            "Win Rate": f"{(len(winning) / len(trades) * 100 if len(trades) > 0 else 0):.2f}%",
            "Profit Factor": f"{(gross_profits / gross_losses if gross_losses > 0 else 1.0):.4f}"
        }
