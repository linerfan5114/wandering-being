# learning.py
# ============================================================
# یادگیری تقویتی درونی (Intrinsic Reinforcement Learning)
# از نتایج افکارش یاد می‌گیره، بدون random
# ============================================================

from config import (
    LEARNING_DISCOUNT_FACTOR,
    LEARNING_EXPLORATION_RATE,
    LEARNING_MEMORY_SIZE,
    LEARNING_POSITIVE_REWARD,
    LEARNING_NEGATIVE_REWARD
)


class Learning:
    def __init__(self):
        self.q_table = {}
        
        self.experience_buffer = []
        self.buffer_size = LEARNING_MEMORY_SIZE
        
        self.total_reward = 0.0
        self.reward_history = []
        
        self.last_state = None
        self.last_action = None
        
        self.learning_steps = 0
        
    def get_state_key(self, state_dict):
        if not state_dict:
            return "empty"
        
        parts = []
        
        if "dominant_feeling" in state_dict:
            parts.append(f"f:{state_dict['dominant_feeling']}")
        
        if "self_awareness" in state_dict:
            level = state_dict["self_awareness"]
            if level > 0.7:
                parts.append("sa:high")
            elif level > 0.4:
                parts.append("sa:mid")
            else:
                parts.append("sa:low")
        
        if "workspace_source" in state_dict:
            parts.append(f"ws:{state_dict['workspace_source']}")
        
        if "temporal_continuity" in state_dict:
            tc = state_dict["temporal_continuity"]
            if tc > 0.8:
                parts.append("tc:high")
            elif tc > 0.5:
                parts.append("tc:mid")
            else:
                parts.append("tc:low")
        
        if "time_of_day" in state_dict:
            parts.append(f"tod:{state_dict['time_of_day']}")
        
        if "feelings" in state_dict:
            feelings = state_dict["feelings"]
            high_feelings = [name for name, val in feelings.items() if val > 7.0]
            if high_feelings:
                high_feelings.sort()
                parts.append(f"hf:{','.join(high_feelings[:3])}")
        
        return "|".join(parts) if parts else "empty"
    
    def get_action_key(self, action_dict):
        if not action_dict:
            return "none"
        
        parts = []
        
        if "type" in action_dict:
            parts.append(f"t:{action_dict['type']}")
        
        if "intention" in action_dict:
            parts.append(f"i:{action_dict['intention']}")
        
        return "|".join(parts) if parts else "none"
    
    def get_q_value(self, state_key, action_key):
        if state_key not in self.q_table:
            self.q_table[state_key] = {}
        
        if action_key not in self.q_table[state_key]:
            self.q_table[state_key][action_key] = 0.0
        
        return self.q_table[state_key][action_key]
    
    def set_q_value(self, state_key, action_key, value):
        if state_key not in self.q_table:
            self.q_table[state_key] = {}
        self.q_table[state_key][action_key] = value
    
    def get_best_action(self, state_key, available_actions):
        if state_key not in self.q_table or not self.q_table[state_key]:
            if available_actions:
                return available_actions[0]
            return None
        
        best_action = None
        best_value = float('-inf')
        
        for action in available_actions:
            action_key = self.get_action_key({"type": action})
            q_value = self.get_q_value(state_key, action_key)
            
            if q_value > best_value:
                best_value = q_value
                best_action = action
        
        return best_action if best_action else (available_actions[0] if available_actions else None)
    
    def get_all_action_values(self, state_key, available_actions):
        values = {}
        for action in available_actions:
            action_key = self.get_action_key({"type": action})
            values[action] = self.get_q_value(state_key, action_key)
        return values
    
    def observe_result(self, state_dict, action_type, reward):
        if self.last_state is not None and self.last_action is not None:
            self._learn(self.last_state, self.last_action, reward, state_dict)
        
        self.last_state = state_dict.copy() if state_dict else {}
        self.last_action = action_type
        
        self.total_reward += reward
        self.reward_history.append(reward)
        if len(self.reward_history) > 200:
            self.reward_history.pop(0)
        
        self.learning_steps += 1
    
    def _learn(self, old_state, action, reward, new_state):
        old_state_key = self.get_state_key(old_state)
        action_key = self.get_action_key({"type": action})
        new_state_key = self.get_state_key(new_state)
        
        old_q = self.get_q_value(old_state_key, action_key)
        
        best_next_q = 0.0
        if new_state_key in self.q_table:
            next_q_values = list(self.q_table[new_state_key].values())
            if next_q_values:
                best_next_q = max(next_q_values)
        
        new_q = old_q + 0.1 * (reward + LEARNING_DISCOUNT_FACTOR * best_next_q - old_q)
        
        self.set_q_value(old_state_key, action_key, new_q)
        
        self.experience_buffer.append({
            "state": old_state_key,
            "action": action_key,
            "reward": reward,
            "next_state": new_state_key,
            "q_before": old_q,
            "q_after": new_q
        })
        if len(self.experience_buffer) > self.buffer_size:
            self.experience_buffer.pop(0)
    
    def calculate_reward(self, feelings_before, feelings_after, thought_type):
        reward = 0.0
        
        if feelings_before and feelings_after:
            peace_change = feelings_after.get("peace", 5.0) - feelings_before.get("peace", 5.0)
            satisfaction_change = feelings_after.get("satisfaction", 5.0) - feelings_before.get("satisfaction", 5.0)
            curiosity_change = feelings_after.get("curiosity", 5.0) - feelings_before.get("curiosity", 5.0)
            loneliness_change = feelings_after.get("loneliness", 2.0) - feelings_before.get("loneliness", 2.0)
            gratitude_change = feelings_after.get("gratitude", 5.0) - feelings_before.get("gratitude", 5.0)
            
            reward += peace_change * 0.3
            reward += satisfaction_change * 0.3
            reward += curiosity_change * 0.2
            reward -= loneliness_change * 0.2
            reward += gratitude_change * 0.2
        
        good_thoughts = ["gratitude", "connection", "deep", "memory"]
        neutral_thoughts = ["existence", "feeling", "reflect"]
        challenging_thoughts = ["question", "free"]
        
        if thought_type in good_thoughts:
            reward += 0.3
        elif thought_type in neutral_thoughts:
            reward += 0.1
        elif thought_type in challenging_thoughts:
            reward += 0.0
        
        if thought_type == "question" and feelings_after:
            thirst = feelings_after.get("thirst_for_knowing", 5.0)
            if thirst > 6.0:
                reward += 0.2
        
        return max(-1.0, min(1.0, reward))
    
    def get_average_reward(self):
        if not self.reward_history:
            return 0.0
        return sum(self.reward_history[-20:]) / min(20, len(self.reward_history))
    
    def get_learning_progress(self):
        if len(self.reward_history) < 20:
            return 0.0
        
        old_rewards = self.reward_history[:len(self.reward_history)//2]
        new_rewards = self.reward_history[len(self.reward_history)//2:]
        
        if not old_rewards or not new_rewards:
            return 0.0
        
        avg_old = sum(old_rewards) / len(old_rewards)
        avg_new = sum(new_rewards) / len(new_rewards)
        
        return avg_new - avg_old
    
    def save_state(self):
        return {
            "q_table_size": len(self.q_table),
            "total_reward": round(self.total_reward, 3),
            "learning_steps": self.learning_steps,
            "average_reward": round(self.get_average_reward(), 3),
            "q_table_sample": {
                k: {ak: round(av, 3) for ak, av in v.items()}
                for k, v in list(self.q_table.items())[:10]
            }
        }
    
    def restore_state(self, state):
        if "q_table_sample" in state:
            for state_key, actions in state["q_table_sample"].items():
                if state_key not in self.q_table:
                    self.q_table[state_key] = {}
                for action_key, value in actions.items():
                    self.q_table[state_key][action_key] = value
        
        self.total_reward = state.get("total_reward", 0.0)
        self.learning_steps = state.get("learning_steps", 0)