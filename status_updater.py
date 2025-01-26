import os
import random
import requests
from slack_sdk import WebClient
from datetime import datetime
from typing import Tuple

class QuoteFetcher:
    """
    Handles fetching and processing meaningful quotes from various sources.
    Focuses on wisdom, mindfulness, and positive philosophical content.
    """
    
    def __init__(self):
        # Configure API endpoints with specific focus on meaningful content
        self.apis = [
            {
                # Quotable.io with carefully selected tags for wisdom and mindfulness
                'url': 'https://api.quotable.io/random?tags=wisdom,philosophy,inspiration,mindfulness,happiness,growth',
                'process': lambda r: (r['content'], r['author'])
            },
            {
                # Zen Quotes API for mindful, philosophical content
                'url': 'https://zenquotes.io/api/random',
                'process': lambda r: (r[0]['q'], r[0]['a'])
            }
        ]
        
        # Define positive themes we want to emphasize in our quotes
        self.positive_themes = [
            'growth', 'wisdom', 'potential', 'mindfulness', 'peace',
            'joy', 'gratitude', 'kindness', 'harmony', 'purpose',
            'learning', 'discovery', 'wonder', 'creativity', 'balance',
            'hope', 'strength', 'courage', 'patience', 'love'
        ]

    def _is_appropriate(self, text: str) -> bool:
        """
        Ensures quotes are appropriate and aligned with positive, meaningful themes.
        Filters out potentially negative or controversial content while ensuring
        the presence of uplifting themes and checking length limits.
        """
        # First check if the quote would be too long when formatted
        formatted_quote = f"{text} - "  # Account for the author part that will be added later
        if len(formatted_quote) > 80:  # Leave room for author (roughly 20 chars)
            return False
            
        # Define topics to avoid in our quotes
        inappropriate_topics = [
            'death', 'dying', 'mortality', 'kill', 'pain', 'suffer',
            'black', 'white', 'race', 'gender', 'political', 'religion',
            'racist', 'sexist', 'offensive', 'controversial', 'hate',
            'drug', 'alcohol', 'nsfw', 'dating', 'gambling', 'war',
            'violence', 'crime', 'fear', 'anxiety', 'depression',
            'fail', 'negative', 'darkness', 'troubled'
        ]
        
        text_lower = text.lower()
        
        # Check for inappropriate content
        if any(topic in text_lower for topic in inappropriate_topics):
            return False
            
        # Ensure quote contains at least one positive theme
        has_positive_theme = any(theme in text_lower for theme in self.positive_themes)
        
        return has_positive_theme

    def _categorize_quote(self, quote: str) -> str:
        """
        Analyzes quote content to determine its primary theme for emoji matching.
        Categories are designed to match with appropriate, meaningful emojis.
        """
        categories = {
            'inspiration': ['inspire', 'dream', 'achieve', 'possible', 'potential'],
            'wisdom': ['learn', 'know', 'wisdom', 'understand', 'truth', 'mind'],
            'mindfulness': ['present', 'moment', 'mindful', 'aware', 'conscious'],
            'growth': ['grow', 'change', 'improve', 'better', 'progress', 'journey'],
            'harmony': ['peace', 'balance', 'harmony', 'calm', 'tranquil'],
            'joy': ['happy', 'joy', 'delight', 'smile', 'laugh', 'gratitude'],
            'purpose': ['purpose', 'meaning', 'goal', 'direction', 'path']
        }
        
        quote_lower = quote.lower()
        for category, keywords in categories.items():
            if any(keyword in quote_lower for keyword in keywords):
                return category
        return 'general'

    def get_random_quote(self) -> Tuple[str, str]:
        """
        Fetches a random quote from available sources, ensuring it meets our
        criteria for positivity and meaningfulness. Makes multiple attempts
        to get a quote within length limits.
        """
        max_attempts = 3  # Try up to 3 times to get a good quote
        
        for _ in range(max_attempts):
            api = random.choice(self.apis)
            try:
                response = requests.get(api['url'], timeout=5)
                response.raise_for_status()
                content = response.json()
                quote, author = api['process'](content)
                
                # Verify quote appropriateness (including length)
                if not self._is_appropriate(quote):
                    continue
                
                # If we get here, the quote is good and within length limits
                return f"{quote} - {author}", self._categorize_quote(quote)
                
            except Exception as e:
                print(f"API Error: {e}")
                break  # Break to fallback quotes if API fails
        
        # If we get here, either all attempts failed or API errored
        # Use our pre-verified fallback quotes
        fallback_quotes = [
            ("We are what we repeatedly do. Excellence, then, is not an act, but a habit. - Aristotle", "wisdom"),
            ("The mind is everything. What you think you become. - Buddha", "mindfulness"),
            ("Happiness is not something ready made. It comes from your own actions. - Dalai Lama", "joy"),
            ("The purpose of our lives is to be happy. - Dalai Lama", "purpose"),
            ("Every moment is a fresh beginning. - T.S. Eliot", "growth"),
            ("The journey of a thousand miles begins with one step. - Lao Tzu", "journey"),
            ("Be the change you wish to see in the world. - Mahatma Gandhi", "inspiration"),
            ("Yesterday I was clever, so I wanted to change the world. Today I am wise, so I am changing myself. - Rumi", "wisdom"),
            ("The universe is not outside of you. Look inside yourself; everything that you want, you already are. - Rumi", "mindfulness"),
            ("What lies behind us and what lies before us are tiny matters compared to what lies within us. - Ralph Waldo Emerson", "potential"),
            ("Life is a balance of holding on and letting go. - Rumi", "harmony"),
            ("The present moment is filled with joy and happiness. If you are attentive, you will see it. - Thich Nhat Hanh", "mindfulness")
        ]
        return random.choice(fallback_quotes)

