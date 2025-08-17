import React from 'react';
import { cn } from '@/utils/cn';

export interface BaseTemplateProps {
  businessName: string;
  tagline?: string;
  description?: string;
  phone?: string;
  email?: string;
  address?: string;
  website?: string;
  services?: string[];
  className?: string;
  children?: React.ReactNode;
}

export const BaseTemplate: React.FC<BaseTemplateProps> = ({
  businessName,
  tagline,
  description,
  phone,
  email,
  address,
  website,
  services = [],
  className,
  children
}) => {
  return (
    <div className={cn("min-h-screen bg-white", className)}>
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900 font-heading">
                {businessName}
              </h1>
              {tagline && (
                <span className="ml-3 text-gray-600 text-sm hidden sm:block">
                  {tagline}
                </span>
              )}
            </div>
            <nav className="hidden md:flex space-x-8">
              <a href="#services" className="text-gray-700 hover:text-primary-600 transition-colors">
                Services
              </a>
              <a href="#about" className="text-gray-700 hover:text-primary-600 transition-colors">
                About
              </a>
              <a href="#contact" className="text-gray-700 hover:text-primary-600 transition-colors">
                Contact
              </a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">{businessName}</h3>
              {description && (
                <p className="text-gray-300 text-sm">{description}</p>
              )}
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Contact Info</h4>
              <div className="space-y-2 text-sm text-gray-300">
                {phone && <p>📞 {phone}</p>}
                {email && <p>✉️ {email}</p>}
                {address && <p>📍 {address}</p>}
              </div>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
              <div className="space-y-2">
                <a href="#services" className="block text-gray-300 hover:text-white text-sm transition-colors">
                  Services
                </a>
                <a href="#about" className="block text-gray-300 hover:text-white text-sm transition-colors">
                  About Us
                </a>
                <a href="#contact" className="block text-gray-300 hover:text-white text-sm transition-colors">
                  Contact
                </a>
              </div>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm text-gray-400">
            <p>&copy; {new Date().getFullYear()} {businessName}. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};
