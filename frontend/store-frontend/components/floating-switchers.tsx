'use client';

import React from 'react'
import LangSwitcher from '@/components/lang-switcher'
import ModeSwitcher from '@/components/mode-switcher'

interface FloatingSwitchersProps {
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left'
  className?: string
}

const FloatingSwitchers = ({ 
  position = 'bottom-right', 
  className = '' 
}: FloatingSwitchersProps) => {
  const positionClasses = {
    'bottom-right': 'bottom-8 right-8',
    'bottom-left': 'bottom-8 left-8',
    'top-right': 'top-8 right-8',
    'top-left': 'top-8 left-8'
  }

  return (
    <div className={`fixed z-50 ${positionClasses[position]} ${className}`}>
      <div className="flex flex-col gap-3">
        {/* Language Switcher */}
        <div className="relative group">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full blur-lg opacity-75 group-hover:opacity-100 transition-opacity"></div>
          <div className="relative bg-white dark:bg-gray-800 rounded-full p-3 shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300 hover:scale-105">
            <LangSwitcher />
          </div>
        </div>

        {/* Theme Switcher */}
        <div className="relative group">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full blur-lg opacity-75 group-hover:opacity-100 transition-opacity"></div>
          <div className="relative bg-white dark:bg-gray-800 rounded-full p-3 shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300 hover:scale-105">
            <ModeSwitcher />
          </div>
        </div>
      </div>
    </div>
  )
}

export default FloatingSwitchers
