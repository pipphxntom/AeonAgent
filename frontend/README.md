# AeonAgent Frontend

Next.js frontend for the AeonAgent SaaS platform.

## Features
- Agent marketplace and catalog
- Tenant dashboard and analytics
- Real-time agent interactions
- Document upload and management
- Billing and subscription management
- Admin panel

## Tech Stack
- Next.js 14 with TypeScript
- Tailwind CSS for styling
- Zustand for state management
- React Query for API calls
- React Hook Form for form handling
- Recharts for analytics

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

3. Start the development server:
```bash
npm run dev
```

## Project Structure
- `app/`: Next.js App Router pages and layouts
- `components/`: Reusable React components
- `lib/`: Utility functions and configurations
- `stores/`: Zustand state stores
- `types/`: TypeScript type definitions
- `styles/`: Global styles and Tailwind configuration
