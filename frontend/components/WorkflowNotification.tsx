import React, { useEffect, useState } from 'react';
import { CheckCircle, AlertCircle, Info, X, Clock } from 'lucide-react';

interface WorkflowNotificationProps {
  workflowProgress: any;
  lastUpdated: Date | null;
  previousProgress: any;
}

interface Notification {
  id: string;
  type: 'success' | 'info' | 'warning' | 'error';
  message: string;
  timestamp: Date;
  autoHide?: boolean;
}

export default function WorkflowNotification({
  workflowProgress,
  lastUpdated,
  previousProgress
}: WorkflowNotificationProps) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [previousProgressRef, setPreviousProgressRef] = useState<any>(null);

  // Detect workflow changes and create notifications
  useEffect(() => {
    if (!workflowProgress || !previousProgressRef) {
      setPreviousProgressRef(workflowProgress);
      return;
    }

    const newNotifications: Notification[] = [];

    // Check for step advancement
    if (workflowProgress.current_step !== previousProgressRef.current_step) {
      const stepName = workflowProgress.current_step.replace('_', ' ').replace(/\b\w/g, (l: string) =>
        l.toUpperCase());
      newNotifications.push({
        id: `step-${Date.now()}`,
        type: 'success',
        message: `✅ Advanced to: ${stepName}`,
        timestamp: new Date(),
        autoHide: true
      });
    }

    // Check for business discovery changes
    if (workflowProgress.businesses_discovered > previousProgressRef.businesses_discovered) {
      const newCount = workflowProgress.businesses_discovered - previousProgressRef.businesses_discovered;
      newNotifications.push({
        id: `businesses-${Date.now()}`,
        type: 'info',
        message: `🔍 Discovered ${newCount} new businesses`,
        timestamp: new Date(),
        autoHide: true
      });
    }

    // Check for website scoring changes
    if (workflowProgress.businesses_scored > previousProgressRef.businesses_scored) {
      const newCount = workflowProgress.businesses_scored - previousProgressRef.businesses_scored;
      newNotifications.push({
        id: `scored-${Date.now()}`,
        type: 'info',
        message: `📊 Scored ${newCount} websites`,
        timestamp: new Date(),
        autoHide: true
      });
    }

    // Check for demo site generation
    if (workflowProgress.demo_sites_generated > previousProgressRef.demo_sites_generated) {
      const newCount = workflowProgress.demo_sites_generated - previousProgressRef.demo_sites_generated;
      newNotifications.push({
        id: `demos-${Date.now()}`,
        type: 'success',
        message: `🏗️ Generated ${newCount} demo sites`,
        timestamp: new Date(),
        autoHide: true
      });
    }

    // Check for data export
    if (workflowProgress.has_exported_data && !previousProgressRef.has_exported_data) {
      newNotifications.push({
        id: `export-${Date.now()}`,
        type: 'success',
        message: `📋 Data exported successfully`,
        timestamp: new Date(),
        autoHide: true
      });
    }

    // Check for outreach generation
    if (workflowProgress.has_outreach && !previousProgressRef.has_outreach) {
      newNotifications.push({
        id: `outreach-${Date.now()}`,
        type: 'success',
        message: `💬 Outreach messages generated`,
        timestamp: new Date(),
        autoHide: true
      });
    }

    // Check for workflow completion
    if (workflowProgress.current_step === 'COMPLETED' && previousProgressRef.current_step !== 'COMPLETED') {
      newNotifications.push({
        id: `complete-${Date.now()}`,
        type: 'success',
        message: `🎉 Workflow completed successfully!`,
        timestamp: new Date(),
        autoHide: false
      });
    }

    // Check for rate limit events
    if (workflowProgress.errors && workflowProgress.errors.length > (previousProgressRef.errors?.length || 0)) {
      const newErrors = workflowProgress.errors.slice(previousProgressRef.errors?.length || 0);
      newErrors.forEach((error: string) => {
        if (error.includes('Google throttled us') || error.includes('retrying in')) {
          newNotifications.push({
            id: `rate-limit-${Date.now()}-${Math.random()}`,
            type: 'warning',
            message: error,
            timestamp: new Date(),
            autoHide: true
          });
        } else {
          newNotifications.push({
            id: `error-${Date.now()}-${Math.random()}`,
            type: 'error',
            message: `❌ ${error}`,
            timestamp: new Date(),
            autoHide: false
          });
        }
      });
    }

    // Check for warnings
    if (workflowProgress.warnings && workflowProgress.warnings.length > previousProgressRef.warnings?.length) {
      const newWarnings = workflowProgress.warnings.slice(previousProgressRef.warnings?.length || 0);
      newWarnings.forEach((warning: string) => {
        newNotifications.push({
          id: `warning-${Date.now()}-${Math.random()}`,
          type: 'warning',
          message: `⚠️ ${warning}`,
          timestamp: new Date(),
          autoHide: true
        });
      });
    }

    // Add new notifications
    if (newNotifications.length > 0) {
      setNotifications(prev => [...prev, ...newNotifications]);
    }

    // Update previous progress reference
    setPreviousProgressRef(workflowProgress);
  }, [workflowProgress, previousProgressRef]);

  // Auto-hide notifications
  useEffect(() => {
    const autoHideNotifications = notifications.filter(n => n.autoHide);
    
    if (autoHideNotifications.length > 0) {
      const timer = setTimeout(() => {
        setNotifications(prev => prev.filter(n => !n.autoHide));
      }, 5000); // Hide after 5 seconds

      return () => clearTimeout(timer);
    }
  }, [notifications]);

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'info':
        return <Info className="w-4 h-4 text-blue-500" />;
      case 'warning':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Info className="w-4 h-4 text-gray-500" />;
    }
  };

  const getNotificationStyles = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'info':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'error':
        return 'bg-red-50 border-red-200 text-red-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  if (notifications.length === 0) {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`flex items-start space-x-3 p-3 rounded-lg border shadow-lg transition-all duration-300 ${getNotificationStyles(notification.type)}`}
        >
          <div className="flex-shrink-0 mt-0.5">
            {getNotificationIcon(notification.type)}
          </div>
          
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium">{notification.message}</p>
            <div className="flex items-center space-x-2 mt-1">
              <Clock className="w-3 h-3 text-gray-500" />
              <span className="text-xs text-gray-500">
                {notification.timestamp.toLocaleTimeString()}
              </span>
            </div>
          </div>
          
          <button
            onClick={() => removeNotification(notification.id)}
            className="flex-shrink-0 p-1 rounded-full hover:bg-black/10 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ))}
    </div>
  );
}
