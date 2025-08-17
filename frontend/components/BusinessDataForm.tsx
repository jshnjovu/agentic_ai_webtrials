import React, { useState, useCallback, useMemo } from 'react';
import { User, Building2, MapPin, Phone, Mail, Globe, Star, ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '@/utils/cn';

export interface BusinessData {
  businessName: string;
  tagline?: string;
  description?: string;
  phone?: string;
  email?: string;
  address?: string;
  website?: string;
  hours?: string;
  rating?: number;
  category: string;
  services: string[];
  // Restaurant specific
  cuisine?: string;
  specialties?: string[];
  menuHighlights?: string[];
  // Retail specific
  storeType?: string;
  featuredProducts?: string[];
  paymentMethods?: string[];
}

interface BusinessDataFormProps {
  initialData?: Partial<BusinessData>;
  onDataChange: (data: BusinessData) => void;
  templateCategory?: string;
}

export const BusinessDataForm: React.FC<BusinessDataFormProps> = ({
  initialData = {},
  onDataChange,
  templateCategory
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<BusinessData>({
    businessName: '',
    tagline: '',
    description: '',
    phone: '',
    email: '',
    address: '',
    website: '',
    hours: '',
    rating: 0,
    category: '',
    services: [],
    cuisine: '',
    specialties: [],
    menuHighlights: [],
    storeType: '',
    featuredProducts: [],
    paymentMethods: [],
    ...initialData
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Memoized steps configuration
  const steps = useMemo(() => [
    { id: 1, title: 'Basic Information', icon: Building2, description: 'Business name and basic details' },
    { id: 2, title: 'Contact Details', icon: Phone, description: 'Phone, email, and address' },
    { id: 3, title: 'Business Details', icon: User, description: 'Category and services' },
    { id: 4, title: 'Customization', icon: Star, description: 'Special features and branding' },
  ], []);

  // Memoized validation function
  const validateStep = useCallback((step: number): boolean => {
    const newErrors: Record<string, string> = {};

    switch (step) {
      case 1:
        if (!formData.businessName.trim()) {
          newErrors.businessName = 'Business name is required';
        }
        break;
      case 2:
        if (!formData.phone && !formData.email) {
          newErrors.contact = 'At least one contact method is required';
        }
        break;
      case 3:
        if (!formData.category) {
          newErrors.category = 'Business category is required';
        }
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData]);

  // Memoized handlers
  const handleNext = useCallback(() => {
    if (validateStep(currentStep)) {
      setCurrentStep(Math.min(currentStep + 1, steps.length));
    }
  }, [currentStep, steps.length, validateStep]);

  const handlePrevious = useCallback(() => {
    setCurrentStep(Math.max(currentStep - 1, 1));
  }, [currentStep]);

  const handleInputChange = useCallback((field: keyof BusinessData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
    // Trigger data change callback
    onDataChange({ ...formData, [field]: value });
  }, [errors, formData, onDataChange]);

  const handleServiceToggle = useCallback((service: string) => {
    const newServices = formData.services.includes(service)
      ? formData.services.filter(s => s !== service)
      : [...formData.services, service];
    
    handleInputChange('services', newServices);
  }, [formData.services, handleInputChange]);

  const handleArrayFieldChange = useCallback((field: keyof BusinessData, value: string, action: 'add' | 'remove') => {
    const currentArray = (formData[field] as string[]) || [];
    let newArray: string[];
    
    if (action === 'add') {
      newArray = [...currentArray, value];
    } else {
      newArray = currentArray.filter(item => item !== value);
    }
    
    handleInputChange(field, newArray);
  }, [formData, handleInputChange]);

  // Memoized progress percentage
  const progressPercentage = useMemo(() => (currentStep / steps.length) * 100, [currentStep, steps.length]);

  // Memoized current step data
  const currentStepData = useMemo(() => steps.find(step => step.id === currentStep), [steps, currentStep]);

  return (
    <div className="max-w-4xl mx-auto">
      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900 font-heading">
            {currentStepData?.title}
          </h2>
          <span className="text-sm text-gray-500">
            Step {currentStep} of {steps.length}
          </span>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-primary-600 h-2 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progressPercentage}%` }}
            role="progressbar"
            aria-valuenow={currentStep}
            aria-valuemin={1}
            aria-valuemax={steps.length}
            aria-label={`Step ${currentStep} of ${steps.length}`}
          />
        </div>
        
        <p className="text-gray-600 mt-2 text-center">
          {currentStepData?.description}
        </p>
      </div>

      {/* Step Content */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        {currentStep === 1 && (
          <div className="space-y-6">
            <div>
              <label htmlFor="businessName" className="block text-sm font-medium text-gray-700 mb-2">
                Business Name *
              </label>
              <input
                id="businessName"
                type="text"
                value={formData.businessName}
                onChange={(e) => handleInputChange('businessName', e.target.value)}
                className={cn(
                  "w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors",
                  errors.businessName ? "border-red-500" : "border-gray-300"
                )}
                placeholder="Enter your business name"
                aria-describedby={errors.businessName ? "businessName-error" : undefined}
                aria-required="true"
              />
              {errors.businessName && (
                <p id="businessName-error" className="mt-1 text-sm text-red-600" role="alert">
                  {errors.businessName}
                </p>
              )}
            </div>

            <div>
              <label htmlFor="tagline" className="block text-sm font-medium text-gray-700 mb-2">
                Tagline
              </label>
              <input
                id="tagline"
                type="text"
                value={formData.tagline}
                onChange={(e) => handleInputChange('tagline', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                placeholder="A short description of your business"
              />
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                placeholder="Tell customers about your business..."
              />
            </div>
          </div>
        )}

        {currentStep === 2 && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                  Phone Number
                </label>
                <input
                  id="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                  placeholder="(555) 123-4567"
                />
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                  placeholder="contact@business.com"
                />
              </div>
            </div>

            <div>
              <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-2">
                Address
              </label>
              <input
                id="address"
                type="text"
                value={formData.address}
                onChange={(e) => handleInputChange('address', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                placeholder="123 Business St, City, State 12345"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="website" className="block text-sm font-medium text-gray-700 mb-2">
                  Website
                </label>
                <input
                  id="website"
                  type="url"
                  value={formData.website}
                  onChange={(e) => handleInputChange('website', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                  placeholder="https://www.business.com"
                />
              </div>

              <div>
                <label htmlFor="hours" className="block text-sm font-medium text-gray-700 mb-2">
                  Business Hours
                </label>
                <input
                  id="hours"
                  type="text"
                  value={formData.hours}
                  onChange={(e) => handleInputChange('hours', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                  placeholder="Mon-Fri 9AM-6PM"
                />
              </div>
            </div>

            {errors.contact && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600" role="alert">
                  {errors.contact}
                </p>
              </div>
            )}
          </div>
        )}

        {currentStep === 3 && (
          <div className="space-y-6">
            <div>
              <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
                Business Category *
              </label>
              <select
                id="category"
                value={formData.category}
                onChange={(e) => handleInputChange('category', e.target.value)}
                className={cn(
                  "w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors",
                  errors.category ? "border-red-500" : "border-gray-300"
                )}
                aria-describedby={errors.category ? "category-error" : undefined}
                aria-required="true"
              >
                <option value="">Select a category</option>
                <option value="restaurant">Restaurant & Food</option>
                <option value="retail">Retail & Shopping</option>
                <option value="service">Professional Services</option>
                <option value="healthcare">Healthcare</option>
                <option value="fitness">Fitness & Wellness</option>
                <option value="beauty">Beauty & Salon</option>
                <option value="automotive">Automotive</option>
                <option value="other">Other</option>
              </select>
              {errors.category && (
                <p id="category-error" className="mt-1 text-sm text-red-600" role="alert">
                  {errors.category}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Services Offered
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {[
                  'Consultation', 'Installation', 'Maintenance', 'Repair',
                  'Design', 'Planning', 'Training', 'Support'
                ].map((service) => (
                  <label key={service} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.services.includes(service)}
                      onChange={() => handleServiceToggle(service)}
                      className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">{service}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Template-specific fields */}
            {templateCategory === 'restaurant' && (
              <div className="space-y-4">
                <div>
                  <label htmlFor="cuisine" className="block text-sm font-medium text-gray-700 mb-2">
                    Cuisine Type
                  </label>
                  <input
                    id="cuisine"
                    type="text"
                    value={formData.cuisine}
                    onChange={(e) => handleInputChange('cuisine', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                    placeholder="Italian, Mexican, Asian, etc."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Specialties
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {formData.specialties?.map((specialty, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-primary-100 text-primary-800"
                      >
                        {specialty}
                        <button
                          type="button"
                          onClick={() => handleArrayFieldChange('specialties', specialty, 'remove')}
                          className="ml-2 text-primary-600 hover:text-primary-800"
                          aria-label={`Remove ${specialty}`}
                        >
                          ×
                        </button>
                      </span>
                    ))}
                    <input
                      type="text"
                      placeholder="Add specialty..."
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && e.currentTarget.value.trim()) {
                          handleArrayFieldChange('specialties', e.currentTarget.value.trim(), 'add');
                          e.currentTarget.value = '';
                        }
                      }}
                      className="px-3 py-1 border border-gray-300 rounded-full text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                </div>
              </div>
            )}

            {templateCategory === 'retail' && (
              <div className="space-y-4">
                <div>
                  <label htmlFor="storeType" className="block text-sm font-medium text-gray-700 mb-2">
                    Store Type
                  </label>
                  <input
                    id="storeType"
                    type="text"
                    value={formData.storeType}
                    onChange={(e) => handleInputChange('storeType', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                    placeholder="Clothing, Electronics, Home & Garden, etc."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Featured Products
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {formData.featuredProducts?.map((product, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-accent-100 text-accent-800"
                      >
                        {product}
                        <button
                          type="button"
                          onClick={() => handleArrayFieldChange('featuredProducts', product, 'remove')}
                          className="ml-2 text-accent-600 hover:text-accent-800"
                          aria-label={`Remove ${product}`}
                        >
                          ×
                        </button>
                      </span>
                    ))}
                    <input
                      type="text"
                      placeholder="Add product..."
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && e.currentTarget.value.trim()) {
                          handleArrayFieldChange('featuredProducts', e.currentTarget.value.trim(), 'add');
                          e.currentTarget.value = '';
                        }
                      }}
                      className="px-3 py-1 border border-gray-300 rounded-full text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {currentStep === 4 && (
          <div className="space-y-6">
            <div>
              <label htmlFor="rating" className="block text-sm font-medium text-gray-700 mb-2">
                Current Rating
              </label>
              <div className="flex items-center space-x-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => handleInputChange('rating', star)}
                                         className={cn(
                       "text-2xl transition-colors",
                       star <= (formData.rating || 0) ? "text-accent-500" : "text-gray-300"
                     )}
                    aria-label={`Rate ${star} stars`}
                  >
                    ★
                  </button>
                ))}
                <span className="ml-2 text-sm text-gray-600">
                  {formData.rating}/5 stars
                </span>
              </div>
            </div>

            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Ready to Generate Your Website?
              </h3>
              <p className="text-gray-600">
                Review your information and click generate to create your professional website
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="flex justify-between items-center mt-8">
        <button
          onClick={handlePrevious}
          disabled={currentStep === 1}
          className={cn(
            "flex items-center px-6 py-3 rounded-lg font-medium transition-colors",
            currentStep === 1
              ? "bg-gray-100 text-gray-400 cursor-not-allowed"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          )}
          aria-label="Go to previous step"
        >
          <ChevronLeft className="w-4 h-4 mr-2" />
          Previous
        </button>

        <button
          onClick={handleNext}
          disabled={currentStep === steps.length}
          className={cn(
            "flex items-center px-6 py-3 rounded-lg font-medium transition-colors",
            currentStep === steps.length
              ? "bg-primary-600 text-white cursor-not-allowed"
              : "bg-primary-500 hover:bg-primary-600 text-white"
          )}
          aria-label={currentStep === steps.length ? "Form completed" : "Go to next step"}
        >
          {currentStep === steps.length ? 'Complete' : 'Next'}
          {currentStep < steps.length && <ChevronRight className="w-4 h-4 ml-2" />}
        </button>
      </div>
    </div>
  );
};
