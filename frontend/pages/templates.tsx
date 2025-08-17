import React, { useState } from 'react';
import { TemplateGallery, Template } from '@/components/TemplateGallery';
import { BusinessDataForm, BusinessData } from '@/components/BusinessDataForm';
import { RestaurantTemplate } from '@/templates/themes/restaurant';
import { RetailTemplate } from '@/templates/themes/retail';
import { BaseTemplate } from '@/templates/base';
import { Download, Eye, ArrowLeft, CheckCircle } from 'lucide-react';
import { cn } from '@/utils/cn';

// Sample template data
const sampleTemplates: Template[] = [
  {
    id: 'restaurant-modern',
    name: 'Modern Restaurant',
    category: 'restaurant',
    description: 'Elegant restaurant template with reservation system and menu showcase',
    preview: 'restaurant-modern',
    features: ['Reservation System', 'Menu Gallery', 'Customer Reviews', 'Mobile Responsive'],
    rating: 4.8,
    usageCount: 1247
  },
  {
    id: 'restaurant-casual',
    name: 'Casual Dining',
    category: 'restaurant',
    description: 'Friendly casual dining template perfect for family restaurants',
    preview: 'restaurant-casual',
    features: ['Family Friendly', 'Online Ordering', 'Special Events', 'Photo Gallery'],
    rating: 4.6,
    usageCount: 892
  },
  {
    id: 'retail-fashion',
    name: 'Fashion Retail',
    category: 'retail',
    description: 'Stylish retail template for clothing and fashion businesses',
    preview: 'retail-fashion',
    features: ['Product Catalog', 'Shopping Cart', 'Size Guide', 'Lookbook'],
    rating: 4.7,
    usageCount: 1563
  },
  {
    id: 'retail-electronics',
    name: 'Electronics Store',
    category: 'retail',
    description: 'Modern electronics store template with product comparisons',
    preview: 'retail-electronics',
    features: ['Product Reviews', 'Tech Specs', 'Warranty Info', 'Support Chat'],
    rating: 4.5,
    usageCount: 734
  },
  {
    id: 'service-consulting',
    name: 'Professional Consulting',
    category: 'service',
    description: 'Professional service template for consultants and agencies',
    preview: 'service-consulting',
    features: ['Service Portfolio', 'Client Testimonials', 'Case Studies', 'Contact Forms'],
    rating: 4.9,
    usageCount: 445
  },
  {
    id: 'service-home',
    name: 'Home Services',
    category: 'service',
    description: 'Home improvement and maintenance services template',
    preview: 'service-home',
    features: ['Service Areas', 'Before/After Gallery', 'Free Quotes', 'Emergency Contact'],
    rating: 4.4,
    usageCount: 678
  }
];

