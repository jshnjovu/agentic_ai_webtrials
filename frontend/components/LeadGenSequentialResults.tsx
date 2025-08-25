import React, { useState } from 'react';
import {
  MapPin,
  Building2,
  Globe,
  Target,
  CheckCircle,
  AlertCircle,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Star,
  Phone,
  Mail
} from 'lucide-react';
import { Business } from '../hooks/useBusinessData';

interface LeadGenSequentialResultsProps {
  businesses: Business[];
  location: string;
  niche: string;
}

export default function LeadGenSequentialResults({
  businesses,
  location,
  niche
}: LeadGenSequentialResultsProps) {
  const [expandedPhase, setExpandedPhase] = useState<number | null>(null);
  const [expandedBusiness, setExpandedBusiness] = useState<number | null>(null);

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 70) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 70) return 'Good';
    if (score >= 60) return 'Fair';
    return 'Poor';
  };

  const lowScorers = businesses.filter(b => (b.score_overall || 0) < 70);
  const highScorers = businesses.filter(b => (b.score_overall || 0) >= 70);

  const phases = [
    {
      id: 1,
      title: '🏢 Phase 1: Business Discovery Results',
      description: `Found ${businesses.length} businesses in ${niche} within ${location}`,
      icon: Building2,
      color: 'blue'
    },
    {
      id: 2,
      title: '📊 Phase 2: Website Scoring Results',
      description: `Scored ${businesses.length} websites with performance analysis`,
      icon: Target,
      color: 'green'
    },
    {
      id: 3,
      title: '🎯 Phase 3: Improvement Opportunities',
      description: `${lowScorers.length} businesses qualify for demo site generation (score &lt; 70)`,
      icon: AlertCircle,
      color: 'orange'
    }
  ];

  return (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          📊 LeadGen Results Summary
        </h2>
        <p className="text-lg text-gray-600">
          Complete workflow results for {niche} businesses in {location}
        </p>
      </div>

      {/* Phase 1: Business Discovery Results */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div
          className="p-6 cursor-pointer hover:bg-gray-50 border-b"
          onClick={() => setExpandedPhase(expandedPhase === 1 ? null : 1)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                <Building2 className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900">Phase 1: Business Discovery Results</h3>
                <p className="text-gray-600">Found {businesses.length} businesses in {niche} within {location}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-2xl font-bold text-blue-600">{businesses.length}</div>
                <div className="text-sm text-gray-500">Businesses Found</div>
              </div>
              {expandedPhase === 1 ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
            </div>
          </div>
        </div>

        {expandedPhase === 1 && (
          <div className="p-6 bg-gray-50">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Business</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contact</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {businesses.map((business, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div>
                          {business.website ? (
                            <a
                              href={business.website}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-800 text-sm font-medium hover:underline"
                            >
                              {business.business_name}
                            </a>
                          ) : (
                            <div className="text-sm font-medium text-gray-900">{business.business_name}</div>
                          )}
                          {business.contact_name && (
                            <div className="text-sm text-gray-500">Contact: {business.contact_name}</div>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="space-y-1">
                          {business.email && (
                            <div className="flex items-center text-sm text-gray-600">
                              <Mail className="w-3 h-3 mr-1" />
                              {business.email}
                            </div>
                          )}
                          {business.phone && (
                            <div className="flex items-center text-sm text-gray-600">
                              <Phone className="w-3 h-3 mr-1" />
                              {business.phone}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="flex items-center text-sm text-gray-600">
                          <MapPin className="w-3 h-3 mr-1" />
                          {business.address}
                        </div>
                      </td>

                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Phase 2: Website Scoring Results */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div
          className="p-6 cursor-pointer hover:bg-gray-50 border-b"
          onClick={() => setExpandedPhase(expandedPhase === 2 ? null : 2)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                <Target className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900">Phase 2: Website Scoring Results</h3>
                <p className="text-gray-600">Performance analysis using Google PageSpeed API and heuristic evaluation</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-2xl font-bold text-green-600">{businesses.length}</div>
                <div className="text-sm text-gray-500">Websites Scored</div>
              </div>
              {expandedPhase === 2 ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
            </div>
          </div>
        </div>

        {expandedPhase === 2 && (
          <div className="p-6 bg-gray-50">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Scoring Summary */}
              <div className="bg-white p-6 rounded-lg border">
                <h4 className="text-lg font-medium mb-4">Scoring Summary</h4>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">High Performers (≥70):</span>
                    <span className="font-semibold text-green-600">{highScorers.length}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Improvement Needed (&lt;70):</span>
                    <span className="font-semibold text-orange-600">{lowScorers.length}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Average Score:</span>
                    <span className="font-semibold">
                      {Math.round(businesses.reduce((sum, b) => sum + (b.score_overall || 0), 0) / businesses.length)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Score Distribution */}
              <div className="bg-white p-6 rounded-lg border">
                <h4 className="text-lg font-medium mb-4">Score Distribution</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Excellent (80-100):</span>
                    <span className="font-semibold text-green-600">
                      {businesses.filter(b => (b.score_overall || 0) >= 80).length}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Good (70-79):</span>
                    <span className="font-semibold text-yellow-600">
                      {businesses.filter(b => (b.score_overall || 0) >= 70 && (b.score_overall || 0) < 80).length}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Fair (60-69):</span>
                    <span className="font-semibold text-orange-600">
                      {businesses.filter(b => (b.score_overall || 0) >= 60 && (b.score_overall || 0) < 70).length}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Poor (&lt;60):</span>
                    <span className="font-semibold text-red-600">
                      {businesses.filter(b => (b.score_overall || 0) < 60).length}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Detailed Scoring Table */}
            <div className="mt-6">
              <h4 className="text-lg font-medium mb-4">Detailed Website Scores</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Business</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Performance</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Accessibility</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">SEO</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Trust</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">CRO</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Overall</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {businesses.map((business, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-4 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{business.business_name}</div>
                            <div className="text-xs text-gray-500">{business.website || 'No website'}</div>
                          </div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-center">
                          <div className={`inline-flex px-2 py-1 rounded text-sm font-medium ${getScoreColor(business.score_perf || 0)}`}>
                            {business.score_perf || 0}
                          </div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-center">
                          <div className={`inline-flex px-2 py-1 rounded text-sm font-medium ${getScoreColor(business.score_access || 0)}`}>
                            {business.score_access || 0}
                          </div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-center">
                          <div className={`inline-flex px-2 py-1 rounded text-sm font-medium ${getScoreColor(business.score_seo || 0)}`}>
                            {business.score_seo || 0}
                          </div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-center">
                          <div className={`inline-flex px-2 py-1 rounded text-sm font-medium ${getScoreColor(business.score_trust || 0)}`}>
                            {business.score_trust || 0}
                          </div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-center">
                          <div className={`inline-flex px-2 py-1 rounded text-sm font-medium ${getScoreColor(business.score_cro || 0)}`}>
                            {business.score_cro || 0}
                          </div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-center">
                          <div className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(business.score_overall || 0)}`}>
                            {business.score_overall || 0}%
                          </div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-center">
                          <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${(business.score_overall || 0) >= 70
                              ? 'bg-green-100 text-green-800'
                              : 'bg-orange-100 text-orange-800'
                            }`}>
                            {(business.score_overall || 0) >= 70 ? (
                              <>
                                <CheckCircle className="w-3 h-3 mr-1" />
                                Good
                              </>
                            ) : (
                              <>
                                <AlertCircle className="w-3 h-3 mr-1" />
                                Needs Demo
                              </>
                            )}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Phase 3: Improvement Opportunities */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div
          className="p-6 cursor-pointer hover:bg-gray-50 border-b"
          onClick={() => setExpandedPhase(expandedPhase === 3 ? null : 3)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mr-4">
                <AlertCircle className="w-6 h-6 text-orange-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900">Phase 3: Improvement Opportunities</h3>
                <p className="text-gray-600">{lowScorers.length} businesses qualify for demo site generation (score &lt; 70)</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-2xl font-bold text-orange-600">{lowScorers.length}</div>
                <div className="text-sm text-gray-500">Demo Candidates</div>
              </div>
              {expandedPhase === 3 ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
            </div>
          </div>
        </div>
        {expandedPhase === 3 && (
          <div className="p-6 bg-gray-50">
            {lowScorers.length > 0 ? (
              <div className="space-y-4">
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <AlertCircle className="w-5 h-5 text-orange-600 mr-2" />
                    <div>
                      <h4 className="font-medium text-orange-800">Demo Site Generation Criteria</h4>
                      <p className="text-sm text-orange-700">
                        Businesses scoring below 70 points automatically qualify for demo site generation.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {lowScorers.map((business, index) => (
                    <div key={index} className="bg-white p-4 rounded-lg border hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-3">
                        <h5 className="font-medium text-gray-900">{business.business_name}</h5>
                        <div
                          className={`inline-flex px-2 py-1 rounded text-xs font-medium ${getScoreColor(
                            business.score_overall || 0
                          )}`}
                        >
                          {business.score_overall || 0}%
                        </div>
                      </div>

                      {/* Keep the list of **unique** top issues only */}
                      {business.top_issues && business.top_issues.length > 0 && (
                        <div className="mt-3 pt-3 border-t">
                          <h6 className="text-xs font-medium text-gray-700 mb-2">Top Issues:</h6>
                          <ul className="space-y-1">
                            {business.top_issues.map((issue, issueIndex) => (
                              <li key={issueIndex} className="text-xs text-red-600 flex items-start">
                                <AlertCircle className="w-3 h-3 mr-1 mt-0.5 flex-shrink-0" />
                                {issue}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      <div className="mt-3 pt-3 border-t">
                        <div className="text-xs text-gray-500">
                          <div className="flex items-center mb-1">
                            <MapPin className="w-3 h-3 mr-1" />
                            {business.address}
                          </div>
                          {business.website && (
                            <div className="flex items-center">
                              <Globe className="w-3 h-3 mr-1" />
                              <a
                                href={business.website}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 hover:underline"
                              >
                                Current Website
                              </a>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                <h4 className="text-lg font-medium text-gray-900 mb-2">All Websites Score Well!</h4>
                <p className="text-gray-600">
                  All discovered businesses have websites scoring 70 or above. No demo sites are needed.
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Next Steps Information */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start">
          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
            <Target className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-medium text-blue-900 mb-2">Next Steps</h3>
            <div className="text-sm text-blue-800 space-y-2">
              <p>
                <strong>Phase 4 (Coming Soon):</strong> Demo Site Generation - AI-powered website creation for qualifying businesses
              </p>
              <p>
                <strong>Phase 5 (Coming Soon):</strong> Site Deployment - Automated hosting and deployment to Vercel
              </p>
              <p>
                <strong>Phase 6 (Coming Soon):</strong> Outreach Campaigns - Personalized email, WhatsApp, and SMS messages
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
