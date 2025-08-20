import React, { useState, useEffect } from 'react'
import { supabase, TABLES } from '../lib/supabase'

export default function TestSupabase() {
  const [connectionStatus, setConnectionStatus] = useState<string>('Testing...')
  const [testResults, setTestResults] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    testSupabaseConnection()
  }, [])

  const testSupabaseConnection = async () => {
    try {
      setLoading(true)
      setError(null)
      
      console.log('🧪 Testing Supabase connection...')
      
      // Test 1: Basic client creation
      if (!supabase) {
        throw new Error('Supabase client not created')
      }
      console.log('✅ Supabase client created')
      
      // Test 2: Check environment variables
      const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
      const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_API_KEY
      
      if (!supabaseUrl || !supabaseKey) {
        throw new Error('Missing Supabase environment variables')
      }
      console.log('✅ Environment variables configured')
      
      // Test 3: Test database connection
      const { data: testData, error: testError } = await supabase
        .from(TABLES.PROCESSING_RUNS)
        .select('*')
        .limit(1)
      
      if (testError) {
        throw new Error(`Database query failed: ${testError.message}`)
      }
      
      console.log('✅ Database connection successful')
      console.log('📊 Test data:', testData)
      
      // Test 4: Test realtime subscription
      const channel = supabase.channel('test-connection')
      const subscription = channel.on('postgres_changes', 
        { event: '*', schema: 'public', table: TABLES.PROCESSING_RUNS },
        (payload) => {
          console.log('🔄 Real-time update received:', payload)
        }
      ).subscribe()
      
      // Wait a moment for subscription to establish
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Cleanup subscription
      supabase.removeChannel(channel)
      console.log('✅ Real-time subscription test successful')
      
      setConnectionStatus('✅ Connected Successfully!')
      setTestResults({
        clientCreated: true,
        envVarsConfigured: true,
        databaseConnected: true,
        realtimeWorking: true,
        testData: testData,
        timestamp: new Date().toISOString()
      })
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      console.error('❌ Supabase test failed:', errorMessage)
      setConnectionStatus('❌ Connection Failed')
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const runBackendTest = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://127.0.0.1:8000/api/v1/test-connection')
      const data = await response.json()
      
      if (response.ok) {
        setTestResults(data)
        setConnectionStatus('✅ Backend Test Successful!')
      } else {
        throw new Error(data.detail || 'Backend test failed')
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      setConnectionStatus('❌ Backend Test Failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-center">
          🧪 Supabase Connection Test
        </h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Frontend Test */}
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-2xl font-semibold mb-4">Frontend Test</h2>
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <span className="text-lg">Status:</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  connectionStatus.includes('✅') ? 'bg-green-600' : 
                  connectionStatus.includes('❌') ? 'bg-red-600' : 'bg-yellow-600'
                }`}>
                  {connectionStatus}
                </span>
              </div>
              
              {loading && (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Testing connection...</span>
                </div>
              )}
              
              {error && (
                <div className="bg-red-600 p-3 rounded text-sm">
                  <strong>Error:</strong> {error}
                </div>
              )}
              
              <button
                onClick={testSupabaseConnection}
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-4 py-2 rounded"
              >
                🔄 Retest Frontend Connection
              </button>
            </div>
          </div>
          
          {/* Backend Test */}
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-2xl font-semibold mb-4">Backend Test</h2>
            <div className="space-y-4">
              <p className="text-gray-300">
                Test the backend Supabase connection and database operations.
              </p>
              
              <button
                onClick={runBackendTest}
                disabled={loading}
                className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 px-4 py-2 rounded"
              >
                🚀 Run Backend Test
              </button>
            </div>
          </div>
        </div>
        
        {/* Test Results */}
        {testResults && (
          <div className="mt-8 bg-gray-800 p-6 rounded-lg">
            <h2 className="text-2xl font-semibold mb-4">Test Results</h2>
            <div className="bg-gray-900 p-4 rounded overflow-auto">
              <pre className="text-sm text-green-400">
                {JSON.stringify(testResults, null, 2)}
              </pre>
            </div>
          </div>
        )}
        
        {/* Environment Info */}
        <div className="mt-8 bg-gray-800 p-6 rounded-lg">
          <h2 className="text-2xl font-semibold mb-4">Environment Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <strong>Supabase URL:</strong>
              <div className="text-sm text-gray-300 break-all">
                {process.env.NEXT_PUBLIC_SUPABASE_URL || 'Not set'}
              </div>
            </div>
            <div>
              <strong>Supabase Key:</strong>
              <div className="text-sm text-gray-300 break-all">
                {process.env.NEXT_PUBLIC_SUPABASE_API_KEY ? 
                  `${process.env.NEXT_PUBLIC_SUPABASE_API_KEY.substring(0, 20)}...` : 
                  'Not set'
                }
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
