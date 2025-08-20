"""
Test endpoint to verify Supabase database connection.
"""

from fastapi import APIRouter, HTTPException
from src.core.supabase import get_supabase_client, is_supabase_configured
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/test-connection")
async def test_supabase_connection():
    """Test Supabase database connection and basic operations."""
    
    try:
        # Check if Supabase is configured
        if not is_supabase_configured():
            raise HTTPException(status_code=500, detail="Supabase not configured")
        
        # Get Supabase client
        supabase = get_supabase_client()
        logger.info("✅ Supabase client created successfully")
        
        # Test basic database operations
        test_results = {}
        
        # 1. Test table existence
        try:
            response = supabase.table('processing_runs').select('count', count='exact').execute()
            test_results['table_exists'] = True
            test_results['processing_runs_count'] = response.count
            logger.info(f"✅ Processing runs table accessible, count: {response.count}")
        except Exception as e:
            test_results['table_exists'] = False
            test_results['table_error'] = str(e)
            logger.error(f"❌ Table access failed: {e}")
        
        # 2. Test insert operation (with rollback)
        try:
            test_data = {
                'location': 'Test Location',
                'niche': 'Test Niche',
                'status': 'initializing',
                'current_step': 'test'
            }
            
            # Insert test record
            insert_response = supabase.table('processing_runs').insert(test_data).execute()
            test_results['insert_success'] = True
            test_results['inserted_id'] = insert_response.data[0]['id'] if insert_response.data else None
            
            # Delete test record (cleanup)
            if insert_response.data:
                supabase.table('processing_runs').delete().eq('id', insert_response.data[0]['id']).execute()
                test_results['cleanup_success'] = True
            
            logger.info("✅ Insert and cleanup test successful")
            
        except Exception as e:
            test_results['insert_success'] = False
            test_results['insert_error'] = str(e)
            logger.error(f"❌ Insert test failed: {e}")
        
        # 3. Test realtime subscription capability
        try:
            channel = supabase.channel('test-connection')
            subscription = channel.on('postgres_changes', 
                event='*', 
                schema='public', 
                table='processing_runs'
            ).subscribe()
            
            # Unsubscribe immediately
            supabase.removeChannel(channel)
            test_results['realtime_success'] = True
            logger.info("✅ Realtime subscription test successful")
            
        except Exception as e:
            test_results['realtime_success'] = False
            test_results['realtime_error'] = str(e)
            logger.error(f"❌ Realtime test failed: {e}")
        
        return {
            "status": "success",
            "message": "Supabase connection test completed",
            "supabase_configured": True,
            "test_results": test_results,
            "timestamp": "2024-01-16T12:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"❌ Supabase connection test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")

@router.get("/test-schema")
async def test_database_schema():
    """Test if all required tables exist and have correct structure."""
    
    try:
        supabase = get_supabase_client()
        
        # List of required tables
        required_tables = [
            'processing_runs',
            'businesses', 
            'website_scores',
            'generated_sites',
            'outreach_campaigns'
        ]
        
        schema_test_results = {}
        
        for table_name in required_tables:
            try:
                # Try to select from table
                response = supabase.table(table_name).select('*').limit(1).execute()
                schema_test_results[table_name] = {
                    'exists': True,
                    'accessible': True,
                    'columns': list(response.data[0].keys()) if response.data else []
                }
                logger.info(f"✅ Table {table_name} exists and accessible")
                
            except Exception as e:
                schema_test_results[table_name] = {
                    'exists': False,
                    'accessible': False,
                    'error': str(e)
                }
                logger.error(f"❌ Table {table_name} test failed: {e}")
        
        return {
            "status": "success",
            "message": "Database schema test completed",
            "schema_test_results": schema_test_results,
            "total_tables": len(required_tables),
            "existing_tables": len([t for t in schema_test_results.values() if t['exists']])
        }
        
    except Exception as e:
        logger.error(f"❌ Schema test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Schema test failed: {str(e)}")
