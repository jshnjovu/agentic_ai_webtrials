import React, { useState, useMemo, useCallback } from 'react';
import { Search, Eye, Check } from 'lucide-react';
import { cn } from '@/utils/cn';

export interface Template {
  id: string;
  name: string;
  category: 'restaurant' | 'retail' | 'service' | 'professional';
  description: string;
  preview: string;
  features: string[];
  rating: number;
  usageCount: number;
}

interface TemplateGalleryProps {
  templates: Template[];
  onTemplateSelect: (template: Template) => void;
  selectedTemplate?: Template;
}

export const TemplateGallery: React.FC<TemplateGalleryProps> = ({
  templates,
  onTemplateSelect,
  selectedTemplate
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'name' | 'rating' | 'usage'>('name');

  // Memoized categories for better performance
  const categories = useMemo(() => [
    { id: 'all', name: 'All Templates', count: templates.length },
    { id: 'restaurant', name: 'Restaurant', count: templates.filter(t => t.category === 'restaurant').length },
    { id: 'retail', name: 'Retail', count: templates.filter(t => t.category === 'retail').length },
    { id: 'service', name: 'Service', count: templates.filter(t => t.category === 'service').length },
    { id: 'professional', name: 'Professional', count: templates.filter(t => t.category === 'professional').length },
  ], [templates]);

  // Memoized filtered and sorted templates
  const filteredTemplates = useMemo(() => {
    return templates
      .filter(template => 
        (selectedCategory === 'all' || template.category === selectedCategory) &&
        (searchTerm === '' || 
          template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          template.description.toLowerCase().includes(searchTerm.toLowerCase()))
      )
      .sort((a, b) => {
        switch (sortBy) {
          case 'rating':
            return b.rating - a.rating;
          case 'usage':
            return b.usageCount - a.usageCount;
          default:
            return a.name.localeCompare(b.name);
        }
      });
  }, [templates, selectedCategory, searchTerm, sortBy]);

  // Memoized handlers for better performance
  const handleCategorySelect = useCallback((categoryId: string) => {
    setSelectedCategory(categoryId);
  }, []);

  const handleSortChange = useCallback((sort: 'name' | 'rating' | 'usage') => {
    setSortBy(sort);
  }, []);

  const handleTemplateSelect = useCallback((template: Template) => {
    onTemplateSelect(template);
  }, [onTemplateSelect]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4 font-heading">
          Choose Your Template
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Select from our professionally designed templates to create your perfect website in minutes
        </p>
      </div>

      {/* Search and Filters */}
      <div className="mb-8 space-y-4">
        {/* Search Bar */}
        <div className="relative max-w-md mx-auto">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" aria-hidden="true" />
          <input
            type="text"
            placeholder="Search templates..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            aria-label="Search templates"
          />
        </div>

        {/* Category Filters */}
        <div className="flex flex-wrap justify-center gap-2" role="tablist" aria-label="Template categories">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => handleCategorySelect(category.id)}
              className={cn(
                "px-4 py-2 rounded-full text-sm font-medium transition-colors",
                selectedCategory === category.id
                  ? "bg-primary-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              )}
              role="tab"
              aria-selected={selectedCategory === category.id}
              aria-label={`${category.name} templates (${category.count})`}
            >
              {category.name} ({category.count})
            </button>
          ))}
        </div>

        {/* Sort Options */}
        <div className="flex justify-center items-center gap-4">
          <span className="text-sm text-gray-600">Sort by:</span>
          <div className="flex gap-2">
            {[
              { key: 'name' as const, label: 'Name' },
              { key: 'rating' as const, label: 'Rating' },
              { key: 'usage' as const, label: 'Popularity' }
            ].map((option) => (
              <button
                key={option.key}
                onClick={() => handleSortChange(option.key)}
                className={cn(
                  "px-3 py-1 text-sm rounded-md transition-colors",
                  sortBy === option.key
                    ? "bg-primary-100 text-primary-700"
                    : "text-gray-600 hover:bg-gray-100"
                )}
                aria-label={`Sort by ${option.label}`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Template Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {filteredTemplates.map((template) => (
          <div
            key={template.id}
            className={cn(
              "bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden border-2",
              selectedTemplate?.id === template.id
                ? "border-primary-500 ring-2 ring-primary-200"
                : "border-gray-200 hover:border-primary-300"
            )}
          >
            {/* Template Preview */}
            <div className="relative h-48 bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
              <div className="text-center">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Eye className="w-8 h-8 text-primary-600" />
                </div>
                <p className="text-sm text-gray-600 font-medium">{template.preview}</p>
              </div>
              {selectedTemplate?.id === template.id && (
                <div className="absolute top-3 right-3 bg-primary-500 text-white rounded-full p-1">
                  <Check className="w-4 h-4" />
                </div>
              )}
            </div>

            {/* Template Info */}
            <div className="p-6">
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-xl font-semibold text-gray-900 line-clamp-2">
                  {template.name}
                </h3>
                <div className="flex items-center gap-1 text-sm text-gray-600">
                  <span className="text-accent-500">★</span>
                  <span>{template.rating}</span>
                </div>
              </div>
              
              <p className="text-gray-600 mb-4 line-clamp-3">
                {template.description}
              </p>

              {/* Features */}
              <div className="mb-4">
                <div className="flex flex-wrap gap-2">
                  {template.features.slice(0, 3).map((feature, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                    >
                      {feature}
                    </span>
                  ))}
                  {template.features.length > 3 && (
                    <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                      +{template.features.length - 3} more
                    </span>
                  )}
                </div>
              </div>

              {/* Usage Count */}
              <div className="text-sm text-gray-500 mb-4">
                Used by {template.usageCount.toLocaleString()} businesses
              </div>

              {/* Select Button */}
              <button
                onClick={() => handleTemplateSelect(template)}
                className={cn(
                  "w-full py-3 px-4 rounded-lg font-medium transition-colors",
                  selectedTemplate?.id === template.id
                    ? "bg-primary-600 text-white cursor-default"
                    : "bg-primary-500 hover:bg-primary-600 text-white"
                )}
                disabled={selectedTemplate?.id === template.id}
                aria-label={`Select ${template.name} template`}
              >
                {selectedTemplate?.id === template.id ? 'Selected' : 'Select Template'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* No Results */}
      {filteredTemplates.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No templates found</h3>
          <p className="text-gray-600">
            Try adjusting your search terms or category filters
          </p>
        </div>
      )}
    </div>
  );
};
