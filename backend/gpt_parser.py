"""
GPT Parser for extracting structured intent from transcribed text.
Uses OpenAI's GPT-3.5 to parse user intent and extract mood, genre, and activity.
"""

import json
from typing import Dict, Any
from openai import OpenAI
from loguru import logger
from config import Config

class IntentParser:
    """Parser for extracting structured intent from text using GPT-3.5."""
    
    def __init__(self):
        """Initialize the GPT parser."""
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        logger.info("Initialized GPT parser")
    
    def parse_intent(self, transcript: str) -> Dict[str, Any]:
        """
        Parse user intent from transcribed text.
        
        Args:
            transcript: Transcribed text from audio
            
        Returns:
            Dictionary containing parsed intent information
        """
        try:
            logger.info(f"Parsing intent from transcript: {transcript[:100]}...")
            
            system_prompt = """
            Generate 2-3 search queries for Spotify based on the user's request.
            
            Use field filters when relevant:
            - artist:"name" for artists
            - track:"name" for songs  
            - year:YYYY or year:YYYY-YYYY for time periods
            - genre:"name" for genres
            
            Examples:
            - "romantic pop year:1980-1989"
            - "artist:Queen rock"
            - "track:Bohemian Rhapsody"
            - "genre:jazz year:1950-1960"
            
            Return ONLY valid JSON:
            {
              "search_queries": ["query1", "query2", "query3"]
            }
            """
            
            user_prompt = f"""
            Please analyze this user request and extract the music preferences:
            
            "{transcript}"
            
            Return only a valid JSON object with the extracted information.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Extract and parse JSON response
            content = response.choices[0].message.content.strip()
            
            # Clean and parse JSON response
            try:
                # Remove markdown code blocks if present
                if content.startswith("```json"):
                    content = content[7:]
                elif content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                
                content = content.strip()
                
                parsed_intent = json.loads(content)
                
                # Validate that search_queries is present and properly formatted
                if 'search_queries' not in parsed_intent:
                    raise RuntimeError("GPT response missing required 'search_queries' field")
                
                if not isinstance(parsed_intent['search_queries'], list):
                    raise RuntimeError("GPT response 'search_queries' must be an array")
                
                if not parsed_intent['search_queries']:
                    raise RuntimeError("GPT response 'search_queries' array is empty")
                
                logger.info(f"search_queries: {parsed_intent.get('search_queries')}")
                logger.info("Successfully parsed intent from transcript")
                logger.debug(f"Parsed intent: {parsed_intent}")
                
                return parsed_intent
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response from GPT-3.5 API: {e}")
                logger.error(f"Raw GPT response content: {content}")
                raise RuntimeError(f"Invalid JSON response from GPT-3.5 API: {e}")
                
        except Exception as e:
            logger.error(f"GPT-3.5 API request failed: {e}")
            raise RuntimeError(f"GPT-3.5 API error: {e}")
    
 