import React, { useState } from 'react';
import Header from './components/Header';
import LandingSection from './components/LandingSection';
import ChatInterface from './components/ChatInterface';
import RecommendationsSection from './components/RecommendationsSection';
import { careerAPI } from './services/api';

interface CareerRecommendation {
  title: string;
  category: string;
  match: number;
  description: string;
  skills: string[];
  outlook: string;
  salaryRange: string;
  reasoning: string;
}

type AppState = 'landing' | 'chat' | 'recommendations';

function App() {
  const [currentState, setCurrentState] = useState<AppState>('landing');
  const [recommendations, setRecommendations] = useState<CareerRecommendation[]>([]);
  const [originalQuery, setOriginalQuery] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const handleGetStarted = () => {
    setCurrentState('chat');
  };

  const handleQuerySubmit = async (query: string) => {
    setOriginalQuery(query);
    setIsLoading(true);
    
    try {
      // The ChatInterface component handles the actual API communication
      // This callback is triggered when career recommendations are received
      const mockRecommendations = await generateMockRecommendationsFromAPI(query);
      setRecommendations(mockRecommendations);
      setCurrentState('recommendations');
    } catch (error) {
      console.error('Error processing query:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewSearch = async () => {
    try {
      await careerAPI.resetConversation();
      setCurrentState('landing');
      setRecommendations([]);
      setOriginalQuery('');
    } catch (error) {
      console.error('Error resetting conversation:', error);
      // Still allow UI reset even if API call fails
      setCurrentState('landing');
      setRecommendations([]);
      setOriginalQuery('');
    }
  };

  // This function parses the AI response and converts it to our recommendation format
  const generateMockRecommendationsFromAPI = async (query: string): Promise<CareerRecommendation[]> => {
    try {
      // Get the current profile to extract recommendations
      const profileResponse = await careerAPI.getProfile();
      
      // For now, we'll create mock recommendations based on the profile
      // In a more advanced implementation, you could parse the AI's response
      // or have the backend return structured recommendation data
      
      const mockCareers: CareerRecommendation[] = [];
      const profile = profileResponse.profile;
      
      // Generate recommendations based on interests
      if (profile.interests.some(interest => 
        interest.toLowerCase().includes('technology') || 
        interest.toLowerCase().includes('coding') ||
        interest.toLowerCase().includes('computer')
      )) {
        mockCareers.push({
          title: 'Software Engineer',
          category: 'Technology',
          match: 94,
          description: 'Design and develop software applications, systems, and platforms using various programming languages and technologies.',
          skills: ['Programming', 'Problem Solving', 'System Design', 'Debugging'],
          outlook: 'Excellent (22% growth)',
          salaryRange: '$85,000 - $150,000',
          reasoning: 'Your interest in technology and coding aligns perfectly with software engineering roles.'
        });
      }
      
      if (profile.interests.some(interest => 
        interest.toLowerCase().includes('help') || 
        interest.toLowerCase().includes('teach') ||
        interest.toLowerCase().includes('education')
      )) {
        mockCareers.push({
          title: 'Educational Technology Specialist',
          category: 'Education & Technology',
          match: 89,
          description: 'Develop and implement technology solutions in educational settings, helping teachers and students leverage digital tools.',
          skills: ['Teaching', 'Technology Integration', 'Curriculum Development', 'Training'],
          outlook: 'Good (8% growth)',
          salaryRange: '$55,000 - $85,000',
          reasoning: 'Your desire to help others combined with technology interests makes this an ideal match.'
        });
      }
      
      if (profile.interests.some(interest => 
        interest.toLowerCase().includes('creative') || 
        interest.toLowerCase().includes('design') ||
        interest.toLowerCase().includes('art')
      )) {
        mockCareers.push({
          title: 'UX/UI Designer',
          category: 'Design & Technology',
          match: 91,
          description: 'Create user-centered designs for digital products, focusing on usability, accessibility, and visual appeal.',
          skills: ['Design Thinking', 'Prototyping', 'User Research', 'Visual Design'],
          outlook: 'Very Good (13% growth)',
          salaryRange: '$65,000 - $120,000',
          reasoning: 'Your creative interests align well with user experience design roles.'
        });
      }

      // Default recommendation if no specific matches
      if (mockCareers.length === 0) {
        mockCareers.push({
          title: 'Business Analyst',
          category: 'Business',
          match: 78,
          description: 'Analyze business processes and requirements to help organizations improve efficiency and achieve their goals.',
          skills: ['Analysis', 'Communication', 'Problem Solving', 'Project Management'],
          outlook: 'Good (7% growth)',
          salaryRange: '$65,000 - $95,000',
          reasoning: 'Based on your profile, business analysis offers a versatile career path that combines analytical thinking with business strategy.'
        });
      }

      return mockCareers;
    } catch (error) {
      console.error('Error generating recommendations from API:', error);
      // Return fallback recommendations
      return [{
        title: 'Career Exploration Needed',
        category: 'General',
        match: 50,
        description: 'Continue chatting with the AI counselor to get more specific recommendations.',
        skills: ['Self-reflection', 'Research', 'Exploration'],
        outlook: 'Always positive',
        salaryRange: 'Varies by field',
        reasoning: 'Keep exploring your interests and talking with the AI counselor to discover your ideal career path.'
      }];
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <Header />
      
      {currentState === 'landing' && (
        <LandingSection onGetStarted={handleGetStarted} />
      )}
      
      {currentState === 'chat' && (
        <ChatInterface onSubmit={handleQuerySubmit} isLoading={isLoading} />
      )}
      
      {currentState === 'recommendations' && (
        <RecommendationsSection 
          recommendations={recommendations}
          onNewSearch={handleNewSearch}
          originalQuery={originalQuery}
        />
      )}
    </div>
  );
}

export default App;