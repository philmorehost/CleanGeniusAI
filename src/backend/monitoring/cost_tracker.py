import os
import sqlite3
from datetime import datetime

class CostTracker:
    PRICING = {
        'deepseek': {'input': 0.14 / 1_000_000, 'output': 0.28 / 1_000_000},
        'openai': {
            'gpt-3.5-turbo': {'input': 0.50 / 1_000_000, 'output': 1.50 / 1_000_000},
            'gpt-4': {'input': 30.00 / 1_000_000, 'output': 60.00 / 1_000_000}
        },
        'claude': {
            'claude-3-sonnet': {'input': 3.00 / 1_000_000, 'output': 15.00 / 1_000_000}
        },
        'gemini': {'input': 0, 'output': 0},
        'ollama': {'input': 0, 'output': 0}
    }

    def __init__(self, db):
        self.db = db

    def calculate_cost(self, provider, model, input_tokens, output_tokens):
        p = provider.lower()
        if p == 'deepseek':
            rates = self.PRICING['deepseek']
        elif p in self.PRICING and isinstance(self.PRICING[p], dict) and 'input' in self.PRICING[p]:
            rates = self.PRICING[p]
        elif p in self.PRICING and model in self.PRICING[p]:
            rates = self.PRICING[p][model]
        else:
            return 0.0

        return round((input_tokens * rates['input']) + (output_tokens * rates['output']), 6)

    def log_usage(self, provider, model, input_tokens, output_tokens, request_type='scan'):
        cost = self.calculate_cost(provider, model, input_tokens, output_tokens)
        conn = self.db._conn()
        conn.execute("""
            INSERT INTO api_usage (provider, model, input_tokens, output_tokens, cost_usd, request_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (provider, model, input_tokens, output_tokens, cost, request_type))
        conn.commit()
        conn.close()
        return cost

    def get_monthly_stats(self, month=None):
        if month is None:
            month = datetime.now().strftime('%Y-%m')

        conn = self.db._conn()
        row = conn.execute("""
            SELECT SUM(cost_usd) FROM api_usage
            WHERE strftime('%Y-%m', timestamp) = ?
        """, (month,)).fetchone()
        total_cost = row[0] or 0.0

        by_provider_rows = conn.execute("""
            SELECT provider, COUNT(*), SUM(input_tokens + output_tokens), SUM(cost_usd)
            FROM api_usage
            WHERE strftime('%Y-%m', timestamp) = ?
            GROUP BY provider
        """, (month,)).fetchall()

        conn.close()

        budget = float(os.getenv('MONTHLY_BUDGET_USD', '5.00'))

        return {
            'month': month,
            'total_cost': total_cost,
            'by_provider': [
                {
                    'provider': r[0],
                    'requests': r[1],
                    'tokens': r[2] or 0,
                    'cost': r[3] or 0.0
                }
                for r in by_provider_rows
            ],
            'budget': {
                'limit': budget,
                'spent': total_cost,
                'alert_threshold': 0.8
            }
        }
