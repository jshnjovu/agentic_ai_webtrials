import React from 'react';
import { BaseTemplate, BaseTemplateProps } from '../../base';
import { MapPin, Phone, Mail, Clock, ShoppingBag, Truck, CreditCard, Star } from 'lucide-react';

export interface RetailTemplateProps extends BaseTemplateProps {
  storeType?: string;
  hours?: string;
  rating?: number;
  featuredProducts?: string[];
  services?: string[];
  paymentMethods?: string[];
}

export const RetailTemplate: React.FC<RetailTemplateProps> = ({
  storeType,
  hours,
  rating,
  featuredProducts = [],
  services = [],
  paymentMethods = [],
  ...baseProps
}) => {
  return (
    <BaseTemplate {...baseProps}>
      {/* Hero Section */}
      <section className="relative bg-gradient-to-r from-secondary-600 to-secondary-800 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 font-heading">
            {baseProps.businessName}
          </h1>
          {baseProps.tagline && (
            <p className="text-xl md:text-2xl mb-8 text-secondary-100">
              {baseProps.tagline}
            </p>
          )}
          {storeType && (
            <p className="text-lg mb-8 text-secondary-200">
              Your Trusted {storeType} Store
            </p>
          )}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button className="bg-accent-500 hover:bg-accent-600 text-white px-8 py-3 rounded-lg font-semibold text-lg transition-colors shadow-lg hover:shadow-xl">
              Shop Now
            </button>
            <button className="bg-white hover:bg-gray-100 text-secondary-600 px-8 py-3 rounded-lg font-semibold text-lg transition-colors shadow-lg hover:shadow-xl">
              View Catalog
            </button>
          </div>
        </div>
      </section>

      {/* Quick Info Bar */}
      <section className="bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {baseProps.phone && (
              <div className="flex items-center justify-center">
                <Phone className="w-5 h-5 text-secondary-600 mr-2" />
                <span className="text-gray-700">{baseProps.phone}</span>
              </div>
            )}
            {baseProps.address && (
              <div className="flex items-center justify-center">
                <MapPin className="w-5 h-5 text-secondary-600 mr-2" />
                <span className="text-gray-700">{baseProps.address}</span>
              </div>
            )}
            {hours && (
              <div className="flex items-center justify-center">
                <Clock className="w-5 h-5 text-secondary-600 mr-2" />
                <span className="text-gray-700">{hours}</span>
              </div>
            )}
            {rating && (
              <div className="flex items-center justify-center">
                <Star className="w-5 h-5 text-accent-500 mr-2" />
                <span className="text-gray-700">{rating}/5</span>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4 font-heading">
              Our Services
            </h2>
            <p className="text-xl text-gray-600">
              We provide comprehensive solutions for all your needs
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {services.map((service, index) => (
              <div key={index} className="text-center p-6 bg-gray-50 rounded-lg hover:shadow-md transition-shadow">
                <div className="w-16 h-16 bg-secondary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <ShoppingBag className="w-8 h-8 text-secondary-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {service}
                </h3>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4 font-heading">
              Featured Products
            </h2>
            <p className="text-xl text-gray-600">
              Discover our most popular items
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {featuredProducts.map((product, index) => (
              <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                <div className="h-48 bg-gradient-to-br from-secondary-100 to-secondary-200 flex items-center justify-center">
                  <span className="text-4xl">🛍️</span>
                </div>
                <div className="p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {product}
                  </h3>
                  <p className="text-gray-600 text-sm mb-3">
                    High-quality product
                  </p>
                  <div className="flex justify-between items-center">
                    <span className="text-lg font-bold text-secondary-600">$99.99</span>
                    <button className="bg-secondary-600 hover:bg-secondary-700 text-white px-3 py-1 rounded text-sm transition-colors">
                      Add to Cart
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4 font-heading">
              About {baseProps.businessName}
            </h2>
            {baseProps.description && (
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                {baseProps.description}
              </p>
            )}
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-secondary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Truck className="w-8 h-8 text-secondary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Fast Delivery</h3>
              <p className="text-gray-600">Quick and reliable shipping</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-secondary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CreditCard className="w-8 h-8 text-secondary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Secure Payment</h3>
              <p className="text-gray-600">Multiple payment options</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-secondary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Star className="w-8 h-8 text-secondary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Quality Guarantee</h3>
              <p className="text-gray-600">100% satisfaction guaranteed</p>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4 font-heading">
              Get in Touch
            </h2>
            <p className="text-xl text-gray-600">
              We're here to help with any questions
            </p>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-6">Contact Information</h3>
              <div className="space-y-4">
                {baseProps.phone && (
                  <div className="flex items-center">
                    <Phone className="w-5 h-5 text-secondary-600 mr-3" />
                    <span className="text-gray-700">{baseProps.phone}</span>
                  </div>
                )}
                {baseProps.email && (
                  <div className="flex items-center">
                    <Mail className="w-5 h-5 text-secondary-600 mr-3" />
                    <span className="text-gray-700">{baseProps.email}</span>
                  </div>
                )}
                {baseProps.address && (
                  <div className="flex items-center">
                    <MapPin className="w-5 h-5 text-secondary-600 mr-3" />
                    <span className="text-gray-700">{baseProps.address}</span>
                  </div>
                )}
                {hours && (
                  <div className="flex items-center">
                    <Clock className="w-5 h-5 text-secondary-600 mr-3" />
                    <span className="text-gray-700">{hours}</span>
                  </div>
                )}
              </div>
              
              {paymentMethods.length > 0 && (
                <div className="mt-8">
                  <h4 className="text-lg font-semibold text-gray-900 mb-3">Payment Methods</h4>
                  <div className="flex flex-wrap gap-2">
                    {paymentMethods.map((method, index) => (
                      <span key={index} className="bg-white px-3 py-1 rounded-full text-sm text-gray-700 border">
                        {method}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            <div className="bg-white p-8 rounded-lg shadow-md">
              <h3 className="text-2xl font-semibold text-gray-900 mb-6">Send us a Message</h3>
              <form className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <input
                    type="text"
                    placeholder="First Name"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-secondary-500 focus:border-transparent"
                  />
                  <input
                    type="text"
                    placeholder="Last Name"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-secondary-500 focus:border-transparent"
                  />
                </div>
                <input
                  type="email"
                  placeholder="Email"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-secondary-500 focus:border-transparent"
                />
                <textarea
                  placeholder="Message"
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-secondary-500 focus:border-transparent"
                ></textarea>
                <button
                  type="submit"
                  className="w-full bg-secondary-600 hover:bg-secondary-700 text-white py-3 rounded-lg font-semibold transition-colors"
                >
                  Send Message
                </button>
              </form>
            </div>
          </div>
        </div>
      </section>
    </BaseTemplate>
  );
};
