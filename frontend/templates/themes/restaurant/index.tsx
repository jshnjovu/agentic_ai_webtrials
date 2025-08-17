import React from 'react';
import { BaseTemplate, BaseTemplateProps } from '../../base';
import { MapPin, Phone, Mail, Clock, Star } from 'lucide-react';

export interface RestaurantTemplateProps extends BaseTemplateProps {
  cuisine?: string;
  hours?: string;
  rating?: number;
  specialties?: string[];
  menuHighlights?: string[];
}

export const RestaurantTemplate: React.FC<RestaurantTemplateProps> = ({
  cuisine,
  hours,
  rating,
  specialties = [],
  menuHighlights = [],
  ...baseProps
}) => {
  return (
    <BaseTemplate {...baseProps}>
      {/* Hero Section */}
      <section className="relative bg-gradient-to-r from-primary-600 to-primary-800 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 font-heading">
            {baseProps.businessName}
          </h1>
          {baseProps.tagline && (
            <p className="text-xl md:text-2xl mb-8 text-primary-100">
              {baseProps.tagline}
            </p>
          )}
          {cuisine && (
            <p className="text-lg mb-8 text-primary-200">
              Authentic {cuisine} Cuisine
            </p>
          )}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button className="bg-accent-500 hover:bg-accent-600 text-white px-8 py-3 rounded-lg font-semibold text-lg transition-colors shadow-lg hover:shadow-xl">
              View Menu
            </button>
            <button className="bg-white hover:bg-gray-100 text-primary-600 px-8 py-3 rounded-lg font-semibold text-lg transition-colors shadow-lg hover:shadow-xl">
              Make Reservation
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
                <Phone className="w-5 h-5 text-primary-600 mr-2" />
                <span className="text-gray-700">{baseProps.phone}</span>
              </div>
            )}
            {baseProps.address && (
              <div className="flex items-center justify-center">
                <MapPin className="w-5 h-5 text-primary-600 mr-2" />
                <span className="text-gray-700">{baseProps.address}</span>
              </div>
            )}
            {hours && (
              <div className="flex items-center justify-center">
                <Clock className="w-5 h-5 text-primary-600 mr-2" />
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
          
          {specialties.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
              {specialties.map((specialty, index) => (
                <div key={index} className="text-center p-6 bg-gray-50 rounded-lg">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {specialty}
                  </h3>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Services/Menu Section */}
      <section id="services" className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4 font-heading">
              Our Menu
            </h2>
            <p className="text-xl text-gray-600">
              Discover our carefully crafted dishes
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {menuHighlights.map((item, index) => (
              <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                <div className="h-48 bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center">
                  <span className="text-4xl">🍽️</span>
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {item}
                  </h3>
                  <p className="text-gray-600">
                    Delicious and authentic preparation
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4 font-heading">
              Visit Us Today
            </h2>
            <p className="text-xl text-gray-600">
              We'd love to serve you
            </p>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-6">Contact Information</h3>
              <div className="space-y-4">
                {baseProps.phone && (
                  <div className="flex items-center">
                    <Phone className="w-5 h-5 text-primary-600 mr-3" />
                    <span className="text-gray-700">{baseProps.phone}</span>
                  </div>
                )}
                {baseProps.email && (
                  <div className="flex items-center">
                    <Mail className="w-5 h-5 text-primary-600 mr-3" />
                    <span className="text-gray-700">{baseProps.email}</span>
                  </div>
                )}
                {baseProps.address && (
                  <div className="flex items-center">
                    <MapPin className="w-5 h-5 text-primary-600 mr-3" />
                    <span className="text-gray-700">{baseProps.address}</span>
                  </div>
                )}
                {hours && (
                  <div className="flex items-center">
                    <Clock className="w-5 h-5 text-primary-600 mr-3" />
                    <span className="text-gray-700">{hours}</span>
                  </div>
                )}
              </div>
            </div>
            
            <div className="bg-gray-100 p-8 rounded-lg">
              <h3 className="text-2xl font-semibold text-gray-900 mb-6">Make a Reservation</h3>
              <form className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <input
                    type="text"
                    placeholder="Name"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                  <input
                    type="email"
                    placeholder="Email"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <input
                    type="date"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                  <input
                    type="time"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <input
                  type="number"
                  placeholder="Number of Guests"
                  min="1"
                  max="20"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <button
                  type="submit"
                  className="w-full bg-primary-600 hover:bg-primary-700 text-white py-3 rounded-lg font-semibold transition-colors"
                >
                  Book Table
                </button>
              </form>
            </div>
          </div>
        </div>
      </section>
    </BaseTemplate>
  );
};
