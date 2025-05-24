# Life Stats Dashboard

A minimalistic frontend dashboard for tracking daily life metrics and goal completion rates.

## Features

- 🎯 **Goal Completion Tracking**: Visualize how many days you've hit your goals
- 📊 **Beautiful Pie Charts**: Clean, minimalistic charts with light green/neon green theme
- 📅 **Multiple Time Periods**: View stats for week, month, or year
- 🚀 **Simple Authentication**: Username-only login (no passwords required)
- 📱 **Responsive Design**: Works on desktop and mobile

## Metrics Tracked

- 💧 Water intake (litres)
- 🍎 Calorie intake (kcal)
- 😴 Sleep hours
- ⚡ Productivity hours
- 🏃 Exercise hours

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on http://localhost:8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

### Backend Setup

Make sure the FastAPI backend is running on port 8000. The frontend will automatically proxy API requests to the backend.

## Project Structure

```
src/
├── app/
│   ├── page.tsx           # Main page with auth logic
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── components/
│   ├── Dashboard.tsx      # Main dashboard component
│   ├── LoginForm.tsx      # Authentication form
│   ├── GoalCompletionChart.tsx  # Pie chart component
│   └── PeriodSelector.tsx # Time period selector
└── lib/
    └── api.ts            # API client and types
```

## Usage

1. **Login**: Enter your username (no password needed)
2. **View Goals**: See pie charts showing goal completion for each metric
3. **Switch Periods**: Toggle between weekly, monthly, and yearly views
4. **Track Progress**: Monitor your consistency across different time periods

## Design

The dashboard features a clean, minimalistic design with:
- Light green (#D1FAE5) and neon green (#10B981) color scheme
- Responsive grid layout
- Smooth animations and transitions
- Clear typography and spacing

## Technology Stack

- **Framework**: Next.js 15 with App Router
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **API Client**: Fetch API with custom hooks
- **TypeScript**: Full type safety

## Development

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
