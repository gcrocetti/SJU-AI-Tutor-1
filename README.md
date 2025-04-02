# SJU-AI-Tutor
Agentic RAG system to improve student retention rates through specialized AI agents.

## Project Overview
This system uses a multi-agent approach to provide comprehensive support for university students, helping to improve retention rates through targeted assistance in different areas:

1. **University Information Agent**
   * Provides accurate information about university resources, policies, and procedures
   * Uses RAG (Retrieval Augmented Generation) to incorporate current university knowledge
   * Answers questions about courses, deadlines, requirements, and campus resources

2. **Motivator Agent (Emotional Support Specialist)**
   * Addresses emotional well-being, motivation, and stress management
   * Conducts regular check-ins to assess student morale
   * Offers stress management and test-anxiety strategies
   * Monitors for signs of severe distress and flags concerns

3. **Teacher Agent (Educational Content Specialist)**
   * Retrieves and presents syllabus and course content from vector database
   * Provides detailed educational content with proper source citations
   * Maintains conversation context to handle follow-up queries intelligently
   * Uses pattern matching to recognize references to previously discussed topics
   * Applies Socratic teaching methods to encourage critical thinking
   * Customizes responses based on conversation history and topic relevance

4. **Orchestrator Agent**
   * Routes student queries to the appropriate specialized agent(s)
   * Analyzes queries to determine intent and select the best agent(s)
   * Creates subqueries optimized for each specialized agent
   * Maintains conversation context across different agent interactions
   * Specifically routes syllabus-related queries to the Teacher Agent

5. **Aggregator Agent**
   * Combines responses from multiple agents into coherent, unified answers
   * Ensures seamless integration of factual information and emotional support
   * Preserves key information while eliminating redundancy
   * Maintains consistent tone and formatting

## Technical Architecture
The system is built on a modern, scalable architecture:

* **Frontend**: React/TypeScript-based chat interface with diagnostics dashboard
* **Backend**: Python-based agents using LangChain 0.3+ and LangGraph
* **Infrastructure**: AWS Lambda for serverless deployment, API Gateway for routing
* **Vector Store**: Pinecone for knowledge retrieval and syllabus content storage
* **LLM Integration**: OpenAI's GPT models via API
* **Search**: Google Custom Search for up-to-date information
* **Conversation Management**: Context tracking for follow-up question handling

## Agent Interaction Flow
1. User submits a query to the main chat interface
2. Orchestrator analyzes the query and determines which specialized agent(s) should handle it
3. If multiple agents are needed, the query is reformulated for each agent's specific domain
4. Specialized agents process their respective portions of the query
5. If multiple agents were used, the Aggregator combines their responses into a cohesive answer
6. Final response is returned to the user's chat interface

## Project Structure
```
SJU-AI-Tutor/
├── agents/                           # All AI agents
│   ├── common/                       # Shared code between agents
│   ├── university_agent/             # University information agent
│   ├── motivator_agent/              # Emotional support specialist
│   ├── orchestrator/                 # Orchestrator agent for routing
│   └── aggregator/                   # Aggregator for combining responses
│
├── aws/                              # AWS-related configurations
│   ├── cloudformation/               # Infrastructure as code
│   ├── lambda/                       # Lambda configurations
│   └── scripts/                      # Deployment scripts
│
├── com/                              # Common utilities and data connectors
│   └── sju/ciro/knowledge_base/      # Knowledge base integration
│
├── docker/                           # Docker configurations
│   ├── base/                         # Base image configuration
│   ├── university_agent/             # University agent image
│   ├── motivator_agent/              # Motivator agent image
│   └── orchestrator/                 # Orchestrator agent image
│
├── frontend/                         # React/TypeScript frontend
│
├── scripts/                          # Development scripts
│   ├── test_university_agent.py      # Test script for university agent
│   ├── test_motivator_agent.py       # Test script for motivator agent
│   └── test_orchestrator_agent.py    # Test script for full agent pipeline
│
└── .env.template                     # Template for environment variables
```

## Getting Started

### Prerequisites
* Python 3.10+
* Node.js 18+
* Docker
* AWS CLI (for deployment)
* OpenAI API Key
* AWS Account (for Cognito authentication and deployment)
* Google API Key and CSE ID (for external search functionality)

### Dependencies

#### Backend Dependencies
All Python dependencies are listed in the `requirements.txt` file and include:
* `langchain>=0.3.0` - LLM application framework
* `langchain-openai>=0.0.5` - LangChain OpenAI integration
* `langgraph>=0.0.16` - Agent workflow framework
* `httpx>=0.24.0` - HTTP client
* `fastapi>=0.104.1` - API framework
* `pydantic>=2.4.2` - Data validation
* `pinecone-client>=2.2.4` - Vector database client
* `httpcore>=1.0.0` - HTTP core for networking
* `uvicorn>=0.23.2` - ASGI server
* `python-dotenv>=1.0.0` - Environment variable management
* `pytest>=7.4.3` - Testing framework

#### Frontend Dependencies
The frontend requires these key packages:
* `react` and `react-dom` - UI framework
* `typescript` - Type checking
* `vite` - Build tool
* `react-router-dom` - Routing
* `aws-amplify` - AWS authentication integration
* `uuid` - Unique ID generation
* `chart.js` and `react-chartjs-2` - Data visualization

