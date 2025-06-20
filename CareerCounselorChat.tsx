import React, { useState, useRef, useEffect } from 'react';
import { Send, RotateCcw, User, Bot, Loader2 } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  type?: string;
}

interface AgentResponse {
  type: string;
  content: string;
  metadata?: Record<string, any>;
}

// Improved mock agent with better state management
class MockCareerAgent {
  private state = 'greeting';
  private questionCount = 0;
  private profile = {
    interests: [] as string[],
    subjects: [] as string[],
    strengths: [] as string[],
    hobbies: [] as string[]
  };
  private hasGivenRecommendations = false;

  async processMessage(message: string): Promise<AgentResponse> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 800));

    // Initial greeting
    if (this.state === 'greeting') {
      this.state = 'gathering';
      return {
        type: 'greeting',
        content: `Hi! I'm your AI career counselor. I'm here to help you discover career paths that match your interests and strengths.

To get started, tell me:
- What subjects do you enjoy most in school?
- What do you like to do in your free time?
- Is there anything you're particularly good at?

Share whatever comes to mind!`
      };
    }

    // Extract information from user message
    this._extractInformation(message);

    // If we're in discussion state and have given recommendations
    if (this.state === 'discussing' && this.hasGivenRecommendations) {
      return this._handleDiscussion(message);
    }

    // Check if we have enough information for recommendations
    const totalInfo = this.profile.interests.length + this.profile.subjects.length + 
                     this.profile.strengths.length + this.profile.hobbies.length;

    // Generate recommendations if we have enough info or asked enough questions
    if (totalInfo >= 2 || this.questionCount >= 3) {
      this.state = 'discussing';
      this.hasGivenRecommendations = true;
      return this._generateRecommendations();
    }

    // Ask follow-up questions
    this.questionCount++;
    return this._askFollowUpQuestion();
  }

  private _extractInformation(message: string) {
    const messageLower = message.toLowerCase();
    
    // Extract subjects
    const subjects = ['biology', 'chemistry', 'physics', 'math', 'mathematics', 'english', 'history', 'art', 'music', 'science', 'computer science', 'psychology', 'sociology'];
    subjects.forEach(subject => {
      if (messageLower.includes(subject) && !this.profile.subjects.some(s => s.toLowerCase() === subject)) {
        this.profile.subjects.push(subject.charAt(0).toUpperCase() + subject.slice(1));
      }
    });

    // Extract interests/hobbies
    const interests = ['reading', 'writing', 'sports', 'technology', 'computers', 'helping people', 'animals', 'environment', 'music', 'art', 'drawing', 'painting', 'cooking', 'gaming', 'research', 'teaching'];
    interests.forEach(interest => {
      if (messageLower.includes(interest) && !this.profile.interests.some(i => i.toLowerCase() === interest)) {
        this.profile.interests.push(interest.charAt(0).toUpperCase() + interest.slice(1));
      }
    });

    // Extract strengths
    const strengths = ['problem solving', 'creative', 'analytical', 'communication', 'leadership', 'teamwork', 'detail-oriented', 'organized'];
    strengths.forEach(strength => {
      if (messageLower.includes(strength.replace(' ', '')) || messageLower.includes(strength)) {
        if (!this.profile.strengths.some(s => s.toLowerCase() === strength)) {
          this.profile.strengths.push(strength.charAt(0).toUpperCase() + strength.slice(1));
        }
      }
    });

    // Extract common hobby phrases
    if (messageLower.includes('free time') || messageLower.includes('hobby') || messageLower.includes('hobbies')) {
      const hobbyKeywords = ['reading', 'sports', 'music', 'art', 'gaming', 'cooking', 'traveling'];
      hobbyKeywords.forEach(hobby => {
        if (messageLower.includes(hobby) && !this.profile.hobbies.some(h => h.toLowerCase() === hobby)) {
          this.profile.hobbies.push(hobby.charAt(0).toUpperCase() + hobby.slice(1));
        }
      });
    }
  }

  private _askFollowUpQuestion(): AgentResponse {
    const questions = [
      "That's great! What other subjects or activities really capture your attention?",
      "Tell me more about what you're naturally good at - what do friends or family often ask for your help with?",
      "When you imagine your ideal work environment, what comes to mind? Do you prefer working with people, data, creative projects, or something else?",
      "What kind of impact would you like to make in your career? Do you want to help people, solve problems, create things, or discover new knowledge?"
    ];

    const questionIndex = Math.min(this.questionCount - 1, questions.length - 1);
    return {
      type: 'questions',
      content: questions[questionIndex],
      metadata: { questionCount: this.questionCount }
    };
  }

  private _generateRecommendations(): AgentResponse {
    let recommendations = "Based on what you've shared, here are some career paths that align with your profile:\n\n";
    let careerCount = 0;

    // Biology/Science careers
    if (this.profile.subjects.some(s => s.toLowerCase().includes('biology')) || 
        this.profile.interests.some(i => i.toLowerCase().includes('science'))) {
      recommendations += `${++careerCount}. **Biologist/Research Scientist**\n`;
      recommendations += "   - Why it fits: Perfect match for your biology interests\n";
      recommendations += "   - Field: Life Sciences\n";
      recommendations += "   - Next steps: Consider biology or related science degree\n\n";

      recommendations += `${++careerCount}. **Medical Doctor**\n`;
      recommendations += "   - Why it fits: Combines biology knowledge with helping people\n";
      recommendations += "   - Field: Healthcare\n";
      recommendations += "   - Next steps: Research pre-med requirements and MCAT prep\n\n";
    }

    // Math/Analytical careers
    if (this.profile.subjects.some(s => s.toLowerCase().includes('math')) || 
        this.profile.strengths.some(s => s.toLowerCase().includes('analytical'))) {
      recommendations += `${++careerCount}. **Data Scientist**\n`;
      recommendations += "   - Why it fits: Perfect for analytical minds who love math\n";
      recommendations += "   - Field: Technology/Analytics\n";
      recommendations += "   - Next steps: Learn programming (Python/R) and statistics\n\n";
    }

    // Art/Creative careers
    if (this.profile.subjects.some(s => s.toLowerCase().includes('art')) || 
        this.profile.interests.some(i => ['art', 'drawing', 'painting', 'music'].includes(i.toLowerCase()))) {
      recommendations += `${++careerCount}. **Graphic Designer**\n`;
      recommendations += "   - Why it fits: Great for creative minds\n";
      recommendations += "   - Field: Creative Arts\n";
      recommendations += "   - Next steps: Build a portfolio and learn design software\n\n";
    }

    // Technology careers
    if (this.profile.interests.some(i => ['technology', 'computers', 'computer science'].includes(i.toLowerCase()))) {
      recommendations += `${++careerCount}. **Software Developer**\n`;
      recommendations += "   - Why it fits: Perfect for tech enthusiasts\n";
      recommendations += "   - Field: Technology\n";
      recommendations += "   - Next steps: Learn programming languages and build projects\n\n";
    }

    // Psychology/Helping careers
    if (this.profile.subjects.some(s => s.toLowerCase().includes('psychology')) || 
        this.profile.interests.some(i => i.toLowerCase().includes('helping people'))) {
      recommendations += `${++careerCount}. **Psychologist/Counselor**\n`;
      recommendations += "   - Why it fits: Great for those who want to help others\n";
      recommendations += "   - Field: Mental Health/Social Services\n";
      recommendations += "   - Next steps: Psychology degree and relevant certifications\n\n";
    }

    // Default recommendations if no specific matches
    if (careerCount === 0) {
      recommendations += "1. **Teacher/Educator**\n";
      recommendations += "   - Why it fits: Great for sharing knowledge and helping others grow\n";
      recommendations += "   - Field: Education\n";
      recommendations += "   - Next steps: Education degree and teaching certification\n\n";

      recommendations += "2. **Project Manager**\n";
      recommendations += "   - Why it fits: Good for organized, communication-focused individuals\n";
      recommendations += "   - Field: Business/Management\n";
      recommendations += "   - Next steps: Business degree and project management certification\n\n";
    }

    recommendations += "Would you like to explore any of these careers in more detail, or would you like me to suggest other options based on different aspects of your interests?";

    return {
      type: 'recommendations',
      content: recommendations,
      metadata: { 
        careersCount: careerCount,
        profile: this.profile 
      }
    };
  }

  private _handleDiscussion(message: string): AgentResponse {
    const messageLower = message.toLowerCase();

    // Check for specific career interest
    if (messageLower.includes('tell me more') || messageLower.includes('learn more') || 
        messageLower.includes('details') || messageLower.includes('explore')) {
      return {
        type: 'discussion',
        content: "I'd be happy to provide more details! Which specific career caught your interest? I can share information about:\n\n• Education requirements and typical degree paths\n• Day-to-day responsibilities and work environment\n• Salary expectations and job market outlook\n• Skills you should start developing now\n• Internship and experience opportunities\n\nJust let me know which career you'd like to explore further!"
      };
    }

    // Check for request for different options
    if (messageLower.includes('other') || messageLower.includes('different') || 
        messageLower.includes('more options') || messageLower.includes('something else')) {
      return {
        type: 'discussion',
        content: "Of course! I can suggest different career paths. To give you better recommendations, could you tell me:\n\n• Are there any specific industries that interest you?\n• Do you prefer working with people, data, or hands-on projects?\n• Are you interested in careers that involve travel, remote work, or specific locations?\n• What's most important to you: creativity, stability, high income, helping others, or intellectual challenge?\n\nShare what appeals to you and I'll suggest some different options!"
      };
    }

    // Default discussion response
    return {
      type: 'discussion',
      content: "That's great that you're thinking about your career options! Here are some ways I can help you further:\n\n• **Explore specific careers** - Get detailed info about education, daily tasks, and career prospects\n• **Discover new options** - Find careers you might not have considered\n• **Plan your next steps** - Get actionable advice for high school and college\n• **Compare careers** - Understand pros and cons of different paths\n\nWhat would be most helpful for you right now?"
    };
  }

  reset() {
    this.state = 'greeting';
    this.questionCount = 0;
    this.profile = { interests: [], subjects: [], strengths: [], hobbies: [] };
    this.hasGivenRecommendations = false;
  }

  getProfile() {
    return this.profile;
  }
}

const CareerCounselorChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [agent] = useState(() => new MockCareerAgent());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Send initial greeting
    handleInitialGreeting();
  }, []);

  const handleInitialGreeting = async () => {
    setIsLoading(true);
    try {
      const response = await agent.processMessage('');
      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: response.content,
        timestamp: new Date(),
        type: response.type
      };
      setMessages([assistantMessage]);
    } catch (error) {
      console.error('Error getting initial greeting:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputValue;
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await agent.processMessage(currentInput);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.content,
        timestamp: new Date(),
        type: response.type
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error processing message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "I apologize, but I'm having trouble processing your message right now. Could you please try again?",
        timestamp: new Date(),
        type: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    agent.reset();
    setMessages([]);
    setInputValue('');
    handleInitialGreeting();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200 p-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">Career Counselor AI</h1>
              <p className="text-sm text-gray-500">Discover your perfect career path</p>
            </div>
          </div>
          <button
            onClick={handleReset}
            className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Reset</span>
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex items-start space-x-3 ${
                message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                message.role === 'user' 
                  ? 'bg-gradient-to-r from-green-500 to-emerald-600' 
                  : 'bg-gradient-to-r from-blue-500 to-indigo-600'
              }`}>
                {message.role === 'user' ? (
                  <User className="w-4 h-4 text-white" />
                ) : (
                  <Bot className="w-4 h-4 text-white" />
                )}
              </div>
              <div className={`flex-1 max-w-3xl ${
                message.role === 'user' ? 'text-right' : ''
              }`}>
                <div className={`inline-block p-4 rounded-2xl shadow-sm ${
                  message.role === 'user'
                    ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white'
                    : 'bg-white text-gray-800 border border-gray-200'
                }`}>
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">
                    {message.content}
                  </div>
                </div>
                <div className={`text-xs text-gray-500 mt-1 ${
                  message.role === 'user' ? 'text-right' : ''
                }`}>
                  {message.timestamp.toLocaleTimeString([], { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1">
                <div className="inline-block p-4 rounded-2xl bg-white border border-gray-200 shadow-sm">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                    <span className="text-sm text-gray-600">Thinking...</span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-end space-x-3">
            <div className="flex-1">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Share your interests, favorite subjects, or ask about careers..."
                className="w-full p-3 border border-gray-300 rounded-xl resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                rows={1}
                style={{ minHeight: '44px', maxHeight: '120px' }}
                disabled={isLoading}
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              className="flex-shrink-0 w-11 h-11 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl hover:from-blue-600 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          <div className="text-xs text-gray-500 mt-2 text-center">
            Press Enter to send • Shift+Enter for new line
          </div>
        </div>
      </div>
    </div>
  );
};

export default CareerCounselorChat;