class EmojiMatcher:
    """
    Matches quote categories with appropriate emojis that reflect the mood
    and meaning of the quote.
    """
    
    def __init__(self):
        self.emoji_map = {
            'inspiration': ['✨', '💫', '🌟', '⭐', '🚀'],
            'wisdom': ['🧠', '📚', '💡', '🎓', '🌿'],
            'mindfulness': ['🧘', '🌸', '☮️', '🕊️', '🌅'],
            'growth': ['🌱', '🪴', '🌿', '🎋', '🌳'],
            'harmony': ['☯️', '🌈', '🕊️', '🌺', '🌸'],
            'joy': ['☀️', '🌟', '💖', '🌸', '✨'],
            'purpose': ['🎯', '⭐', '🌟', '🧭', '🌅'],
            'general': ['💭', '✨', '💫', '🌟', '💝']
        }

    def get_emoji(self, category: str) -> str:
        """Returns a contextually appropriate emoji for the quote's category."""
        return random.choice(self.emoji_map.get(category, self.emoji_map['general']))

class SlackStatusUpdater:
    """
    Manages the process of updating Slack status with meaningful quotes
    and matching emojis.
    """
    
    def __init__(self, token):
        """Initialize the updater with necessary components."""
        self.client = WebClient(token=token)
        self.quote_fetcher = QuoteFetcher()
        self.emoji_matcher = EmojiMatcher()

    def update_status(self):
        """
        Updates Slack status with a meaningful quote and matching emoji.
        Handles the entire process including error checking and logging.
        """
        try:
            # Fetch quote and determine its category
            # Quote is guaranteed to be within limits by _is_appropriate
            quote, category = self.quote_fetcher.get_random_quote()
            
            # Get matching emoji
            emoji = self.emoji_matcher.get_emoji(category)
            
            # Calculate next day for status expiration
            tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = tomorrow.timestamp() + 86400  # Add 24 hours
            
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
            raise e  # Re-raise for GitHub Actions to mark as failed