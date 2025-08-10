FROM sju-ai-tutor-base:latest

# Copy motivator agent specific files
COPY agents/motivator_agent ${LAMBDA_TASK_ROOT}/agents/motivator_agent/

# Create a symlink to make the entry point available at the expected path
RUN ln -s ${LAMBDA_TASK_ROOT}/tutor/motivator_agent/agent.py ${LAMBDA_TASK_ROOT}/app.py

# Set the Lambda handler
CMD ["app.lambda_handler"]