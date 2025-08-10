#!/bin/bash

# Start script for running both frontend and backend components
# of the Ciro AI Tutor system

# Color codes for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check for required commands
if ! command_exists python || ! command_exists python3; then
  echo -e "${YELLOW}Python is not found in PATH. Will use the Python from the venv once activated.${NC}"
  # Continue anyway, as we'll use the Python from the virtual environment
fi

if ! command_exists npm; then
  echo -e "${YELLOW}npm is not installed. Please install Node.js and npm.${NC}"
  exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
  echo -e "${YELLOW}No .env file found. Creating from template...${NC}"
  if [ -f ".env.template" ]; then
    cp .env.template .env
    echo -e "${GREEN}Created .env file. Please edit it to add your API keys.${NC}"
  else
    echo -e "${YELLOW}No .env.template found. You'll need to create a .env file with OPENAI_API_KEY.${NC}"
  fi
fi

# Create Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo -e "${GREEN}Creating Python virtual environment...${NC}"
  python -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
if [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
  source venv/Scripts/activate
else
  echo -e "${YELLOW}Could not find activation script. Your environment might not be set up correctly.${NC}"
  exit 1
fi

# Install Python dependencies
echo -e "${GREEN}Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Install frontend dependencies
echo -e "${GREEN}Installing frontend dependencies...${NC}"
cd frontend
npm install
cd ..

# Function to clean up processes on exit
cleanup() {
  echo -e "${GREEN}Stopping all processes...${NC}"
  pkill -P $$
  exit 0
}

# Set up trap to clean up on exit
trap cleanup EXIT INT TERM

# Start backend server
echo -e "${GREEN}Starting backend server...${NC}"
python app.py &
backend_pid=$!

# Give the backend a moment to start
sleep 2

# Start frontend development server
echo -e "${GREEN}Starting frontend development server...${NC}"
cd frontend
npm run dev &
frontend_pid=$!

echo -e "${GREEN}Both servers are running!${NC}"
echo -e "${GREEN}Backend API: http://localhost:5001${NC}"
echo -e "${GREEN}Frontend: http://localhost:3000${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"

# Wait for both processes
wait $backend_pid $frontend_pid