To install frontend dependencies:
```bash
cd frontend
npm install react react-dom typescript vite @vitejs/plugin-react-swc
npm install react-router-dom uuid chart.js react-chartjs-2
npm install aws-amplify  # For AWS Cognito authentication
```

### Local Development Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/SJU-AI-Tutor.git
   cd SJU-AI-Tutor
   ```

2. Set up the Python environment:
   ```bash
   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.template .env
   # Edit .env with your API keys
   ```

4. Configure AWS credentials:
   ```bash
   aws configure
   # Enter your AWS access key, secret key, region, and output format
   ```

5. Set up the frontend:
   ```bash
   cd frontend
   npm install
   
   # Add AWS Amplify for Cognito integration
   npm install aws-amplify
   
   # Start development server
   npm run dev
   ```

6. Configure AWS Amplify settings:
   Create a file at `frontend/src/aws-config.ts` with your Cognito settings:
   ```typescript
   export const awsConfig = {
     Auth: {
       region: 'us-east-2', // Your AWS region
       userPoolId: 'us-east-2_yourUserPoolId', // From Cognito console
       userPoolWebClientId: 'yourAppClientId', // From Cognito console
       authenticationFlowType: 'USER_PASSWORD_AUTH'
     }
   };
   ```

7. Test the agents locally:
   ```bash
   # Test individual agents
   python scripts/test_university_agent.py
   python scripts/test_motivator_agent.py
   python scripts/test_teacher_agent.py
   
   # Test the full agent pipeline with orchestrator
   python scripts/test_orchestrator_agent.py
   ```

### AWS Cognito Setup

Setting up AWS Cognito for authentication:

1. **Create a User Pool:**
   - Go to AWS Management Console → Amazon Cognito → User Pools → Create user pool
   - Choose "Cognito user pool" as the provider type
   - Select sign-in options: Email (recommended for SJU user emails)
   - Configure security requirements:
     - Password policy: Choose "Cognito defaults" unless you have specific requirements
     - Multi-factor authentication (MFA): Optional (recommended for production)
     - User account recovery: Enable self-service account recovery

2. **Configure Sign-Up Experience:**
   - Self-registration: Enable for development, manage for production
   - Required attributes: email, given_name (first name), family_name (last name)
   - Custom attributes: Add any SJU-specific attributes (e.g., studentId, program)
   - Verification messages: Email message for account verification

3. **Configure App Integration:**
   - App type: Public client
   - App client name: "SJU-AI-Tutor-Web-Client"
   - Authentication flows: ALLOW_USER_PASSWORD_AUTH and ALLOW_REFRESH_TOKEN_AUTH
   - Token expiration: Set appropriate values (default is fine for development)
   - Hosted UI: Disable (we're using our own UI)

4. **Review and Create:**
   - Review all settings
   - Create user pool

5. **Get User Pool Details:**
   - Note your **User Pool ID** and **App Client ID**
   - These will be used in your Amplify configuration

6. **Test User Pool (Optional):**
   - Add a test user through the AWS Console
   - You can use the AWS CLI to test authentication:
     ```bash
     aws cognito-idp admin-create-user --user-pool-id YOUR_USER_POOL_ID --username test@example.com
     aws cognito-idp admin-set-user-password --user-pool-id YOUR_USER_POOL_ID --username test@example.com --password TestPassword123! --permanent
     ```

7. **Frontend Integration:**
   - Create `frontend/src/aws-config.ts` with your Cognito details:
     ```typescript
     export const awsConfig = {
       Auth: {
         region: 'us-east-2',  // Your AWS region
         userPoolId: 'us-east-2_yourUserPoolId',
         userPoolWebClientId: 'yourAppClientId',
         authenticationFlowType: 'USER_PASSWORD_AUTH'
       }
     };
     ```
   
   - Update `frontend/src/main.tsx` to initialize Amplify:
     ```typescript
     import { Amplify } from 'aws-amplify';
     import { awsConfig } from './aws-config';
     
     // Initialize AWS Amplify
     Amplify.configure(awsConfig);
     ```
   
   - Modify the `authService.ts` as shown in the documentation to use Amplify Auth methods
   - Keep the same UI components and interaction patterns that you currently have

### Deployment
Deployment to AWS is handled through CloudFormation:

1. Package the application:
   ```bash
   cd aws/scripts
   chmod +x deploy.sh
   ./deploy.sh
   ```

2. The deploy script will:
   - Build Docker images for all agents
   - Push images to Amazon ECR
   - Deploy the CloudFormation stack
   - Set up API Gateway endpoints
   - Configure Lambda functions for all agents

## API Endpoints

After deployment, the following endpoints are available:

- `/chat` - Main endpoint that uses the Orchestrator agent (use this for the frontend)
- `/university` - Direct access to the University agent
- `/motivator` - Direct access to the Motivator agent

## Cross-Agent Collaboration

The system features advanced agent collaboration:

- The Motivator agent can request campus resource information from the University agent
- The Orchestrator determines when queries need multiple agents for comprehensive responses
- The Aggregator seamlessly combines information from different agents 

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License
This code is licensed under the Apache License, Version 2.0.