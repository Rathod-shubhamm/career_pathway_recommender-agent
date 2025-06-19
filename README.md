# Student Career Pathway Recommender

An AI-powered career counseling application that helps students discover suitable career paths through natural conversation.

## Features

- **Natural Language Interface**: Chat with an AI career counselor using natural conversation
- **Personalized Recommendations**: Get career suggestions based on your interests, skills, and goals
- **Real-time Analysis**: AI analyzes your responses and asks follow-up questions for better understanding
- **Comprehensive Career Information**: Detailed information about recommended careers including salary, outlook, and required skills

## Architecture

### Frontend (React + TypeScript)
- Modern React application with TypeScript
- Tailwind CSS for styling
- Real-time chat interface
- Responsive design

### Backend (Python + FastAPI)
- FastAPI web framework
- Groq API integration with Llama 3.1 model
- Intelligent conversation management
- Student profile analysis and career matching

## Setup Instructions

### Prerequisites
- Node.js (v16 or higher)
- Python 3.8+
- Groq API key

### Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

3. **Run the backend server:**
   ```bash
   python student_career_path_recommender.py
   ```
   
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```
   
   The frontend will be available at `http://localhost:5173`

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/chat` - Send message to AI counselor
- `POST /api/reset` - Reset conversation context
- `GET /api/profile` - Get current student profile

## Usage

1. **Start the Application**: Make sure both backend and frontend servers are running
2. **Begin Conversation**: Click "Start Career Discovery" and begin chatting with the AI
3. **Natural Interaction**: Describe your interests, hobbies, academic strengths, and career goals
4. **Follow-up Questions**: The AI will ask clarifying questions to better understand you
5. **Get Recommendations**: Receive personalized career recommendations with detailed information
6. **Explore Further**: Ask follow-up questions about specific careers or start a new conversation

## Example Conversations

**Student**: "I love coding and math, but I'm also interested in helping people. What careers might suit me?"

**AI Counselor**: "That's a great combination! Your interest in coding and math shows strong analytical skills, while your desire to help people suggests you'd thrive in roles that have social impact. Can you tell me more about what kind of helping appeals to you? For example, do you enjoy teaching others, solving problems that benefit communities, or working directly with people one-on-one?"

## Technology Stack

### Frontend
- React 18
- TypeScript
- Tailwind CSS
- Vite
- Lucide React (icons)

### Backend
- Python 3.8+
- FastAPI
- Groq API (Llama 3.1)
- Pydantic
- Uvicorn

## Development

### Frontend Development
```bash
npm run dev    # Start development server
npm run build  # Build for production
npm run lint   # Run ESLint
```

### Backend Development
```bash
python student_career_path_recommender.py  # Run with auto-reload
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.