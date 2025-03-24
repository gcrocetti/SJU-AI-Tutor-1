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

3. **Orchestrator Agent**
   * Routes student queries to the appropriate specialized agent(s)
   * Analyzes queries to determine intent and select the best agent(s)
   * Creates subqueries optimized for each specialized agent
   * Maintains conversation context across different agent interactions

4. **Aggregator Agent**
   * Combines responses from multiple agents into coherent, unified answers
   * Ensures seamless integration of factual information and emotional support
   * Preserves key information while eliminating redundancy
   * Maintains consistent tone and formatting

## Technical Architecture
The system is built on a modern, scalable architecture:

* **Frontend**: React/TypeScript-based chat interface with diagnostics dashboard
* **Backend**: Python-based agents using LangChain 0.3+ and LangGraph
* **Infrastructure**: AWS Lambda for serverless deployment, API Gateway for routing
* **Vector Store**: Pinecone for knowledge retrieval
* **LLM Integration**: OpenAI's GPT models via API
* **Search**: Google Custom Search for up-to-date information

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
* Google API Key and CSE ID

### Local Development Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/SJU-AI-Tutor.git
   cd SJU-AI-Tutor
   ```

2. Set up the Python environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.template .env
   # Edit .env with your API keys
   ```

4. Set up the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. Test the agents locally:
   ```bash
   # Test individual agents
   python scripts/test_university_agent.py
   python scripts/test_motivator_agent.py
   
   # Test the full agent pipeline with orchestrator
   python scripts/test_orchestrator_agent.py
   ```

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