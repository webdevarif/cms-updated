'use client';

import React from 'react'
import LangSwitcher from '@/components/lang-switcher'
import ModeSwitcher from '@/components/mode-switcher'

const SwitchersDemo = () => {
  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-3 min-w-0">
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">Language:</span>
        <LangSwitcher />
      </div>

      <div className="flex items-center gap-3 min-w-0">
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">Theme:</span>
        <ModeSwitcher />
      </div>
    </div>
  )
}

export default SwitchersDemo
