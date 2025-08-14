"""
Base service class for all business logic services.
Provides common functionality and enforces coding standards.
"""

import logging
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod


class BaseService(ABC):
    """Base class for all business logic services."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up structured logging for the service."""
        logger = logging.getLogger(f"{self.__class__.__name__}")
        logger.setLevel(logging.INFO)
        
        # Create formatter for structured logging
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - runId:%(runId)s - businessId:%(businessId)s - agentName:%(agentName)s - %(message)s'
        )
        
        # Add handler if not already present
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def log_operation(self, operation: str, run_id: Optional[str] = None, 
                     business_id: Optional[str] = None, **kwargs):
        """Log an operation with structured data."""
        extra = {
            'runId': run_id or 'unknown',
            'businessId': business_id or 'unknown',
            'agentName': self.service_name
        }
        extra.update(kwargs)
        
        self.logger.info(f"Operation: {operation}", extra=extra)
    
    def log_error(self, error: Exception, operation: str, run_id: Optional[str] = None,
                  business_id: Optional[str] = None, **kwargs):
        """Log an error with structured data."""
        extra = {
            'runId': run_id or 'unknown',
            'businessId': business_id or 'unknown',
            'agentName': self.service_name
        }
        extra.update(kwargs)
        
        self.logger.error(f"Error in {operation}: {str(error)}", extra=extra)
    
    @abstractmethod
    def validate_input(self, data: Any) -> bool:
        """Validate input data for the service."""
        pass
    
    def handle_error(self, error: Exception, context: str, run_id: Optional[str] = None) -> Dict[str, Any]:
        """Handle errors consistently across all services."""
        self.log_error(error, context, run_id)
        
        return {
            "success": False,
            "error": str(error),
            "context": context,
            "service": self.service_name,
            "run_id": run_id
        }
