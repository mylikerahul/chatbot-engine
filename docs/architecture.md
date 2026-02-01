# Project Architecture

## Overview
This project follows a modular, service-based architecture to keep the codebase
clean, testable, and scalable.

## High-Level Flow
User / Extension  
→ run.py  
→ app/main.py  
→ services (AI logic)  
→ response back to client

## Key Principles
- Separation of concerns
- Environment-based configuration
- Easy testability
- Minimal coupling between modules

## Folder Responsibilities

- app/
  Core application logic
- services/
  AI / business logic
- utils/
  Helper and common utilities
- data/
  Local storage / mock data
- tests/
  Automated tests
