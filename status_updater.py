import os
import random
import requests
from slack_sdk import WebClient
from datetime import datetime
import time
from typing import Tuple

class QuoteFetcher:
    """Handles fetching and processing quotes from various APIs."""
    
    def __init__(self):
        self.apis = [
            {
                'url': 'https://api.quotable.io/random',
                'process': lambda r: (r['content'], r['author'])
            },
            {
                'url': 'https://api.adviceslip.com/advice',
                'process': lambda r: (r['slip']['advice'], 'Advice Slip')
            }
        ]

    def get_random_quote(self) -> Tuple[str, str]:
        """Fetch a random quote from one of the APIs."""
        api = random.choice(self.apis)
        try:
            response = requests.get(api['url'], timeout=5)
            response.raise_for_status()
            content = response.json()
            quote, author = api['process'](content)
            return f"{quote} - {author}", self._categorize_quote(quote)
        except Exception as e:
            print(f"API Error: {e}")
            fallback_quotes = [
                ("The only way to do great work is to love what you do. - Steve Jobs", "inspiration"),
                ("Stay hungry, stay foolish. - Steve Jobs", "motivation"),
                ("The future depends on what you do today. - Gandhi", "future"),
                ("Life is what happens while you're busy making other plans. - John Lennon", "life")
            ]
            return random.choice(fallback_quotes)

    def _categorize_quote(self, quote: str) -> str:
        """Analyze quote content to determine its category for emoji matching."""
        categories = {
            'inspiration': ['dream', 'inspire', 'create', 'achieve', 'possible'],
            'motivation': ['work', 'success', 'goal', 'accomplish', 'determination'],
            'wisdom': ['learn', 'know', 'wisdom', 'understand', 'truth'],
            'life': ['life', 'live', 'journey', 'path', 'experience'],
            'love': ['love', 'heart', 'passion', 'care', 'together'],
            'future': ['future', 'tomorrow', 'plan', 'vision', 'forward'],
            'growth': ['grow', 'change', 'improve', 'better', 'progress']
        }
        
        quote_lower = quote.lower()
        for category, keywords in categories.items():
            if any(keyword in quote_lower for keyword in keywords):
                return category
        return 'general'

class EmojiMatcher:
    """Matches quote categories with appropriate emojis."""
    
    def __init__(self):
        self.emoji_map = {
            'inspiration': ['✨', '💫', '🌟', '⭐', '🚀'],
            'motivation': ['💪', '🎯', '⚡', '🔥', '📈'],
            'wisdom': ['🧠', '📚', '🤔', '💡', '🎓'],
            'life': ['🌈', '🌱', '🌺', '🌞', '🦋'],
            'love': ['❤️', '💖', '💝', '💗', '💓'],
            'future': ['🔮', '🎆', '🌠', '🎇', '✨'],
            'growth': ['🌱', '🪴', '🌿', '🎋', '🌳'],
            'general': ['💭', '💫', '✨', '🌟', '💡']
        }

    def get_emoji(self, category: str) -> str:
        """Get a random emoji that matches the quote's category."""
        return random.choice(self.emoji_map.get(category, self.emoji_map['general']))

class SlackStatusUpdater:
    def __init__(self, token):
        """Initialize the Slack client with your token."""
        self.client = WebClient(token=token)
        self.quote_fetcher = QuoteFetcher()
        self.emoji_matcher = EmojiMatcher()

    def update_status(self):
        """Update Slack status with a random quote and matching emoji."""
        try:
            # Get quote and its category
            quote, category = self.quote_fetcher.get_random_quote()
            
            # Get matching emoji
            emoji = self.emoji_matcher.get_emoji(category)
            
            # Trim quote if it's too long for Slack status
            if len(quote) > 100:
                quote = quote[:97] + "..."
            
            # Get current date for the status expiration
            tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = tomorrow.timestamp() + 86400  # Add 24 hours in seconds
            
            # Update the status
            self.client.users_profile_set(
                profile={
                    "status_text": quote,
                    "status_emoji": emoji,
                    "status_expiration": int(tomorrow)
                }
            )
            print(f"Status updated successfully: {quote} {emoji}")
        except Exception as e:
            print(f"Error updating status: {e}")