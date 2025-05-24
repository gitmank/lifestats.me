# Environment Variables Setup

## For Development
Create a `.env.local` file with:
```
API_URL=http://localhost:8000
```

## For Production (Vercel)
Set the environment variable in your Vercel dashboard:
```
API_URL=https://lifestats.manomay.co
```

**Note**: The `API_URL` is server-only and not exposed to the client. All API calls now go through Next.js API routes that proxy to your backend.

## Migration from Direct API Calls
- Removed: `NEXT_PUBLIC_API_URL` (client-exposed)
- Added: `API_URL` (server-only)
- Frontend now calls Next.js API routes instead of backend directly
- Better security: backend URL not exposed to clients 