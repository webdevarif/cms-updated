'use client';

import React, { useEffect, useState } from 'react';

export function DarkModeTest() {
  const [htmlClasses, setHtmlClasses] = useState('');
  const [bodyClasses, setBodyClasses] = useState('');
  const [hasDarkClass, setHasDarkClass] = useState(false);

  useEffect(() => {
    // Update classes when component mounts or theme changes
    const updateClasses = () => {
      if (typeof document !== 'undefined') {
        setHtmlClasses(document.documentElement.className || 'none');
        setBodyClasses(document.body.className || 'none');
        setHasDarkClass(document.documentElement.classList.contains('dark'));
      }
    };

    updateClasses();

    // Listen for DOM changes
    if (typeof document !== 'undefined') {
      const observer = new MutationObserver(() => {
        updateClasses();
      });

      observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['class']
      });

      observer.observe(document.body, {
        attributes: true,
        attributeFilter: ['class']
      });

      return () => {
        observer.disconnect();
      };
    }
  }, []);

  return (
    <div className="p-4 space-y-4">
      <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 transition-colors">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Dark Mode Test - Basic Colors
        </h3>
        <p className="text-gray-600 dark:text-gray-300">
          This should change colors when dark mode is toggled.
        </p>
      </div>

      <div className="p-4 bg-blue-50 dark:bg-blue-900 rounded-lg border border-blue-200 dark:border-blue-700 transition-colors">
        <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100">
          Blue Theme Test
        </h3>
        <p className="text-blue-600 dark:text-blue-300">
          This blue theme should also adapt to dark mode.
        </p>
      </div>

      <div className="p-4 bg-green-50 dark:bg-green-900 rounded-lg border border-green-200 dark:border-green-700 transition-colors">
        <h3 className="text-lg font-semibold text-green-900 dark:text-green-100">
          Green Theme Test
        </h3>
        <p className="text-green-600 dark:text-green-300">
          This green theme should also adapt to dark mode.
        </p>
      </div>

      <div className="flex gap-2">
        <div className="px-3 py-1 bg-gray-100 dark:bg-gray-800 rounded text-sm text-gray-700 dark:text-gray-300">
          Gray 100/800
        </div>
        <div className="px-3 py-1 bg-gray-200 dark:bg-gray-700 rounded text-sm text-gray-800 dark:text-gray-200">
          Gray 200/700
        </div>
        <div className="px-3 py-1 bg-gray-300 dark:bg-gray-600 rounded text-sm text-gray-900 dark:text-gray-100">
          Gray 300/600
        </div>
        <div className="px-3 py-1 bg-gray-400 dark:bg-gray-500 rounded text-sm text-white dark:text-gray-100">
          Gray 400/500
        </div>
      </div>

      {/* Debug Info */}
      <div className="p-4 bg-purple-50 dark:bg-purple-900 rounded-lg border border-purple-200 dark:border-purple-700">
        <h3 className="text-lg font-semibold text-purple-900 dark:text-purple-100">
          Debug Information
        </h3>
        <div className="space-y-2 text-sm text-purple-800 dark:text-purple-200">
          <div>HTML classes: <span className="font-mono bg-purple-100 dark:bg-purple-800 px-2 py-1 rounded">{htmlClasses}</span></div>
          <div>Body classes: <span className="font-mono bg-purple-100 dark:bg-purple-800 px-2 py-1 rounded">{bodyClasses}</span></div>
          <div>Has dark class: <span className="font-mono bg-purple-100 dark:bg-purple-800 px-2 py-1 rounded">{hasDarkClass ? 'YES' : 'NO'}</span></div>
        </div>
      </div>
    </div>
  );
}

export default DarkModeTest
