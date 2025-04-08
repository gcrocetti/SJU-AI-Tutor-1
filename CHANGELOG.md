# Changelog

## April 8, 2025

### Added
- Knowledge Check Agent for generating and scoring quizzes
  - Support for 10 computer science chapters with multiple choice questions
  - Question generation using OpenAI GPT-4o
  - DynamoDB integration for tracking student progress
  - Text response evaluation for free-form knowledge checks
- Backend infrastructure for knowledge check operations
  - Quiz generation
  - Answer scoring
  - Progress tracking
- Frontend integration with Knowledge Check Agent
  - Connected frontend quiz components to backend API
  - Added user authentication integration with quiz results
  - Implemented fallback mechanisms for graceful degradation
  - Enhanced user ID tracking for quiz attempts

### Modified
- Updated university agent prompts to support knowledge check integrations
- Enhanced auth service with user ID retrieval functionality
- Updated diagnostics service with real API integration for quizzes

## Previous Changes

### Added
- Teaching Agent functionality
- Improved orchestration logic
- AWS scaffolding for future expansion

### Fixed
- Security vulnerability fixes
- UI integration with agent backend

### Added
- Temporary UI link via Flask until AWS is fully setup