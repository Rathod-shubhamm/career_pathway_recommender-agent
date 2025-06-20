# Career Counselor AI

A modern, interactive web application that helps students discover career paths aligned with their interests, strengths, and academic preferences. Built with React, TypeScript, and Tailwind CSS, featuring an intelligent conversational AI agent.

## 🌟 Features

- **Interactive Chat Interface**: Engaging conversation flow with a career counseling AI
- **Smart Profile Building**: Automatically extracts and builds student profiles from natural conversation
- **Personalized Recommendations**: Provides tailored career suggestions based on individual interests and strengths
- **Beautiful UI/UX**: Modern, responsive design with smooth animations and micro-interactions
- **State Management**: Intelligent conversation flow that avoids loops and repetitive responses
- **Real-time Feedback**: Dynamic typing indicators and conversation state tracking

## 🚀 Live Demo

Visit the deployed application: [https://amazing-rolypoly-a7ceb6.netlify.app](https://amazing-rolypoly-a7ceb6.netlify.app)

## 🛠️ Technology Stack

### Frontend
- **React 18** - Modern React with hooks and functional components
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework for rapid styling
- **Lucide React** - Beautiful, customizable icons
- **Vite** - Fast build tool and development server

### AI Agent (Python Backend)
- **Python 3.8+** - Core programming language
- **OpenAI API** - Advanced language model integration
- **Asyncio** - Asynchronous programming for better performance
- **Dataclasses** - Clean data structure management
- **JSON** - Structured data handling

## 📁 Project Structure

```
career-counselor-ai/
├── src/
│   ├── components/
│   │   └── CareerCounselorChat.tsx    # Main chat interface component
│   ├── App.tsx                        # Root application component
│   ├── main.tsx                       # Application entry point
│   └── index.css                      # Global styles
├── scripts/
│   └── improved_career_agent.py       # Python AI agent implementation
├── public/                            # Static assets
├── dist/                             # Built application files
└── README.md                         # Project documentation
```

## 🚀 Getting Started

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+ (for AI agent)
- OpenAI API key (optional, has fallback mode)

### Frontend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd career-counselor-ai
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Open your browser**
   Navigate to `http://localhost:5173`

### AI Agent Setup (Optional)

The frontend includes a mock agent for demonstration. To use the full Python AI agent:

1. **Install Python dependencies**
   ```bash
   pip install openai python-dotenv requests asyncio
   ```

2. **Set up environment variables**
   Create a `.env` file:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   HUGGINGFACE_TOKEN=your_hf_token_here  # Optional
   ```

3. **Run the Python agent**
   ```bash
   python scripts/improved_career_agent.py
   ```

## 🎯 How It Works

### Conversation Flow

1. **Greeting**: Welcomes students and explains the process
2. **Information Gathering**: Asks engaging questions about interests, subjects, and strengths
3. **Profile Building**: Intelligently extracts and categorizes student information
4. **Recommendations**: Provides 3-4 tailored career suggestions with detailed explanations
5. **Discussion**: Handles follow-up questions and provides additional career exploration

### Key Features

#### Smart Information Extraction
- Automatically identifies subjects, interests, hobbies, and strengths from natural conversation
- Avoids repetitive questions by tracking what information has been gathered
- Uses both AI-powered and rule-based extraction methods

#### Intelligent State Management
- Prevents conversation loops with consecutive clarifying question limits
- Transitions smoothly between gathering information and providing recommendations
- Handles various conversation scenarios (direct questions, casual chat, etc.)

#### Personalized Career Matching
- Maps student interests to relevant career fields
- Provides specific, actionable recommendations rather than generic suggestions
- Includes education requirements and next steps for each career

## 🎨 Design Philosophy

### User Experience
- **Conversational**: Natural, friendly interaction that feels like talking to a real counselor
- **Non-intimidating**: Casual approach that encourages students to share openly
- **Informative**: Provides valuable, actionable career guidance
- **Engaging**: Beautiful interface with smooth animations and clear visual hierarchy

### Technical Excellence
- **Type Safety**: Full TypeScript implementation for robust development
- **Performance**: Optimized React components with proper state management
- **Accessibility**: Semantic HTML and keyboard navigation support
- **Responsive**: Works seamlessly across desktop, tablet, and mobile devices

## 🔧 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## 🌐 Deployment

The application is automatically deployed to Netlify. For manual deployment:

1. **Build the application**
   ```bash
   npm run build
   ```

2. **Deploy the `dist` folder** to your preferred hosting service

## 🤖 AI Agent Features

### Conversation States
- **Greeting**: Initial welcome and explanation
- **Gathering Info**: Collecting student information through questions
- **Clarifying**: Follow-up questions for missing information
- **Recommending**: Generating personalized career suggestions
- **Discussing**: Handling follow-up questions and exploration

### Profile Management
- **Dynamic Extraction**: Pulls information from natural conversation
- **Completeness Tracking**: Monitors how much information has been gathered
- **Change Detection**: Identifies when new information is added
- **Structured Storage**: Organizes information into categories (interests, subjects, strengths, etc.)

### Career Matching Engine
- **Field Mapping**: Connects student interests to career domains
- **Specific Recommendations**: Provides concrete career titles rather than generic categories
- **Educational Pathways**: Includes degree requirements and next steps
- **Fallback Logic**: Works even without external AI services

## 🔮 Future Enhancements

- **Backend Integration**: Connect frontend to Python AI agent via API
- **User Accounts**: Save conversation history and recommendations
- **Career Database**: Expand career information with salary data, job outlook, etc.
- **Assessment Tools**: Add personality and skills assessments
- **Resource Library**: Include links to educational programs and career resources
- **Multi-language Support**: Expand accessibility to non-English speakers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for providing advanced language model capabilities
- The React and TypeScript communities for excellent tooling
- Tailwind CSS for making beautiful designs accessible
- Lucide for providing beautiful, consistent icons

## 📞 Support

If you encounter any issues or have questions:

1. Check the existing issues in the repository
2. Create a new issue with detailed information
3. For urgent matters, contact the development team

---

**Built with ❤️ for students exploring their career futures**
