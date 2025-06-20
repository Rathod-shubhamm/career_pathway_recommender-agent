import json
import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
import os
from dotenv import load_dotenv
import requests

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# CORE DATA MODELS
# =============================================================================

class ConversationState(Enum):
    GREETING = "greeting"
    GATHERING_INFO = "gathering"
    CLARIFYING = "clarifying"
    RECOMMENDING = "recommending"
    DISCUSSING = "discussing"

@dataclass
class StudentProfile:
    interests: List[str] = field(default_factory=list)
    hobbies: List[str] = field(default_factory=list)
    subjects: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    dislikes: List[str] = field(default_factory=list)
    personality: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)

    def completeness(self) -> float:
        fields = [self.interests, self.hobbies, self.subjects, self.strengths]
        filled = sum(1 for field in fields if field)
        return filled / len(fields)

    def has_changed(self, other_snapshot: str) -> bool:
        current = json.dumps(self.__dict__, sort_keys=True)
        return current != other_snapshot

    def snapshot(self) -> str:
        return json.dumps(self.__dict__, sort_keys=True)

# =============================================================================
# FREE LLM CLIENT
# =============================================================================

class FreeLLMClient:
    def __init__(self):
        # Using Hugging Face Inference API (free tier)
        self.api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")  # Optional, can work without
        self.headers = {}
        if self.hf_token:
            self.headers["Authorization"] = f"Bearer {self.hf_token}"
        
        # Fallback to local processing if API fails
        self.use_fallback = False
        
    async def generate_response(self, prompt: str, max_tokens: int = 400, temperature: float = 0.7) -> str:
        """Generate response using free LLM or fallback logic"""
        try:
            # Try Hugging Face API first
            if not self.use_fallback:
                response = await self._call_huggingface_api(prompt, max_tokens)
                if response:
                    return response
            
            # Use fallback logic
            return self._fallback_generation(prompt)
            
        except Exception as e:
            logger.warning(f"LLM generation failed, using fallback: {str(e)}")
            return self._fallback_generation(prompt)
    
    async def _call_huggingface_api(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Call Hugging Face Inference API"""
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": 0.7,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                self.api_url, 
                headers=self.headers, 
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "").strip()
            else:
                logger.warning(f"HF API returned status {response.status_code}")
                self.use_fallback = True
                
        except Exception as e:
            logger.warning(f"HF API call failed: {str(e)}")
            self.use_fallback = True
            
        return None
    
    def _fallback_generation(self, prompt: str) -> str:
        """Rule-based fallback when LLM is unavailable"""
        prompt_lower = prompt.lower()
        
        # Extract info fallback
        if "extract student information" in prompt_lower:
            return self._extract_info_fallback(prompt)
        
        # Question generation fallback
        elif "ask" in prompt_lower and "question" in prompt_lower:
            return self._generate_questions_fallback(prompt)
        
        # Recommendations fallback
        elif "recommend" in prompt_lower and "career" in prompt_lower:
            return self._generate_recommendations_fallback(prompt)
        
        # General conversation fallback
        else:
            return self._general_conversation_fallback(prompt)
    
    def _extract_info_fallback(self, prompt: str) -> str:
        """Extract information using improved keyword matching"""
        # Extract the message from the prompt
        message_match = re.search(r'message: "(.*?)"', prompt)
        if not message_match:
            return '{"interests": [], "hobbies": [], "subjects": [], "strengths": [], "dislikes": [], "personality": [], "goals": []}'
        
        message = message_match.group(1).lower()
        
        extracted = {
            "interests": [],
            "hobbies": [],
            "subjects": [],
            "strengths": [],
            "dislikes": [],
            "personality": [],
            "goals": []
        }
        
        # Enhanced subject recognition
        subject_mapping = {
            # Sciences
            "biology": "Biology", "bio": "Biology", "life science": "Biology",
            "chemistry": "Chemistry", "chem": "Chemistry", 
            "physics": "Physics", "physical science": "Physics",
            "science": "Science", "sciences": "Science",
            
            # Mathematics
            "math": "Mathematics", "mathematics": "Mathematics", "calculus": "Mathematics",
            "algebra": "Mathematics", "geometry": "Mathematics",
            
            # Language Arts
            "english": "English", "literature": "Literature", "writing": "Writing",
            "reading": "Literature", "language": "English",
            
            # Social Studies
            "history": "History", "geography": "Geography", "social studies": "Social Studies",
            "government": "Government", "civics": "Government",
            
            # Arts
            "art": "Art", "music": "Music", "drama": "Drama", "theater": "Drama",
            "dance": "Dance", "creative": "Creative Arts",
            
            # Physical Education
            "pe": "Physical Education", "sports": "Physical Education", "gym": "Physical Education",
            "physical education": "Physical Education",
            
            # Technology
            "computer": "Computer Science", "coding": "Computer Science", "programming": "Computer Science",
            "technology": "Technology", "tech": "Technology"
        }
        
        # Check for subjects
        for keyword, subject in subject_mapping.items():
            if keyword in message:
                if subject not in extracted["subjects"]:
                    extracted["subjects"].append(subject)
        
        # Enhanced interest detection
        interest_patterns = [
            (r"interested in (.+?)(?:\.|,|!|\?|$)", "interests"),
            (r"love (.+?)(?:\.|,|!|\?|$)", "interests"),
            (r"like (.+?)(?:\.|,|!|\?|$)", "interests"),
            (r"enjoy (.+?)(?:\.|,|!|\?|$)", "interests"),
            (r"passionate about (.+?)(?:\.|,|!|\?|$)", "interests"),
            (r"fascinated by (.+?)(?:\.|,|!|\?|$)", "interests"),
        ]
        
        for pattern, category in interest_patterns:
            matches = re.findall(pattern, message)
            for match in matches:
                # Clean up the match
                clean_match = re.sub(r'\b(and|or|the|a|an)\b', '', match).strip()
                if clean_match and len(clean_match) > 2:
                    words = clean_match.split()[:3]  # Take first 3 words
                    interest = " ".join(words).title()
                    if interest not in extracted[category]:
                        extracted[category].append(interest)
        
        # Enhanced hobby keywords
        hobby_keywords = {
            "reading": "Reading", "gaming": "Gaming", "games": "Gaming",
            "painting": "Painting", "drawing": "Drawing", "sketching": "Drawing",
            "singing": "Singing", "dancing": "Dancing", 
            "cooking": "Cooking", "gardening": "Gardening",
            "photography": "Photography", "writing": "Writing",
            "swimming": "Swimming", "running": "Running",
            "hiking": "Hiking", "camping": "Camping",
            "playing": "Playing Music", "instrument": "Playing Music"
        }
        
        for keyword, hobby in hobby_keywords.items():
            if keyword in message:
                if hobby not in extracted["hobbies"]:
                    extracted["hobbies"].append(hobby)
        
        # Career goals detection
        goal_patterns = [
            r"want to be (.+?)(?:\.|,|!|\?|$)",
            r"dream of being (.+?)(?:\.|,|!|\?|$)",
            r"hope to become (.+?)(?:\.|,|!|\?|$)",
            r"aspire to be (.+?)(?:\.|,|!|\?|$)"
        ]
        
        for pattern in goal_patterns:
            matches = re.findall(pattern, message)
            for match in matches:
                clean_match = match.strip().title()
                if clean_match not in extracted["goals"]:
                    extracted["goals"].append(clean_match)
        
        return json.dumps(extracted)
    
    def _generate_questions_fallback(self, prompt: str) -> str:
        """Generate questions using predefined templates"""
        question_templates = [
            "What subjects in school do you find most engaging?",
            "What activities do you do in your free time that you really enjoy?",
            "Are there any skills you feel you're naturally good at?",
            "What kind of work environment appeals to you - working with people, working alone, or in a team?",
            "Do you prefer creative tasks or more analytical ones?",
            "What are some topics you could talk about for hours?",
            "Are there any careers you've ever been curious about?",
            "What motivates you most - helping others, solving problems, or creating things?"
        ]
        
        import random
        return random.choice(question_templates)
    
    def _generate_recommendations_fallback(self, prompt: str) -> str:
        """Generate basic career recommendations with improved matching"""
        # Extract profile info from prompt
        interests = self._extract_list_from_prompt(prompt, "Interests")
        subjects = self._extract_list_from_prompt(prompt, "Subjects")
        hobbies = self._extract_list_from_prompt(prompt, "Hobbies")
        
        all_text = " ".join(interests + subjects + hobbies).lower()
        recommendations = []
        
        # Biology/Life Sciences careers
        if any(word in all_text for word in ["biology", "life science", "living things", "animals", "plants", "genetics", "ecology", "nature"]):
            recommendations.extend([
                {
                    "title": "Biologist/Research Scientist",
                    "reason": "Your interest in biology aligns perfectly with research in living systems",
                    "education": "Bachelor's in Biology, then Master's/PhD for research roles",
                    "next_step": "Look into different biology specializations like marine biology, genetics, or ecology"
                },
                {
                    "title": "Healthcare Professional (Doctor/Nurse)",
                    "reason": "Biology knowledge is fundamental for understanding human health",
                    "education": "Pre-med courses, then medical school or nursing program",
                    "next_step": "Research medical school requirements and consider volunteering at hospitals"
                },
                {
                    "title": "Environmental Scientist",
                    "reason": "Combines biology with environmental protection and conservation",
                    "education": "Bachelor's in Environmental Science or Biology",
                    "next_step": "Learn about environmental issues and conservation organizations"
                }
            ])
        
        # Medicine/Health specific
        elif any(word in all_text for word in ["medicine", "doctor", "health", "medical", "anatomy", "physiology"]):
            recommendations.extend([
                {
                    "title": "Medical Doctor",
                    "reason": "Direct path to practicing medicine and helping patients",
                    "education": "Bachelor's degree, MCAT, medical school, residency",
                    "next_step": "Research medical specialties and volunteer at healthcare facilities"
                },
                {
                    "title": "Physical Therapist",
                    "reason": "Combines medical knowledge with hands-on patient care",
                    "education": "Bachelor's degree then Doctor of Physical Therapy program",
                    "next_step": "Shadow a physical therapist to understand the daily work"
                }
            ])
        
        # Chemistry careers
        elif any(word in all_text for word in ["chemistry", "chemical", "reactions", "compounds", "lab work"]):
            recommendations.extend([
                {
                    "title": "Chemist",
                    "reason": "Your chemistry interest opens doors to research and development",
                    "education": "Bachelor's in Chemistry, Master's/PhD for advanced roles",
                    "next_step": "Explore different chemistry fields like organic, analytical, or biochemistry"
                },
                {
                    "title": "Pharmaceutical Scientist",
                    "reason": "Combines chemistry with medicine to develop new drugs",
                    "education": "Bachelor's in Chemistry/Biology, advanced degree helpful",
                    "next_step": "Learn about drug development and pharmaceutical companies"
                }
            ])
        
        # Physics/Engineering
        elif any(word in all_text for word in ["physics", "math", "engineering", "mechanical", "electrical", "software", "computer"]):
            if "software" in all_text or "computer" in all_text or "programming" in all_text:
                recommendations.append({
                    "title": "Software Engineer",
                    "reason": "Your interest in computers and logical thinking fits programming",
                    "education": "Bachelor's in Computer Science or related field",
                    "next_step": "Start learning a programming language like Python or Java"
                })
            else:
                recommendations.append({
                    "title": "Engineer",
                    "reason": "Your interest in math and science subjects shows analytical thinking",
                    "education": "Bachelor's degree in Engineering",
                    "next_step": "Explore different engineering fields like mechanical, electrical, or civil"
                })
        
        # Creative/Arts
        elif any(word in all_text for word in ["art", "creative", "design", "drawing", "painting", "music", "writing"]):
            recommendations.extend([
                {
                    "title": "Graphic Designer",
                    "reason": "Your creative interests and artistic skills align well",
                    "education": "Bachelor's in Graphic Design or related field",
                    "next_step": "Start building a portfolio of your creative work"
                },
                {
                    "title": "Creative Professional",
                    "reason": "Many careers can utilize your artistic talents",
                    "education": "Varies by field - portfolio often more important than degree",
                    "next_step": "Explore specific creative fields like animation, web design, or illustration"
                }
            ])
        
        # Psychology/Social Sciences
        elif any(word in all_text for word in ["psychology", "people", "help", "social", "counseling", "therapy"]):
            recommendations.extend([
                {
                    "title": "Psychologist/Counselor",
                    "reason": "Your interest in understanding people and helping them",
                    "education": "Bachelor's in Psychology, then Master's/PhD for clinical work",
                    "next_step": "Learn about different psychology specializations"
                },
                {
                    "title": "Social Worker",
                    "reason": "Direct path to helping people and communities",
                    "education": "Bachelor's in Social Work or related field",
                    "next_step": "Volunteer with community organizations to gain experience"
                }
            ])
        
        # Business/General
        elif any(word in all_text for word in ["business", "management", "marketing", "finance", "economics"]):
            recommendations.append({
                "title": "Business Professional",
                "reason": "Your interest in business concepts opens many career paths",
                "education": "Bachelor's in Business Administration or related field",
                "next_step": "Explore different business areas like marketing, finance, or management"
            })
        
        # Teaching
        elif any(word in all_text for word in ["teaching", "education", "explain", "tutor"]):
            recommendations.append({
                "title": "Teacher/Educator",
                "reason": "Your interest in sharing knowledge and helping others learn",
                "education": "Bachelor's degree plus teaching certification",
                "next_step": "Consider volunteering with tutoring or mentoring programs"
            })
        
        # Default recommendations if no specific matches
        if not recommendations:
            recommendations = [
                {
                    "title": "Explore Multiple Paths",
                    "reason": "Many career options are available - let's learn more about your interests",
                    "education": "Various options depending on chosen field",
                    "next_step": "Tell me more about what specific activities or subjects excite you most"
                }
            ]
        
        # Format recommendations
        formatted = "Based on your interests, here are some career recommendations:\n\n"
        for i, rec in enumerate(recommendations[:3], 1):
            formatted += f"{i}. **{rec['title']}**\n"
            formatted += f"   Why it fits: {rec['reason']}\n"
            formatted += f"   Education: {rec['education']}\n"
            formatted += f"   Next step: {rec['next_step']}\n\n"
        
        return formatted
    
    def _general_conversation_fallback(self, prompt: str) -> str:
        """Handle general conversation"""
        responses = [
            "That's interesting! Tell me more about what specifically draws you to that.",
            "I'd love to learn more about your interests. What else do you enjoy doing?",
            "That sounds great! How do you think that might relate to potential career paths?",
            "Thanks for sharing! What other activities or subjects are you passionate about?",
            "That's wonderful! Are there any careers you've ever thought about that might involve that interest?"
        ]
        
        import random
        return random.choice(responses)
    
    def _extract_list_from_prompt(self, prompt: str, field_name: str) -> List[str]:
        """Extract list items from prompt text"""
        pattern = f"{field_name}: (.*?)(?:\\n|$)"
        match = re.search(pattern, prompt)
        if match:
            items = match.group(1).replace("None specified", "").replace("Unknown", "")
            return [item.strip() for item in items.split(",") if item.strip()]
        return []

# =============================================================================
# DYNAMIC PROMPTS
# =============================================================================

class DynamicPrompts:
    @staticmethod
    def extract_info(message: str) -> str:
        return f"""Extract student information from this message: "{message}"

Return JSON with these fields (only include what's clearly mentioned):
{{
    "interests": ["list of interests"],
    "hobbies": ["list of hobbies"], 
    "subjects": ["favorite school subjects"],
    "strengths": ["academic/personal strengths"],
    "dislikes": ["things to avoid"],
    "personality": ["personality traits"],
    "goals": ["career aspirations"]
}}

Be flexible - extract any relevant information even if it's casual conversation.
If no career-related info is found, return empty arrays for all fields."""

    @staticmethod
    def generate_questions(profile: StudentProfile, asked_questions: List[str]) -> str:
        completeness = int(profile.completeness() * 100)
        recent_questions = asked_questions[-3:] if asked_questions else []
        
        return f"""You are a career counselor. Current student info:
- Interests: {', '.join(profile.interests) or 'Unknown'}
- Hobbies: {', '.join(profile.hobbies) or 'Unknown'}
- Subjects: {', '.join(profile.subjects) or 'Unknown'}
- Completeness: {completeness}%

Ask 1-2 engaging questions to learn more. Avoid repeating: {', '.join(recent_questions)}

Focus on missing areas and be encouraging. Keep it conversational."""

    @staticmethod
    def generate_recommendations(profile: StudentProfile) -> str:
        return f"""Recommend 3-4 specific careers for this student:

Profile:
- Interests: {', '.join(profile.interests) or 'None specified'}
- Hobbies: {', '.join(profile.hobbies) or 'None specified'}
- Subjects: {', '.join(profile.subjects) or 'None specified'}
- Strengths: {', '.join(profile.strengths) or 'None specified'}

CRITICAL: Match careers directly to their specific interests. 

For each career provide:
1. Career title
2. Why it matches their interests (be specific)
3. Brief education overview
4. One next step they could take

Keep recommendations practical and achievable."""

    @staticmethod
    def handle_general_conversation(message: str, profile: StudentProfile) -> str:
        return f"""The student said: "{message}"

Current profile: {profile.__dict__}

Respond naturally as a career counselor. If they're asking questions, being casual, or discussing non-career topics, engage appropriately while gently steering toward career exploration when natural.

Be conversational and helpful. Don't force career questions if they're asking something else."""

# =============================================================================
# RATE LIMITER
# =============================================================================

class SimpleRateLimiter:
    def __init__(self, requests_per_minute: int = 10):  # Increased for free tier
        self.rpm = requests_per_minute
        self.requests = []
    
    async def wait_if_needed(self):
        now = time.time()
        self.requests = [t for t in self.requests if now - t < 60]
        
        if len(self.requests) >= self.rpm:
            sleep_time = 60 - (now - self.requests[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        self.requests.append(now)

# =============================================================================
# MAIN AGENT
# =============================================================================

class SimpleCareerAgent:
    def __init__(self, max_history: int = 8):
        self.profile = StudentProfile()
        self.state = ConversationState.GREETING
        self.conversation_history = []
        self.asked_questions = []
        self.consecutive_clarifying = 0
        self.max_history = max_history
        self.rate_limiter = SimpleRateLimiter()
        self.recommendations_given = False
        
        # Initialize free LLM client
        self.llm_client = FreeLLMClient()
        
        logger.info("Simple Career Agent initialized with Free LLM")

    def _trim_history(self):
        """Keep conversation memory within limits"""
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

    def _is_career_related_question(self, message: str) -> bool:
        """Check if message is asking about careers/recommendations"""
        career_keywords = [
            'career', 'job', 'profession', 'recommend', 'suggestion', 
            'what should i', 'advice', 'path', 'future', 'work'
        ]
        return any(keyword in message.lower() for keyword in career_keywords)

    async def process_message(self, message: str) -> Dict:
        """Main message processing with improved state management"""
        try:
            logger.info(f"Processing message in state: {self.state.value}")
            
            # Add to conversation memory
            self.conversation_history.append({
                "role": "student",
                "content": message,
                "timestamp": datetime.now().isoformat(),
                "state": self.state.value
            })
            self._trim_history()
            
            # Extract and update profile
            profile_snapshot = self.profile.snapshot()
            extracted_info = await self._extract_info(message)
            self._update_profile(extracted_info)
            
            # Reset clarifying counter if new info was added OR if it's a direct question
            if self.profile.has_changed(profile_snapshot) or self._is_career_related_question(message):
                self.consecutive_clarifying = 0
            else:
                self.consecutive_clarifying += 1
            
            # Generate response based on current state and message content
            response = await self._generate_response(message)
            
            # Add response to memory
            self.conversation_history.append({
                "role": "counselor", 
                "content": response["content"],
                "timestamp": datetime.now().isoformat(),
                "state": self.state.value
            })
            self._trim_history()
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return self._fallback_response()

    async def _extract_info(self, message: str) -> Dict:
        """Extract structured information using LLM or fallback"""
        try:
            await self.rate_limiter.wait_if_needed()
            
            prompt = DynamicPrompts.extract_info(message)
            response = await self.llm_client.generate_response(prompt, max_tokens=400, temperature=0.1)
            
            # Try to parse JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # If JSON parsing fails, return empty dict
            return {}
            
        except Exception as e:
            logger.error(f"Info extraction failed: {str(e)}")
            return {}

    def _update_profile(self, extracted_info: Dict):
        """Update student profile with new information"""
        if not extracted_info:
            return
            
        def add_unique(target_list: List[str], new_items: List[str]):
            for item in new_items:
                if item and item.lower() not in [existing.lower() for existing in target_list]:
                    target_list.append(item)
        
        add_unique(self.profile.interests, extracted_info.get("interests", []))
        add_unique(self.profile.hobbies, extracted_info.get("hobbies", []))
        add_unique(self.profile.subjects, extracted_info.get("subjects", []))
        add_unique(self.profile.strengths, extracted_info.get("strengths", []))
        add_unique(self.profile.dislikes, extracted_info.get("dislikes", []))
        add_unique(self.profile.personality, extracted_info.get("personality", []))
        add_unique(self.profile.goals, extracted_info.get("goals", []))
        
        logger.info(f"Profile updated. Completeness: {self.profile.completeness():.1%}")

    async def _generate_response(self, message: str) -> Dict:
        """Improved state management and response generation"""
        completeness = self.profile.completeness()
        
        # Handle greeting state
        if self.state == ConversationState.GREETING:
            self.state = ConversationState.GATHERING_INFO
            return self._greeting_response()
        
        # Check if user is directly asking for recommendations
        if self._is_career_related_question(message) and completeness > 0:
            self.state = ConversationState.RECOMMENDING
            response = await self._generate_recommendations()
            self.state = ConversationState.DISCUSSING
            self.recommendations_given = True
            return response
        
        # If we're in discussing state, handle follow-up questions naturally
        if self.state == ConversationState.DISCUSSING:
            return await self._handle_discussion(message)
        
        # Force recommendations if we have enough info and haven't given any yet
        if completeness >= 0.5 and not self.recommendations_given:
            self.state = ConversationState.RECOMMENDING
            response = await self._generate_recommendations()
            self.state = ConversationState.DISCUSSING
            self.recommendations_given = True
            return response
        
        # Force recommendations if stuck in clarifying loop
        if self.consecutive_clarifying > 3:
            self.state = ConversationState.RECOMMENDING
            response = await self._generate_recommendations()
            self.state = ConversationState.DISCUSSING
            self.recommendations_given = True
            self.consecutive_clarifying = 0
            return response
        
        # Default to gathering more info
        self.state = ConversationState.CLARIFYING
        return await self._generate_questions()

    async def _handle_discussion(self, message: str) -> Dict:
        """Handle conversation in discussion state"""
        try:
            await self.rate_limiter.wait_if_needed()
            
            prompt = DynamicPrompts.handle_general_conversation(message, self.profile)
            response = await self.llm_client.generate_response(prompt, max_tokens=300, temperature=0.7)
            
            return {
                "type": "discussion",
                "content": response,
                "metadata": {"completeness": int(self.profile.completeness() * 100)}
            }
            
        except Exception as e:
            logger.error(f"Discussion handling failed: {str(e)}")
            return {
                "type": "discussion",
                "content": "That's interesting! Would you like to explore any career options related to what we've discussed?",
                "metadata": {"error": True}
            }

    def _greeting_response(self) -> Dict:
        """Initial greeting with dynamic content"""
        greeting = """Hi! I'm your AI career counselor. I'm here to help you discover career paths that match your interests and strengths.

Let's start with getting to know you:
- What subjects or activities do you really enjoy?
- What do you like to do in your free time?
- Is there anything you're naturally good at?

Feel free to share whatever comes to mind - we can have a casual conversation!"""
        
        return {
            "type": "greeting",
            "content": greeting,
            "metadata": {"completeness": 0}
        }

    async def _generate_questions(self) -> Dict:
        """Generate clarifying questions using LLM or fallback"""
        try:
            await self.rate_limiter.wait_if_needed()
            
            prompt = DynamicPrompts.generate_questions(self.profile, self.asked_questions)
            questions = await self.llm_client.generate_response(prompt, max_tokens=200, temperature=0.7)
            
            self.asked_questions.append(questions)
            
            return {
                "type": "questions",
                "content": questions,
                "metadata": {"completeness": int(self.profile.completeness() * 100)}
            }
            
        except Exception as e:
            logger.error(f"Question generation failed: {str(e)}")
            return {
                "type": "questions", 
                "content": "Tell me more about what you enjoy doing! What kind of activities make you lose track of time?",
                "metadata": {"fallback": True}
            }

    async def _generate_recommendations(self) -> Dict:
        """Generate career recommendations using LLM or fallback"""
        try:
            await self.rate_limiter.wait_if_needed()
            
            prompt = DynamicPrompts.generate_recommendations(self.profile)
            recommendations = await self.llm_client.generate_response(prompt, max_tokens=800, temperature=0.6)
            
            return {
                "type": "recommendations",
                "content": recommendations,
                "metadata": {
                    "completeness": int(self.profile.completeness() * 100),
                    "profile_summary": self.profile.__dict__
                }
            }
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            return {
                "type": "recommendations",
                "content": "Based on what you've shared, I can see some potential career paths. Could you tell me a bit more about what specifically interests you so I can give better recommendations?",
                "metadata": {"error": True}
            }

    def _fallback_response(self) -> Dict:
        """Simple fallback responses"""
        fallbacks = {
            ConversationState.GREETING: "Hi! What subjects or activities do you enjoy most?",
            ConversationState.GATHERING_INFO: "Tell me about your interests and hobbies.",
            ConversationState.CLARIFYING: "What kind of activities do you find most engaging?",
            ConversationState.RECOMMENDING: "Let me suggest some careers based on your interests.",
            ConversationState.DISCUSSING: "What would you like to know more about?"
        }
        
        return {
            "type": "fallback",
            "content": fallbacks.get(self.state, "Could you tell me more about your interests?"),
            "metadata": {"error": True}
        }

    def reset(self):
        """Reset conversation state"""
        self.profile = StudentProfile()
        self.state = ConversationState.GREETING
        self.conversation_history = []
        self.asked_questions = []
        self.consecutive_clarifying = 0
        self.recommendations_given = False
        logger.info("Agent reset completed")

    def get_status(self) -> Dict:
        """Get current agent status"""
        return {
            "state": self.state.value,
            "profile_completeness": self.profile.completeness(),
            "conversation_length": len(self.conversation_history),
            "recommendations_given": self.recommendations_given,
            "profile": self.profile.__dict__
        }

# =============================================================================
# SIMPLE USAGE EXAMPLE
# =============================================================================

async def main():
    """Simple command-line interface for testing"""
    agent = SimpleCareerAgent()
    
    print("Career Counselor Agent - Free LLM Version")
    print("(type 'quit' to exit, 'reset' to restart)")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'reset':
                agent.reset()
                print("Agent: Conversation reset! Let's start fresh.")
                continue
            elif user_input.lower() == 'status':
                status = agent.get_status()
                print(f"Agent Status: {json.dumps(status, indent=2)}")
                continue
            
            if user_input:
                response = await agent.process_message(user_input)
                print(f"\nAgent: {response['content']}")
                
                if response.get('metadata', {}).get('completeness'):
                    print(f"[Profile: {response['metadata']['completeness']}% complete]")
                    
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    asyncio.run(main())