# Student Career Pathway Recommender using Groq & Llama 3.1
# This implementation demonstrates building an intelligent career counseling system
# that understands student interests and provides personalized recommendations

import json
import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import asyncio
from groq import Groq
from pydantic import BaseModel, Field, validator
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# DATA MODELS
# =============================================================================

class AcademicStrength(Enum):
    EXCELLENT = "excellent"
    STRONG = "strong"
    AVERAGE = "average"
    DEVELOPING = "developing"

class InterestCategory(Enum):
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    SOCIAL = "social"
    HANDS_ON = "hands_on"
    ENTREPRENEURIAL = "entrepreneurial"
    NATURE = "nature"
    TECHNOLOGY = "technology"

class CareerField(Enum):
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    CREATIVE_ARTS = "creative_arts"
    BUSINESS = "business"
    EDUCATION = "education"
    SCIENCE_RESEARCH = "science_research"
    TRADES_CRAFTS = "trades_crafts"
    SOCIAL_SERVICES = "social_services"
    SPORTS_FITNESS = "sports_fitness"
    ENVIRONMENT = "environment"

@dataclass
class StudentProfile:
    interests: List[str] = field(default_factory=list)
    hobbies: List[str] = field(default_factory=list)
    favorite_subjects: List[str] = field(default_factory=list)
    academic_strengths: List[str] = field(default_factory=list)
    academic_challenges: List[str] = field(default_factory=list)
    overall_academic_level: Optional[AcademicStrength] = None
    dislikes: List[str] = field(default_factory=list)
    work_environment_preferences: List[str] = field(default_factory=list)
    personality_traits: List[str] = field(default_factory=list)
    career_goals: List[str] = field(default_factory=list)
    life_goals: List[str] = field(default_factory=list)

    def calculate_completeness(self) -> float:
        score = 0.0
        total_possible = 8.0
        if self.interests: score += 1.0
        if self.hobbies: score += 1.0
        if self.favorite_subjects: score += 1.0
        if self.academic_strengths: score += 1.0
        if self.dislikes: score += 1.0
        if self.personality_traits: score += 1.0
        if self.career_goals: score += 1.0
        if self.work_environment_preferences: score += 1.0
        return min(score / total_possible, 1.0)

    def get_dominant_interest_categories(self) -> List[InterestCategory]:
        category_counts = {category: 0 for category in InterestCategory}
        all_interests = self.interests + self.hobbies + self.favorite_subjects
        category_keywords = {
            InterestCategory.CREATIVE: ['art', 'music', 'draw', 'paint', 'design', 'creative', 'write'],
            InterestCategory.ANALYTICAL: ['math', 'logic', 'puzzle', 'analyze', 'research', 'data'],
            InterestCategory.SOCIAL: ['people', 'help', 'team', 'communicate', 'counsel', 'teach'],
            InterestCategory.HANDS_ON: ['build', 'fix', 'craft', 'make', 'construct', 'repair'],
            InterestCategory.ENTREPRENEURIAL: ['business', 'lead', 'manage', 'sell', 'organize'],
            InterestCategory.NATURE: ['nature', 'environment', 'animal', 'outdoor', 'plant'],
            InterestCategory.TECHNOLOGY: ['computer', 'code', 'program', 'tech', 'digital', 'software']
        }
        for interest in all_interests:
            interest_lower = interest.lower()
            for category, keywords in category_keywords.items():
                if any(keyword in interest_lower for keyword in keywords):
                    category_counts[category] += 1
        return sorted(
            [cat for cat, count in category_counts.items() if count > 0],
            key=lambda cat: category_counts[cat],
            reverse=True
        )

class ConversationState(Enum):
    GREETING = "greeting"
    GATHERING_BASIC_INFO = "gathering_basic"
    EXPLORING_ACADEMICS = "exploring_academics"
    CLARIFYING_PREFERENCES = "clarifying"
    GENERATING_RECOMMENDATIONS = "recommending"
    DISCUSSING_CAREERS = "discussing"
    PLANNING_NEXT_STEPS = "planning"

