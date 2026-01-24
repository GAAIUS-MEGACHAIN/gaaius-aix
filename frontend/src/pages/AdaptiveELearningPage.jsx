import React from 'react';
import AdaptiveELearningTab from '@/components/AdaptiveELearningTab';

/**
 * AdaptiveELearningPage
 * 
 * Full-page wrapper for the Adaptive eLearning component
 * Integrates personalized learning paths with AI Tutoring proficiency tracking
 * 
 * Features:
 * - Course browsing and enrollment
 * - Adaptive learning path creation
 * - Progress tracking with proficiency-based recommendations
 * - Weak area identification with tutoring integration
 * - Real-time analytics and dashboards
 */
export default function AdaptiveELearningPage() {
  return (
    <div className="h-screen bg-[#050505] flex flex-col overflow-hidden">
      <AdaptiveELearningTab />
    </div>
  );
}
