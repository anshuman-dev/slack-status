import os
import random
import requests
from slack_sdk import WebClient
from datetime import datetime
from typing import Tuple

class QuoteFetcher:
    """
    Handles fetching and processing meaningful quotes from various sources.
    Combines tech wisdom, leadership insights, and pop culture references.
    """
    
    def __init__(self):
        # Configure API endpoints focusing on tech and leadership content
        self.apis = [
            {
                # Quotable.io with tech and leadership focused tags
                'url': 'https://api.quotable.io/random?tags=technology,science,success,leadership,innovation,business,inspiration',
                'process': lambda r: (r['content'], r['author'])
            },
            {
                # Zen Quotes API for additional wisdom
                'url': 'https://zenquotes.io/api/random',
                'process': lambda r: (r[0]['q'], r[0]['a'])
            }
        ]
        
        # Define themes we want to emphasize in our quotes
        self.positive_themes = [
            'innovation', 'leadership', 'technology', 'success', 'growth',
            'courage', 'wisdom', 'power', 'victory', 'excellence',
            'creativity', 'determination', 'strength', 'progress', 'vision',
            'achievement', 'inspiration', 'discovery', 'breakthrough', 'triumph'
        ]

    def _is_appropriate(self, text: str) -> bool:
        """
        Ensures quotes are appropriate, positive, and within length limits.
        Filters out negative content while ensuring uplifting themes.
        """
        # First check if the quote would be too long when formatted
        formatted_quote = f"{text} - "  # Account for the author part
        if len(formatted_quote) > 80:  # Leave room for author (roughly 20 chars)
            return False
            
        # Define topics to avoid
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
        Categories cover both tech and entertainment themes.
        """
        categories = {
            'tech': ['code', 'program', 'developer', 'engineer', 'system', 'data'],
            'innovation': ['innovate', 'create', 'invent', 'build', 'design', 'future'],
            'leadership': ['lead', 'guide', 'inspire', 'achieve', 'vision', 'success'],
            'wisdom': ['learn', 'know', 'understand', 'truth', 'mind', 'think'],
            'power': ['strength', 'force', 'power', 'strong', 'mighty', 'valor'],
            'victory': ['win', 'conquer', 'achieve', 'triumph', 'succeed', 'accomplish'],
            'journey': ['path', 'way', 'road', 'journey', 'quest', 'adventure']
        }
        
        quote_lower = quote.lower()
        for category, keywords in categories.items():
            if any(keyword in quote_lower for keyword in keywords):
                return category
        return 'general'

    def get_random_quote(self) -> Tuple[str, str]:
        """
        Fetches a random quote, making multiple attempts to get one within length limits.
        Falls back to curated quotes from tech and entertainment if API fails.
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
                
                return f"{quote} - {author}", self._categorize_quote(quote)
                
            except Exception as e:
                print(f"API Error: {e}")
                break

        # Carefully curated fallback quotes combining tech, leadership, and pop culture
        fallback_quotes = [
            # Tech Leadership
            ("Innovation distinguishes between a leader and a follower. - Steve Jobs", "innovation"),
            ("Move fast and learn things. - Meta Engineering", "tech"),
            ("Done is better than perfect. - Sheryl Sandberg", "leadership"),
            ("Make it work, make it right, make it fast. - Kent Beck", "tech"),
            ("First solve the problem, then write the code. - John Johnson", "tech"),
            ("Stay hungry, stay foolish. - Steve Jobs", "innovation"),
            ("Talk is cheap. Show me the code. - Linus Torvalds", "tech"),
            
            # Game of Thrones
            ("Chaos isn't a pit. Chaos is a ladder. - Littlefinger", "wisdom"),
            ("The man who passes the sentence should swing the sword. - Ned Stark", "leadership"),
            ("I am not a politician, I am a queen. - Daenerys Targaryen", "power"),
            ("The night is dark and full of terrors, but the fire burns them all away. - Melisandre", "victory"),
            
            # Star Wars
            ("Do. Or do not. There is no try. - Yoda", "wisdom"),
            ("Never tell me the odds. - Han Solo", "courage"),
            ("The Force will be with you. Always. - Obi-Wan Kenobi", "power"),
            ("In my experience, there's no such thing as luck. - Obi-Wan Kenobi", "wisdom"),
            
            # Lord of the Rings
            ("All we have to decide is what to do with the time given us. - Gandalf", "wisdom"),
            ("Even the smallest person can change the course of the future. - Galadriel", "innovation"),
            ("There's some good in this world, and it's worth fighting for. - Sam", "victory"),
            
            # Marvel
            ("I am Iron Man. - Tony Stark", "power"),
            ("With great power comes great responsibility. - Uncle Ben", "leadership"),
            ("I can do this all day. - Steve Rogers", "determination"),
            
            # Tech Shows/Movies
            ("I am not a robot. I just speak in code. - Silicon Valley", "tech"),
            ("Sometimes it's better to be a warrior in a garden than a gardener in a war. - Mr. Robot", "wisdom"),
            ("It's not a bug – it's an undocumented feature. - Programming Wisdom", "tech"),
            
            # Modern Tech Leaders
            ("The best way to predict the future is to invent it. - Alan Kay", "innovation"),
            ("Code is poetry. - WordPress", "tech"),
            ("Think different. - Apple", "innovation")
        ]
        return random.choice(fallback_quotes)

class EmojiMatcher:
    """
    Matches quote categories with appropriate emojis that reflect the mood
    and meaning of the quote.
    """
    
    def __init__(self):
        self.emoji_map = {
            'tech': ['💻', '⚡', '🤖', '🚀', '💡'],
            'innovation': ['✨', '💫', '🌟', '⭐', '🔮'],
            'leadership': ['👑', '🎯', '🦁', '⚔️', '🛡️'],
            'wisdom': ['🧠', '📚', '🎓', '🌿', '🔮'],
            'power': ['⚡', '💪', '🔥', '⚔️', '✨'],
            'victory': ['🏆', '👑', '⭐', '🌟', '🔥'],
            'journey': ['🧭', '🗺️', '⭐', '🌠', '🚀'],
            'general': ['💫', '✨', '⭐', '🌟', '💝']
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