class CareerRecommendation(BaseModel):
    career_title: str = Field(description="Specific career title")
    field: CareerField = Field(description="Broader career field")
    match_confidence: float = Field(ge=0.0, le=1.0, description="How confident we are in this match")
    reasons_for_match: List[str] = Field(description="Specific reasons this career fits")
    education_requirements: str = Field(description="Education needed for this career")
    alternative_pathways: List[str] = Field(description="Different ways to enter this field")
    job_market_outlook: str = Field(description="Employment prospects")
    typical_work_environment: str = Field(description="What the day-to-day looks like")
    salary_range: str = Field(description="Earning potential")
    skills_to_develop: List[str] = Field(description="Key skills to work on")
    next_steps: List[str] = Field(description="Concrete actions student can take")

# =============================================================================
# PROMPT ENGINEERING
# =============================================================================

class LlamaPrompts:
    EXTRACT_STUDENT_INFO = '''You are an expert career counselor analyzing student responses. Your job is to carefully extract information about their interests, abilities, and preferences.

Student's message: "{message}"

Please analyze this message and extract any information about:
- Interests (things they enjoy or are curious about)
- Hobbies (activities they do in their free time)
- Academic subjects they mentioned (favorite or challenging)
- Academic performance indicators (grades, ease of learning)
- Dislikes or things they want to avoid
- Personality traits (introverted/extroverted, creative, logical, etc.)
- Career goals or aspirations
- Work environment preferences

Return your analysis as JSON in this exact format:
{{
    "interests": ["list of interests found"],
    "hobbies": ["list of hobbies found"],
    "favorite_subjects": ["school subjects they like"],
    "academic_strengths": ["subjects or skills they're good at"],
    "academic_challenges": ["subjects or areas they struggle with"],
    "dislikes": ["things they want to avoid"],
    "personality_traits": ["traits you can infer"],
    "career_goals": ["any career aspirations mentioned"],
    "work_preferences": ["work environment preferences"],
    "confidence_level": 0.8,
    "missing_info": ["what else would be helpful to know"]
}}

Only include information that is clearly stated or strongly implied. Be conservative in your interpretations.'''

    GENERATE_CLARIFYING_QUESTIONS = '''You are a friendly career counselor who needs to learn more about a student to provide better guidance.

Current knowledge about the student:
- Interests: {interests}
- Hobbies: {hobbies}
- Favorite subjects: {subjects}
- Academic strengths: {strengths}
- Things they dislike: {dislikes}
- Profile completeness: {completeness}%

Based on what you know, generate 2-3 thoughtful questions that would help you understand this student better and provide more personalized career recommendations.

Your questions should be:
- Open-ended and encouraging
- Specific enough to get useful information
- Appropriate for a high school student
- Focused on filling the biggest gaps in understanding

Format your response as a friendly counselor would speak, introducing the questions naturally.

Example good questions:
- "What kind of activities make you lose track of time because you enjoy them so much?"
- "When you work on projects, do you prefer working alone or with others?"
- "Are there any careers you've heard about that sound interesting, even if you're not sure what they involve?"

Generate questions that would be most helpful for this specific student.'''

    GENERATE_CAREER_RECOMMENDATIONS = '''You are an expert career counselor providing personalized career recommendations to a student.

Student Profile:
- Interests: {interests}
- Hobbies: {hobbies}
- Favorite subjects: {subjects}
- Academic strengths: {strengths}
- Academic challenges: {challenges}
- Dislikes: {dislikes}
- Personality traits: {personality}
- Career goals: {goals}

Based on this profile, recommend 3-4 specific careers that would be excellent matches. For each career, provide:

1. **Career Title**: Specific job title
2. **Why it's a great match**: Connect to their specific interests and strengths
3. **Education path**: What they need to study
4. **Work environment**: What a typical day looks like
5. **Growth potential**: Job outlook and advancement opportunities
6. **Next steps**: Specific actions they can take now

Make sure your recommendations:
- Are realistic given their academic profile
- Avoid areas they've indicated they dislike
- Connect clearly to their stated interests
- Include both traditional and emerging career options
- Consider different education pathways (college, trade school, etc.)

Present your recommendations in an encouraging, detailed way that helps the student understand why each career might be perfect for them.'''

    EXPLAIN_SPECIFIC_CAREER = '''You are a career counselor explaining a specific career to a student who has shown interest.

Career to explain: {career}
Student's interests: {interests}
Student's strengths: {strengths}

Provide a comprehensive overview of this career, including:

1. **What they actually do**: Day-to-day responsibilities and tasks
2. **Why it matches their profile**: Specific connections to their interests and strengths
3. **Education and training**: Different pathways to enter this field
4. **Work environment**: Where they work, who they work with
5. **Career progression**: How they can advance and grow
6. **Compensation**: Realistic salary expectations
7. **Job market**: Current demand and future outlook
8. **Skills to develop**: What they should start working on now
9. **Ways to explore**: How they can learn more or get experience

Make this information specific and actionable. Help them understand if this career might truly be a good fit and what they need to do to pursue it.'''

