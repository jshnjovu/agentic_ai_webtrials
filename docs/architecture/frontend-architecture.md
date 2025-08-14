# Frontend Architecture

## Component Architecture

**Component Organization:**
```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/                     # shadcn/ui base components
│   │   ├── layout/                 # Layout components
│   │   ├── processing/             # Agentic workflow components
│   │   ├── business/               # Business data components
│   │   ├── outreach/               # Outreach management
│   │   ├── results/                # Results and export
│   │   └── shared/                 # Reusable components
│   ├── pages/
│   ├── hooks/
│   ├── services/
│   ├── stores/
│   ├── styles/
│   └── utils/
```

## State Management Architecture

**State Structure:**
```typescript
// Zustand store for UI state
interface UIStore {
  activeRunId: string | null;
  isProcessing: boolean;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  sidebarOpen: boolean;
  currentView: 'form' | 'processing' | 'results';
  selectedBusiness: string | null;
}

// React Query for server state with real-time subscriptions
const useProgressSubscription = (runId: string) => {
  const queryClient = useQueryClient();
  
  React.useEffect(() => {
    if (!runId) return;
    
    const ws = new WebSocket(`${WS_BASE_URL}/processing-runs/${runId}/progress`);
    
    ws.onmessage = (event) => {
      const progressData = JSON.parse(event.data);
      queryClient.setQueryData(['processing-run', runId], (oldData: any) => ({
        ...oldData,
        ...progressData
      }));
    };
    
    return () => ws.close();
  }, [runId, queryClient]);
};
```

## Routing Architecture

**Route Organization:**
```
pages/
├── index.tsx                       # Landing page with processing form
├── processing/
│   └── [runId]/
│       ├── index.tsx              # Real-time progress dashboard
│       ├── businesses.tsx         # Business listing and details
│       ├── outreach.tsx           # Campaign management
│       └── results.tsx            # Final results and export
├── api/                           # API routes (proxy to FastAPI)
└── _app.tsx                       # App wrapper with providers
```

---
