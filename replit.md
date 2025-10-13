# Pimm - AI-Assisted Mental Health Platform

## Overview

Pimm is a comprehensive mental health platform that combines AI-powered therapeutic conversations with expert oversight. The system facilitates secure patient-AI interactions while providing mental health professionals with tools to monitor, review, and intervene when necessary. The platform features real-time confidence scoring, expert annotation capabilities, and a dual-interface design that serves both patients seeking support and experts providing oversight.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (October 2025)

### LangChain & LangGraph AI Implementation
Implemented a comprehensive AI service layer using LangChain and LangGraph for therapeutic conversations:

1. **AI Service Architecture (server/ai/)**:
   - **LangChain Integration**: Using gpt-5 via Replit AI Integrations (no API key needed)
   - **Therapeutic Prompts**: System prompts designed for empathetic mental health support
   - **Confidence Scoring**: 5-metric evaluation system (Empathy, Safety, Clarity, Actionability, Boundaries)
   - **LangGraph State Machine**: Handles conversation flow with crisis detection and safety routing

2. **Confidence Assessment System**:
   - Binary pass/fail evaluation at 90% threshold per metric
   - Overall score calculated as (passing metrics / total metrics) × 100
   - Structured outputs using Zod schemas for reliability
   - Temperature 0 for deterministic safety assessments

3. **Crisis Detection & Safety**:
   - Keyword-based crisis detection (suicide, self-harm, harm to others)
   - Automatic crisis response with emergency resources
   - Escalation flags for nurse and doctor review
   - Expert review triggered when confidence < 90%

4. **Backend Integration**:
   - POST `/api/conversations/:id/chat` endpoint for AI conversations
   - Saves messages with detailed confidence metrics
   - Updates conversation status based on safety assessment
   - Metric mapping by name (not index) for reliability

5. **Frontend Integration**:
   - Real-time AI chat in PatientChat component
   - Loads existing conversation history
   - React Query for state management
   - Proper error handling and loading states

6. **Technical Details**:
   - Models: gpt-5 (conversation) and gpt-5 temp=0 (scoring)
   - State management: LangGraph with typed state annotations
   - Validation: Zod schemas for structured outputs
   - Safety: Multiple layers of crisis detection and escalation

## Recent Changes (October 2025)

### UI Simplification and Confidence-First Design
Updated the expert dashboard interface to prioritize confidence scores and streamline navigation:

1. **Simplified Sidebar Navigation**:
   - Reduced sidebar items to only: Dashboard, Profile, Settings
   - Removed: Patient Cases and AI Conversations pages
   - Cleaner, more focused navigation for medical staff workflow

2. **Removed Navigation Tabs**:
   - Eliminated tab-based filtering (By Confidence, Pending Review, Active, Reviewed, All)
   - Conversations now always displayed sorted by confidence score (lowest first)
   - Added info banner explaining confidence-based ranking system

3. **Conversation Card Refinements**:
   - Removed all status badges (Pending Review, Review Required, etc.)
   - Transformed confidence display from large text to smaller clickable button
   - Confidence button shows "Pass (XX%)" or "Fail (XX%)" with appropriate icon and color
   - Clicking confidence button navigates to conversation detail view

4. **User Persona Update**:
   - Changed primary expert user from "Dr. Sarah Wilson" to "Nurse Jennifer Adams"
   - Reflects nurse-first triage workflow in medical hierarchy

5. **Dynamic Dashboard Stats**:
   - Stats cards show real-time counts from conversation data
   - Pending, Active, Reviewed, and High Priority counts update dynamically
   - High Priority determined by confidence threshold (<90% for nurses)

## System Architecture

### Frontend Architecture
The client application is built using **React with TypeScript** and follows a component-based architecture. The UI is constructed using **shadcn/ui components** built on top of **Radix UI primitives**, providing accessible and customizable interface elements. The styling system uses **Tailwind CSS** with a comprehensive design system that includes custom CSS variables for theming, supporting both light and dark modes with medical-focused color palettes.

The routing is handled by **Wouter** for lightweight client-side navigation. State management utilizes **React Query (TanStack Query)** for server state management and caching, with local component state handled through React hooks. The application supports role-based interfaces - patients see a simplified chat interface while experts access comprehensive dashboards with conversation monitoring and review capabilities.

### Backend Architecture
The server follows a **Node.js Express** architecture with TypeScript support. The application uses **ESM modules** and is configured for both development and production environments. The server includes middleware for request logging, JSON parsing, and error handling. The routing system is modular, with API routes prefixed under `/api`.

The storage layer is abstracted through an interface pattern, currently implementing an in-memory storage solution but designed to easily accommodate database implementations. The architecture supports CRUD operations for users, conversations, messages, and expert reviews.

### Database Design
The system uses **Drizzle ORM** with **PostgreSQL** for data persistence. The schema includes four main entities:

- **Users table**: Supports multiple roles (patient, expert, admin) with role-specific fields like specialization for experts
- **Conversations table**: Tracks patient-AI interactions with status management, confidence scoring, and expert review flags
- **Messages table**: Stores individual messages with sender identification, confidence scores for AI responses, and expert annotations
- **Expert Reviews table**: Manages the expert oversight workflow with status tracking and feedback mechanisms

The schema uses UUIDs for primary keys and includes proper foreign key relationships with cascading behavior.

### AI Integration & Confidence System
The platform implements a confidence scoring mechanism for AI responses, ranging from 0-100. Low confidence scores (typically below 60) trigger automatic expert review flags. The system supports expert annotations on AI responses, allowing professionals to provide guidance and corrections that improve future AI interactions.

### Authentication & Authorization
The system implements role-based access control with three user roles: patient, expert, and admin. Each role has different interface permissions and data access levels. Patients can only access their own conversations, while experts can review multiple patient cases within their scope of practice.

### Component Design System
The UI follows a medical-professional design approach with careful attention to accessibility and trust-building visual elements. The component library includes specialized elements like confidence indicators, conversation cards for expert dashboards, and chat interfaces optimized for therapeutic conversations.

The design system implements a sophisticated theming approach with CSS custom properties, allowing for consistent styling across light/dark modes while maintaining the professional medical aesthetic required for healthcare applications.

## External Dependencies

### Core Framework Dependencies
- **React 18** with TypeScript for the frontend framework
- **Express.js** for the backend server framework
- **Vite** for build tooling and development server
- **Node.js** runtime environment

### UI and Styling
- **Tailwind CSS** for utility-first styling approach
- **Radix UI** primitives for accessible component foundations
- **shadcn/ui** component library for pre-built interface elements
- **Lucide React** for consistent iconography
- **class-variance-authority** for component variant management

### Database and ORM
- **Drizzle ORM** for type-safe database operations
- **@neondatabase/serverless** for PostgreSQL database connectivity
- **Drizzle Kit** for database migrations and schema management

### State Management and Data Fetching
- **TanStack React Query** for server state management and caching
- **React Hook Form** with resolvers for form state management
- **Zod** for runtime type validation and schema validation

### Development and Build Tools
- **TypeScript** for static type checking
- **ESBuild** for production builds
- **PostCSS** with Autoprefixer for CSS processing
- **@replit/vite-plugin-runtime-error-modal** for development error handling

### Authentication and Session Management
- **connect-pg-simple** for PostgreSQL session storage
- Session management infrastructure (to be implemented)

### Utility Libraries
- **date-fns** for date manipulation and formatting
- **clsx** and **tailwind-merge** for conditional CSS class management
- **nanoid** for generating unique identifiers
- **wouter** for lightweight client-side routing