# =============================================================================
# RATE LIMITING
# =============================================================================

class RateLimiter:
    def __init__(self, requests_per_minute: int = 25):
        self.requests_per_minute = requests_per_minute
        self.request_times = []
    async def wait_if_needed(self):
        now = time.time()
        self.request_times = [t for t in self.request_times if now - t < 60]
        if len(self.request_times) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0])
            if sleep_time > 0:
                logger.info(f"Rate limiting: waiting {sleep_time:.1f} seconds")
                await asyncio.sleep(sleep_time)
        self.request_times.append(now)

# =============================================================================
# MAIN CONVERSATION MANAGER
# =============================================================================

class CareerCounselorAgent:
    def __init__(self, groq_api_key: str, max_history: int = 10):
        self.client = Groq(api_key=groq_api_key)
        self.rate_limiter = RateLimiter()
        self.student_profile = StudentProfile()
        self.conversation_state = ConversationState.GREETING
        self.conversation_history = []
        self.session_context = {}
        self.model = "llama-3.1-8b-instant"
        self.max_history = max_history
        logger.info("Career Counselor Agent initialized with Groq/Llama 3.1")

    def _trim_conversation_history(self):
        """Keep only the most recent messages based on max_history setting"""
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
            logger.info(f"Trimmed conversation history to {self.max_history} messages")

    def reset_context(self):
        """Reset the agent's context and start fresh"""
        self.conversation_history = []
        self.student_profile = StudentProfile()
        self.conversation_state = ConversationState.GREETING
        self.session_context = {}
        logger.info("Agent context has been reset")

    async def process_message(self, message: str) -> Dict:
        try:
            logger.info(f"Processing message in state: {self.conversation_state.value}")
            
            # Add message to history
            self.conversation_history.append({
                "role": "student",
                "content": message,
                "timestamp": datetime.now().isoformat(),
                "state": self.conversation_state.value
            })
            
            # Trim history if needed
            self._trim_conversation_history()
            
            extracted_info = await self._extract_student_information(message)
            self._update_student_profile(extracted_info)
            response = await self._generate_response()
            
            # Add response to history
            self.conversation_history.append({
                "role": "counselor",
                "content": response["content"],
                "timestamp": datetime.now().isoformat(),
                "state": self.conversation_state.value,
                "metadata": response.get("metadata", {})
            })
            
            # Trim history again after adding response
            self._trim_conversation_history()
            
            # If we've provided recommendations, optionally clear some context
            if self.conversation_state == ConversationState.DISCUSSING_CAREERS:
                self.session_context = {}
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return self._create_fallback_response()

    async def _extract_student_information(self, message: str) -> Dict:
        try:
            await self.rate_limiter.wait_if_needed()
            prompt = LlamaPrompts.EXTRACT_STUDENT_INFO.format(message=message)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting structured information from natural language. Always return valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            content = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                logger.warning("No JSON found in extraction response")
                return {}
        except Exception as e:
            logger.error(f"Error extracting information: {str(e)}")
            return {}

    def _update_student_profile(self, extracted_info: Dict):
        if not extracted_info:
            return
        def add_unique(target_list: List[str], new_items: List[str]):
            for item in new_items:
                if item.lower() not in [existing.lower() for existing in target_list]:
                    target_list.append(item)
        add_unique(self.student_profile.interests, extracted_info.get("interests", []))
        add_unique(self.student_profile.hobbies, extracted_info.get("hobbies", []))
        add_unique(self.student_profile.favorite_subjects, extracted_info.get("favorite_subjects", []))
        add_unique(self.student_profile.academic_strengths, extracted_info.get("academic_strengths", []))
        add_unique(self.student_profile.academic_challenges, extracted_info.get("academic_challenges", []))
        add_unique(self.student_profile.dislikes, extracted_info.get("dislikes", []))
        add_unique(self.student_profile.personality_traits, extracted_info.get("personality_traits", []))
        add_unique(self.student_profile.career_goals, extracted_info.get("career_goals", []))
        add_unique(self.student_profile.work_environment_preferences, extracted_info.get("work_preferences", []))
        logger.info(f"Profile updated. Completeness: {self.student_profile.calculate_completeness():.1%}")

    async def _generate_response(self) -> Dict:
        completeness = self.student_profile.calculate_completeness()
        if self.conversation_state == ConversationState.GREETING:
            self.conversation_state = ConversationState.GATHERING_BASIC_INFO
            return self._create_greeting_response()
        elif completeness < 0.6:
            if self.conversation_state != ConversationState.CLARIFYING_PREFERENCES:
                self.conversation_state = ConversationState.CLARIFYING_PREFERENCES
            return await self._generate_clarifying_questions()
        elif completeness >= 0.6:
            if self.conversation_state != ConversationState.GENERATING_RECOMMENDATIONS:
                self.conversation_state = ConversationState.GENERATING_RECOMMENDATIONS
            return await self._generate_career_recommendations()
        else:
            return await self._generate_clarifying_questions()

    def _create_greeting_response(self) -> Dict:
        greeting = """Hi there! I'm your AI career counselor, and I'm really excited to help you explore potential career paths that might be perfect for you.\n\nI'd love to learn about what makes you tick! Could you start by telling me:\n- What subjects or activities do you genuinely enjoy?\n- What do you like to do in your free time?\n- Are there any particular strengths you've noticed about yourself?\n\nThere are no wrong answers here - I'm just trying to understand what might make you happy and successful in your future career. What would you like to share first?"""
        return {
            "type": "greeting",
            "content": greeting,
            "metadata": {
                "profile_completeness": 0.0,
                "next_expected": "student_interests"
            }
        }

    async def _generate_clarifying_questions(self) -> Dict:
        try:
            await self.rate_limiter.wait_if_needed()
            interests = ", ".join(self.student_profile.interests) if self.student_profile.interests else "Not specified"
            hobbies = ", ".join(self.student_profile.hobbies) if self.student_profile.hobbies else "Not specified"
            subjects = ", ".join(self.student_profile.favorite_subjects) if self.student_profile.favorite_subjects else "Not specified"
            strengths = ", ".join(self.student_profile.academic_strengths) if self.student_profile.academic_strengths else "Not specified"
            dislikes = ", ".join(self.student_profile.dislikes) if self.student_profile.dislikes else "Not specified"
            completeness = int(self.student_profile.calculate_completeness() * 100)
            prompt = LlamaPrompts.GENERATE_CLARIFYING_QUESTIONS.format(
                interests=interests,
                hobbies=hobbies,
                subjects=subjects,
                strengths=strengths,
                dislikes=dislikes,
                completeness=completeness
            )
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a friendly, encouraging career counselor asking thoughtful questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            questions = response.choices[0].message.content
            return {
                "type": "clarifying_questions",
                "content": questions,
                "metadata": {
                    "profile_completeness": completeness,
                    "missing_areas": self._identify_missing_information()
                }
            }
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return {
                "type": "clarifying_questions",
                "content": "I'd love to learn more about you! What are some activities that you really enjoy doing, and what school subjects do you find most interesting or easiest?",
                "metadata": {"fallback": True}
            }

    async def _generate_career_recommendations(self) -> Dict:
        try:
            await self.rate_limiter.wait_if_needed()
            profile_data = {
                "interests": ", ".join(self.student_profile.interests) or "General curiosity",
                "hobbies": ", ".join(self.student_profile.hobbies) or "Various activities",
                "subjects": ", ".join(self.student_profile.favorite_subjects) or "Mixed subjects",
                "strengths": ", ".join(self.student_profile.academic_strengths) or "Learning and growing",
                "challenges": ", ".join(self.student_profile.academic_challenges) or "Normal learning challenges",
                "dislikes": ", ".join(self.student_profile.dislikes) or "None specified",
                "personality": ", ".join(self.student_profile.personality_traits) or "Developing personality",
                "goals": ", ".join(self.student_profile.career_goals) or "Exploring options"
            }
            prompt = LlamaPrompts.GENERATE_CAREER_RECOMMENDATIONS.format(**profile_data)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert career counselor providing personalized, encouraging, and realistic career recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1500
            )
            recommendations = response.choices[0].message.content
            self.conversation_state = ConversationState.DISCUSSING_CAREERS
            return {
                "type": "career_recommendations",
                "content": recommendations,
                "metadata": {
                    "profile_completeness": int(self.student_profile.calculate_completeness() * 100),
                    "dominant_interests": [cat.value for cat in self.student_profile.get_dominant_interest_categories()],
                    "student_profile": self._get_profile_summary()
                }
            }
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return self._create_fallback_response()

    def _identify_missing_information(self) -> List[str]:
        missing = []
        if not self.student_profile.interests and not self.student_profile.hobbies:
            missing.append("interests_and_hobbies")
        if not self.student_profile.academic_strengths:
            missing.append("academic_strengths")
        if not self.student_profile.personality_traits:
            missing.append("personality_preferences")
        if not self.student_profile.work_environment_preferences:
            missing.append("work_environment")
        if not self.student_profile.dislikes:
            missing.append("things_to_avoid")
        return missing

    def _get_profile_summary(self) -> Dict:
        return {
            "interests": self.student_profile.interests,
            "hobbies": self.student_profile.hobbies,
            "favorite_subjects": self.student_profile.favorite_subjects,
            "academic_strengths": self.student_profile.academic_strengths,
            "personality_traits": self.student_profile.personality_traits,
            "career_goals": self.student_profile.career_goals,
            "completeness": self.student_profile.calculate_completeness(),
            "dominant_interest_categories": [cat.value for cat in self.student_profile.get_dominant_interest_categories()]
        }

    def _create_fallback_response(self) -> Dict:
        return {
            "type": "fallback",
            "content": (
                "I'm having a bit of trouble processing that right now. Could you tell me more about what interests you or what you enjoy doing? "
                "I'm here to help you explore career options, so anything you share about your favorite activities, subjects, or goals will be really helpful!"
            ),
            "metadata": {"error": True}
        }

# =============================================================================
# FASTAPI APP SETUP
# =============================================================================

app = FastAPI(title="Student Career Pathway Recommender API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    logger.error("GROQ_API_KEY not found in environment variables")
    raise ValueError("GROQ_API_KEY is required")

agent = CareerCounselorAgent(groq_api_key=groq_api_key)

class MessageRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"message": "Student Career Pathway Recommender API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/chat")
async def chat(request: MessageRequest):
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        response = await agent.process_message(request.message)
        return {
            "success": True,
            "response": response["content"],
            "metadata": response.get("metadata", {}),
            "type": response.get("type", "unknown")
        }
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/reset")
async def reset():
    try:
        agent.reset_context()
        return {"success": True, "message": "Conversation context has been reset"}
    except Exception as e:
        logger.error(f"Error in reset endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/profile")
async def get_profile():
    try:
        return {
            "success": True,
            "profile": agent._get_profile_summary(),
            "state": agent.conversation_state.value
        }
    except Exception as e:
        logger.error(f"Error in profile endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "student_career_path_recommender:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 