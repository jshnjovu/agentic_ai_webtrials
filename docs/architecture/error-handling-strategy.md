# Error Handling Strategy

## Error Response Format

```typescript
interface ApiError {
  error: {
    code: string;           // Machine-readable error code
    message: string;        // Human-readable error message
    details?: Record<string, any>; // Additional error context
    timestamp: string;      // ISO timestamp
    requestId: string;      // Unique request identifier
    retryable: boolean;     // Whether the error can be retried
    recoveryActions?: string[]; // Suggested recovery actions
  };
  context?: {
    runId?: string;         // Processing run context
    businessId?: string;    // Business context
    agentName?: string;     // Agent context
    operation?: string;     // Operation being performed
  };
}
```

## Error Flow

```mermaid
sequenceDiagram
    participant UI as Frontend UI
    participant API as FastAPI Backend
    participant ORCH as Agent Orchestrator  
    participant AGENT as AI Agent
    participant EXT as External API
    participant DB as Database
    participant LOG as Error Logger

    AGENT->>EXT: API Request
    EXT-->>AGENT: Error Response (429, 500, timeout)
    
    AGENT->>LOG: Log error with context
    AGENT->>AGENT: Check retry policy
    
    alt Retryable Error
        AGENT->>AGENT: Exponential backoff delay
        AGENT->>EXT: Retry request
        alt Retry Success
            EXT->>AGENT: Successful response
        else Max Retries Exceeded
            AGENT->>ORCH: Report agent failure
            ORCH->>DB: Update error status
            ORCH->>ORCH: Execute compensation logic
        end
    else Non-Retryable Error
        AGENT->>ORCH: Report permanent failure
        ORCH->>DB: Update processing run status
    end
    
    ORCH->>API: Error status update
    API->>DB: Persist error details
    DB->>Supabase Realtime: Error event
    Supabase Realtime->>UI: Real-time error notification
    UI->>UI: Display error with recovery options
```

---
