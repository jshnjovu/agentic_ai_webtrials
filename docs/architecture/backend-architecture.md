# Backend Architecture

## Service Architecture

**FastAPI Service Organization:**
```
backend/
├── src/
│   ├── main.py                     # FastAPI app initialization
│   ├── core/                       # Core application logic
│   ├── api/                        # API route definitions
│   ├── agents/                     # AI Agent implementations
│   ├── services/                   # Business logic services
│   ├── models/                     # Database models
│   ├── schemas/                    # Pydantic request/response models
│   └── utils/                      # Utility functions
├── tests/
├── requirements.txt
└── Dockerfile
```

## Agentic Orchestrator Pattern

```python
class AgentOrchestrator:
    async def orchestrate_processing(self, run_config: ProcessingRunConfig) -> ProcessingRunResult:
        """
        Orchestrate the complete agentic processing pipeline with parallel execution
        """
        run_id = run_config.run_id
        
        try:
            # Phase 1: Business Discovery
            await self.progress_tracker.update_status(run_id, "discovering")
            businesses = await self._execute_discovery_phase(run_config)
            
            # Phase 2: Parallel Processing (Scoring, Generation, Outreach)
            await self.progress_tracker.update_status(run_id, "processing")
            results = await self._execute_parallel_processing(businesses, run_config)
            
            # Phase 3: Export and Completion
            await self.progress_tracker.update_status(run_id, "exporting")
            export_result = await self._execute_export_phase(results, run_config)
            
            await self.progress_tracker.update_status(run_id, "completed")
            return ProcessingRunResult(
                run_id=run_id,
                businesses=businesses,
                results=results,
                export_paths=export_result,
                status="completed"
            )
            
        except Exception as e:
            await self.progress_tracker.update_status(run_id, "failed", str(e))
            raise ProcessingError(f"Orchestration failed: {str(e)}")
```

## Database Architecture

**Repository Pattern Implementation:**
```python
class BaseRepository:
    def __init__(self, session: AsyncSession, model_class):
        self.session = session
        self.model_class = model_class
    
    async def create(self, **kwargs):
        instance = self.model_class(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance
    
    async def get_by_id(self, id: str):
        result = await self.session.get(self.model_class, id)
        return result

class ProcessingRunRepository(BaseRepository):
    async def get_with_businesses(self, run_id: str) -> Optional[ProcessingRunModel]:
        """Get processing run with all related businesses"""
        stmt = (
            select(ProcessingRunModel)
            .options(
                selectinload(ProcessingRunModel.businesses)
                .selectinload(BusinessModel.website_scores),
                selectinload(ProcessingRunModel.businesses)
                .selectinload(BusinessModel.generated_sites),
                selectinload(ProcessingRunModel.businesses)
                .selectinload(BusinessModel.outreach_campaigns)
            )
            .where(ProcessingRunModel.id == run_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
```

---
