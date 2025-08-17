import React, { useState } from 'react';
import { 
  MapPin, 
  Building2, 
  Globe, 
  Phone, 
  Mail, 
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Search,
  Star,
  RefreshCw,
  AlertCircle
} from 'lucide-react';
import { useBusinessData, Business } from '../hooks/useBusinessData';

interface DiscoveredBusinessesTableProps {
  sessionId: string | null;
  onBusinessSelect?: (business: Business) => void;
}

export default function DiscoveredBusinessesTable({ 
  sessionId, 
  onBusinessSelect 
}: DiscoveredBusinessesTableProps) {
  const [expandedBusiness, setExpandedBusiness] = useState<number | null>(null);
  const [sortField, setSortField] = useState<keyof Business>('business_name');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  // Use the new business data hook
  const {
    businesses,
    isLoading,
    error,
    refresh,
    lastUpdated,
    totalCount,
    location,
    niche,
    workflowProgress
  } = useBusinessData({
    sessionId,
    enabled: !!sessionId,
    pollInterval: 5000,
    autoRefresh: true
  });

  const handleSort = (field: keyof Business) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const sortedBusinesses = [...businesses].sort((a, b) => {
    const aValue = a[sortField as keyof Business];
    const bValue = b[sortField as keyof Business];
    
    if (aValue === undefined && bValue === undefined) return 0;
    if (aValue === undefined) return 1;
    if (bValue === undefined) return -1;
    
    if (typeof aValue === 'string' && typeof bValue === 'string') {
      return sortDirection === 'asc' 
        ? aValue.localeCompare(bValue)
        : bValue.localeCompare(aValue);
    }
    
    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
    }
    
    if (typeof aValue === 'boolean' && typeof bValue === 'boolean') {
      return sortDirection === 'asc' ? (aValue === bValue ? 0 : aValue ? -1 : 1) : (aValue === bValue ? 0 : aValue ? 1 : -1);
    }
    
    return 0;
  });

  const getSortIcon = (field: keyof Business) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? '↑' : '↓';
  };

  const getPriceLevelText = (level?: number) => {
    if (level === undefined) return 'N/A';
    return '$'.repeat(level);
  };

  const getRatingDisplay = (rating?: number, reviewCount?: number) => {
    if (rating === undefined) return 'N/A';
    return (
      <div className="flex items-center space-x-1">
        <div className="flex items-center">
          {[...Array(5)].map((_, i) => (
            <Star 
              key={i} 
              className={`w-3 h-3 ${
                i < Math.floor(rating) 
                  ? 'text-yellow-400 fill-current' 
                  : 'text-gray-300'
              }`} 
            />
          ))}
        </div>
        <span className="text-xs text-gray-600">({reviewCount || 0})</span>
      </div>
    );
  };

  // Show loading state
  if (isLoading && businesses.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Discovering businesses...</p>
      </div>
    );
  }

  // Show error state
  if (error && businesses.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 text-center">
        <div className="text-red-500 mb-4">
          <AlertCircle className="w-12 h-12 mx-auto" />
        </div>
        <p className="text-red-600 mb-4">Failed to load businesses</p>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={refresh}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          <RefreshCw className="w-4 h-4 inline mr-2" />
          Try Again
        </button>
      </div>
    );
  }

  // Show empty state
  if (businesses.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 text-center">
        <Search className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        <p className="text-gray-600">No businesses discovered yet</p>
        <p className="text-sm text-gray-500">Start a conversation to discover businesses</p>
      </div>
    );
  }

  const isDiscoveryComplete = () => {
    return workflowProgress && workflowProgress.businesses_discovered >= 10;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-semibold flex items-center">
              <Search className="w-5 h-5 mr-2" />
              Discovered Businesses
            </h3>
            <p className="text-blue-100 mt-1">
              Found {totalCount} {niche} businesses in {location}
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">{totalCount}</div>
            <div className="text-blue-100 text-sm">Businesses Found</div>
          </div>
        </div>
      </div>

      {/* Refresh and Status Bar */}
      <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={refresh}
              disabled={isLoading}
              className="flex items-center space-x-2 px-3 py-1 text-sm text-gray-600 hover:text-gray-800 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
            {lastUpdated && (
              <span className="text-sm text-gray-500">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </span>
            )}
          </div>
          {isLoading && (
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span>Updating...</span>
            </div>
          )}
        </div>
      </div>

      {/* Discovery Logs Section */}
      {isLoading && (
        <div className="bg-blue-50 px-6 py-4 border-b border-blue-200">
          <div className="flex items-center space-x-2 mb-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            <span className="font-medium text-blue-900">Live Discovery Progress</span>
          </div>
          <div className="space-y-1">
            <div className="text-sm text-blue-800">Scraping Google Places...</div>
            {workflowProgress && workflowProgress.businesses_discovered > 0 && (
              <div className="text-sm text-blue-800">Found {workflowProgress.businesses_discovered}</div>
            )}
            {workflowProgress && workflowProgress.businesses_discovered >= 10 && (
              <div className="text-sm text-green-800 font-medium">Discovery complete</div>
            )}
          </div>
        </div>
      )}

      {/* Discovery Status Indicator */}
      {!isLoading && workflowProgress && workflowProgress.businesses_discovered > 0 && (
        <div className="bg-green-50 px-6 py-3 border-b border-green-200">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm font-medium text-green-800">
              Discovery Complete: {workflowProgress.businesses_discovered} businesses found
            </span>
          </div>
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th 
                className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('business_name')}
              >
                <div className="flex items-center space-x-1">
                  <Building2 className="w-4 h-4" />
                  <span>Business Name</span>
                  {getSortIcon('business_name')}
                </div>
              </th>
              <th 
                className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('rating')}
              >
                <div className="flex items-center space-x-1">
                  <Star className="w-4 h-4" />
                  <span>Rating</span>
                  {getSortIcon('rating')}
                </div>
              </th>
              <th 
                className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('score_overall')}
              >
                <div className="flex items-center space-x-1">
                  <span>Website Score</span>
                  {getSortIcon('score_overall')}
                </div>
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <div className="flex items-center space-x-1">
                  <MapPin className="w-4 h-4" />
                  <span>Location</span>
                </div>
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <div className="flex items-center space-x-1">
                  <Globe className="w-4 h-4" />
                  <span>Website</span>
                </div>
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <div className="flex items-center space-x-1">
                  <Phone className="w-4 h-4" />
                  <span>Contact</span>
                </div>
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <div className="flex items-center space-x-1">
                  <span>Categories</span>
                </div>
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedBusinesses.map((business, index) => (
              <React.Fragment key={index}>
                <tr className="hover:bg-gray-50">
                  <td className="px-4 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => setExpandedBusiness(expandedBusiness === index ? null : index)}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        {expandedBusiness === index ? (
                          <ChevronUp className="w-4 h-4" />
                        ) : (
                          <ChevronDown className="w-4 h-4" />
                        )}
                      </button>
                      <div>
                        <div className="text-sm font-medium text-gray-900">{business.business_name}</div>
                        {business.contact_name && (
                          <div className="text-xs text-gray-500">Contact: {business.contact_name}</div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    {getRatingDisplay(business.rating, business.review_count)}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    {business.score_overall !== undefined ? (
                      <div className="flex items-center space-x-1">
                        <Star 
                          className={`w-3 h-3 ${
                            business.score_overall >= 0.75 
                              ? 'text-yellow-400 fill-current' 
                              : 'text-gray-300'
                          }`} 
                        />
                        <span className="text-xs text-gray-600">
                          {business.score_overall?.toFixed(2) || 'N/A'}
                        </span>
                      </div>
                    ) : 'N/A'}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    <div className="flex items-center justify-between group">
                      <div className="flex items-center text-sm text-gray-900">
                        <MapPin className="w-3 h-3 mr-1" />
                        {business.address}
                      </div>
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(business.address);
                          // You could add a toast notification here
                        }}
                        className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 p-1 text-gray-400 hover:text-gray-600 rounded"
                        title="Copy address"
                      >
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                      </button>
                    </div>
                    {business.postcode && (
                      <div className="text-xs text-gray-500 ml-4">{business.postcode}</div>
                    )}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    {business.website ? (
                      <a
                        href={business.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center px-2 py-1 border border-transparent text-xs font-medium rounded text-blue-700 bg-blue-50 hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
                      >
                        <Globe className="w-3 h-3 mr-1" />
                        Visit Site
                      </a>
                    ) : (
                      <span className="inline-flex items-center px-2 py-1 text-xs font-medium text-gray-500 bg-gray-50 rounded">
                        <Building2 className="w-3 h-3 mr-1" />
                        No website
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    <div className="space-y-1">
                      {business.phone && (
                        <div className="flex items-center justify-between group">
                          <div className="flex items-center text-sm text-gray-600">
                            <Phone className="w-3 h-3 mr-1" />
                            {business.phone}
                          </div>
                          <button
                            onClick={() => {
                              navigator.clipboard.writeText(business.phone!);
                              // You could add a toast notification here
                            }}
                            className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 p-1 text-gray-400 hover:text-gray-600 rounded"
                            title="Copy phone number"
                          >
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                          </button>
                        </div>
                      )}
                      {business.email && (
                        <div className="flex items-center justify-between group">
                          <div className="flex items-center text-sm text-gray-600">
                            <Mail className="w-3 h-3 mr-1" />
                            {business.email}
                          </div>
                          <button
                            onClick={() => {
                              navigator.clipboard.writeText(business.email!);
                              // You could add a toast notification here
                            }}
                            className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 p-1 text-gray-400 hover:text-gray-600 rounded"
                            title="Copy email address"
                          >
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                          </button>
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    <div className="flex flex-wrap gap-1">
                      {business.categories?.slice(0, 3).map((category, catIndex) => (
                        <span
                          key={catIndex}
                          className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                        >
                          {category}
                        </span>
                      ))}
                      {business.categories && business.categories.length > 3 && (
                        <span className="text-xs text-gray-500">
                          +{business.categories.length - 3} more
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-center">
                    {business.demo_status === 'generated' ? (
                      <div className="space-y-2">
                        <div className="text-xs text-green-600 font-medium">✅ Demo Generated</div>
                        {business.generated_site_url && (
                          <a
                            href={business.generated_site_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center px-2 py-1 text-xs font-medium text-blue-700 bg-blue-100 rounded hover:bg-blue-200 transition-colors"
                          >
                            <ExternalLink className="w-3 h-3 mr-1" />
                            View Demo
                          </a>
                        )}
                      </div>
                    ) : business.demo_status === 'skipped' ? (
                      <div className="text-xs text-gray-600">
                        <div className="text-green-600 font-medium">✅ High Score</div>
                        <div className="text-xs">{business.demo_skip_reason}</div>
                      </div>
                    ) : business.demo_status === 'failed' ? (
                      <div className="text-xs text-red-600">
                        <div className="font-medium">❌ Demo Failed</div>
                        <div className="text-xs">{business.demo_error}</div>
                      </div>
                    ) : business.demo_eligible ? (
                      <button
                        onClick={() => onBusinessSelect?.(business)}
                        className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        🚀 Generate Demo
                      </button>
                    ) : (
                      <div className="text-xs text-gray-500">
                        <div className="font-medium">✅ Good Score</div>
                        <div className="text-xs">No demo needed</div>
                      </div>
                    )}
                  </td>
                </tr>
                
                {/* Expanded Details */}
                {expandedBusiness === index && (
                  <tr>
                    <td colSpan={7} className="px-4 py-4 bg-gray-50">
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {/* Business Details */}
                        <div className="space-y-3">
                          <h6 className="font-medium text-gray-900">Business Details</h6>
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-600">Source:</span>
                              <span className="font-medium">{business.source || 'Unknown'}</span>
                            </div>
                            {business.place_id && (
                              <div className="flex justify-between">
                                <span className="text-gray-600">Place ID:</span>
                                <span className="font-medium font-mono text-xs">{business.place_id}</span>
                              </div>
                            )}
                            {business.price_level !== undefined && (
                              <div className="flex justify-between">
                                <span className="text-gray-600">Price Level:</span>
                                <span className="font-medium">{getPriceLevelText(business.price_level)}</span>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Contact Information */}
                        <div className="space-y-3">
                          <h6 className="font-medium text-gray-900">Contact Information</h6>
                          <div className="space-y-2 text-sm">
                            {business.phone && (
                              <div className="flex items-center">
                                <Phone className="w-3 h-3 mr-2 text-gray-400" />
                                <span>{business.phone}</span>
                              </div>
                            )}
                            {business.email && (
                              <div className="flex items-center">
                                <Mail className="w-3 h-3 mr-2 text-gray-400" />
                                <span>{business.email}</span>
                              </div>
                            )}
                            <div className="flex items-center">
                              <MapPin className="w-3 h-3 mr-2 text-gray-400" />
                              <span>{business.address}</span>
                            </div>
                          </div>
                        </div>

                        {/* Categories & Tags */}
                        <div className="space-y-3">
                          <h6 className="font-medium text-gray-900">Categories & Tags</h6>
                          <div className="flex flex-wrap gap-2">
                            {business.categories?.map((category, catIndex) => (
                              <span
                                key={catIndex}
                                className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800"
                              >
                                {category}
                              </span>
                            ))}
                          </div>
                        </div>

                        {/* Quick Actions */}
                        <div className="space-y-3">
                          <h6 className="font-medium text-gray-900">Quick Actions</h6>
                          <div className="flex flex-wrap gap-2">
                            {business.website && (
                              <a
                                href={business.website}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
                              >
                                <ExternalLink className="w-4 h-4 mr-2" />
                                Visit Website
                              </a>
                            )}
                            {business.phone && (
                              <a
                                href={`tel:${business.phone}`}
                                className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
                              >
                                <Phone className="w-4 h-4 mr-2" />
                                Call Business
                              </a>
                            )}
                            {business.email && (
                              <a
                                href={`mailto:${business.email}`}
                                className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
                              >
                                <Mail className="w-4 h-4 mr-2" />
                                Send Email
                              </a>
                            )}
                            <button
                              onClick={() => onBusinessSelect?.(business)}
                              className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
                            >
                              <Building2 className="w-4 h-4 mr-2" />
                              Select for Analysis
                            </button>
                            {/* View on Map - if we have coordinates */}
                            {business.place_id && (
                              <a
                                href={`https://www.google.com/maps/place/?q=place_id:${business.place_id}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
                              >
                                <MapPin className="w-4 h-4 mr-2" />
                                View on Map
                              </a>
                            )}
                          </div>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary Footer */}
      <div className="bg-gray-50 px-6 py-4 border-t">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center space-x-4">
            <span>Total: {totalCount} businesses</span>
            <span>•</span>
            <span>Location: {location}</span>
            <span>•</span>
            <span>Niche: {niche}</span>
          </div>
          <div className="text-right">
            {isDiscoveryComplete() ? (
              <div className="space-y-2">
                <div className="text-xs text-green-600 font-medium">
                  ✅ Discovery complete - Ready for scoring
                </div>
                <button
                  onClick={() => {
                    // This would trigger the scoring workflow
                    console.log('Starting website scoring...');
                    // In a real implementation, this would call the scoring API
                  }}
                  className="inline-flex items-center px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors"
                >
                  🚀 Start Scoring
                </button>
              </div>
            ) : (
              <div className="text-xs text-gray-500">
                Discovery in progress...
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
