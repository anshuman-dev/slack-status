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
                'url': 'https://api.quotable.io/random?tags=technology,wisdom,business,success,leadership',
                'process': lambda r: (r['content'], r['author'])
            },
            {
                'url': 'https://zenquotes.io/api/random',
                'process': lambda r: (r[0]['q'], r[0]['a'])
            }
        ]

    def _is_appropriate(self, text: str) -> bool:
        """Check if the quote is appropriate for professional settings."""
        # List of topics/words to avoid
        inappropriate_topics = [
            'black', 'white', 'race', 'gender', 'political', 'religion',
            'racist', 'sexist', 'offensive', 'controversial', 'hate',
            'drug', 'alcohol', 'nsfw', 'dating', 'gambling'
        ]
        
        text_lower = text.lower()
        return not any(topic in text_lower for topic in inappropriate_topics)

    def get_random_quote(self) -> Tuple[str, str]:
        """Fetch a random quote from one of the APIs."""
        api = random.choice(self.apis)
        try:
            response = requests.get(api['url'], timeout=5)
            response.raise_for_status()
            content = response.json()
            quote, author = api['process'](content)
            # Check if the quote is appropriate
            if not self._is_appropriate(quote):
                raise ValueError("Quote contained inappropriate content")
            return f"{quote} - {author}", self._categorize_quote(quote)
        except Exception as e:
            print(f"API Error: {e}")
            fallback_quotes = [
                ("Innovation distinguishes between a leader and a follower. - Steve Jobs", "inspiration"),
                ("The best way to predict the future is to create it. - Peter Drucker", "future"),
                ("Continuous learning is the minimum requirement for success in any field. - Brian Tracy", "growth"),
                ("Quality is not an act, it is a habit. - Aristotle", "wisdom"),
                ("The only limit to our realization of tomorrow will be our doubts of today. - Franklin D. Roosevelt", "motivation"),
                ("Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill", "motivation"),
                ("The way to get started is to quit talking and begin doing. - Walt Disney", "action"),
                ("Leadership is the capacity to translate vision into reality. - Warren Bennis", "leadership")
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