export default function TemplatesPage() {
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [businessData, setBusinessData] = useState<BusinessData | null>(null);
  const [currentStep, setCurrentStep] = useState<'gallery' | 'data-input' | 'preview' | 'generated'>('gallery');
  const [generatedSite, setGeneratedSite] = useState<string>('');

  const handleTemplateSelect = (template: Template) => {
    setSelectedTemplate(template);
    setCurrentStep('data-input');
  };

  const handleBusinessDataChange = (data: BusinessData) => {
    setBusinessData(data);
  };

  const handleGenerateWebsite = () => {
    if (businessData && selectedTemplate) {
      // In a real implementation, this would generate the actual HTML/CSS
      setGeneratedSite('https://generated-site.example.com');
      setCurrentStep('generated');
    }
  };

  const handleBackToGallery = () => {
    setSelectedTemplate(null);
    setBusinessData(null);
    setCurrentStep('gallery');
  };

  const handlePreview = () => {
    setCurrentStep('preview');
  };

  const renderGeneratedSite = () => {
    if (!businessData || !selectedTemplate) return null;

    switch (selectedTemplate.category) {
      case 'restaurant':
        return (
          <RestaurantTemplate
            {...businessData}
            cuisine={businessData.cuisine}
            hours={businessData.hours}
            rating={businessData.rating}
            specialties={businessData.specialties}
            menuHighlights={businessData.services}
          />
        );
      case 'retail':
        return (
          <RetailTemplate
            {...businessData}
            storeType={businessData.storeType}
            hours={businessData.hours}
            rating={businessData.rating}
            featuredProducts={businessData.featuredProducts}
            services={businessData.services}
            paymentMethods={businessData.paymentMethods}
          />
        );
      default:
        return (
          <BaseTemplate {...businessData}>
            <div className="py-20 text-center">
              <h1 className="text-4xl font-bold text-gray-900 mb-6">
                {businessData.businessName}
              </h1>
              {businessData.description && (
                <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
                  {businessData.description}
                </p>
              )}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
                {businessData.services.map((service, index) => (
                  <div key={index} className="bg-gray-50 p-6 rounded-lg">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">{service}</h3>
                  </div>
                ))}
              </div>
            </div>
          </BaseTemplate>
        );
    }
  };

  const renderContent = () => {
    switch (currentStep) {
      case 'gallery':
        return (
          <TemplateGallery
            templates={sampleTemplates}
            onTemplateSelect={handleTemplateSelect}
            selectedTemplate={selectedTemplate || undefined}
          />
        );

      case 'data-input':
        return (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="mb-8">
              <button
                onClick={handleBackToGallery}
                className="flex items-center text-primary-600 hover:text-primary-700 font-medium mb-4"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Templates
              </button>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Customize Your {selectedTemplate?.name} Template
              </h1>
              <p className="text-gray-600">
                Fill in your business information to generate your personalized website
              </p>
            </div>
            
            <BusinessDataForm
              onDataChange={handleBusinessDataChange}
              templateCategory={selectedTemplate?.category}
            />
            
            {businessData && (
              <div className="mt-8 text-center">
                <button
                  onClick={handlePreview}
                  className="bg-accent-500 hover:bg-accent-600 text-white px-8 py-3 rounded-lg font-semibold text-lg transition-colors shadow-lg hover:shadow-xl"
                >
                  <Eye className="w-5 h-5 inline mr-2" />
                  Preview Website
                </button>
              </div>
            )}
          </div>
        );

      case 'preview':
        return (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="mb-8">
              <button
                onClick={() => setCurrentStep('data-input')}
                className="flex items-center text-primary-600 hover:text-primary-700 font-medium mb-4"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Customization
              </button>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Preview Your Website
              </h1>
              <p className="text-gray-600">
                Review your website before generating the final version
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow-lg overflow-hidden">
              <div className="bg-gray-100 px-4 py-2 border-b flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                </div>
                <span className="text-sm text-gray-600">Preview Mode</span>
              </div>
              <div className="max-h-96 overflow-y-auto">
                {renderGeneratedSite()}
              </div>
            </div>
            
            <div className="mt-8 text-center space-x-4">
              <button
                onClick={() => setCurrentStep('data-input')}
                className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-6 py-2 rounded-lg font-medium transition-colors"
              >
                Make Changes
              </button>
              <button
                onClick={handleGenerateWebsite}
                className="bg-success-500 hover:bg-success-600 text-white px-8 py-3 rounded-lg font-semibold text-lg transition-colors shadow-lg hover:shadow-xl"
              >
                Generate Website
              </button>
            </div>
          </div>
        );

      case 'generated':
        return (
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
            <div className="bg-white rounded-lg shadow-lg p-12">
              <div className="w-20 h-20 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="w-10 h-10 text-success-600" />
              </div>
              
              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                Website Generated Successfully!
              </h1>
              
              <p className="text-gray-600 mb-8 text-lg">
                Your professional website has been created and is ready to use.
              </p>
              
              <div className="bg-gray-50 rounded-lg p-6 mb-8">
                <h3 className="font-semibold text-gray-900 mb-2">Your Website URL:</h3>
                <p className="text-primary-600 font-mono text-lg break-all">
                  {generatedSite}
                </p>
              </div>
              
              <div className="space-y-4">
                <button className="w-full bg-primary-600 hover:bg-primary-700 text-white px-8 py-3 rounded-lg font-semibold text-lg transition-colors">
                  <Download className="w-5 h-5 inline mr-2" />
                  Download Website Files
                </button>
                
                <button className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 px-8 py-3 rounded-lg font-medium transition-colors">
                  View Live Website
                </button>
                
                <button
                  onClick={handleBackToGallery}
                  className="w-full bg-transparent hover:bg-gray-50 text-gray-600 px-8 py-3 rounded-lg font-medium transition-colors border border-gray-300"
                >
                  Create Another Website
                </button>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900 font-heading">
                Website Template Generator
              </h1>
            </div>
            <nav className="flex space-x-8">
              <a href="#" className="text-gray-700 hover:text-primary-600 transition-colors">
                Templates
              </a>
              <a href="#" className="text-gray-700 hover:text-primary-600 transition-colors">
                My Projects
              </a>
              <a href="#" className="text-gray-700 hover:text-primary-600 transition-colors">
                Help
              </a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {renderContent()}
      </main>
    </div>
  );
}
