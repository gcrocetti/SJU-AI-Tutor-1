FROM sju-ai-tutor-base:latest

# Copy orchestrator and aggregator agent files
COPY agents/orchestrator ${LAMBDA_TASK_ROOT}/agents/orchestrator/
COPY agents/aggregator ${LAMBDA_TASK_ROOT}/agents/aggregator/

# Copy specialized agents for integration
COPY agents/university_agent ${LAMBDA_TASK_ROOT}/agents/university_agent/
COPY agents/motivator_agent ${LAMBDA_TASK_ROOT}/agents/motivator_agent/

# Create a symlink to make the entry point available at the expected path
RUN ln -s ${LAMBDA_TASK_ROOT}/agents/orchestrator/agent.py ${LAMBDA_TASK_ROOT}/app.py

# Set the Lambda handler
CMD ["app.lambda_handler"]