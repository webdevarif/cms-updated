'use client';

import React, { useState } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { useLogout } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Heading } from '@/components/ui/typography';
import {
  Home,
  Store,
  User,
  Menu,
  X,
  LogOut
} from 'lucide-react';

interface DashLayoutProps {
  children: React.ReactNode;
}

const DashLayout: React.FC<DashLayoutProps> = ({ children }) => {
  const t = useTranslations();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { logout, isLoading: logoutLoading } = useLogout();

  const navigation = [
    {
      name: t('dashboard.overview'),
      href: '/dashboard',
      icon: Home,
      current: pathname === '/dashboard'
    },
    {
      name: t('dashboard.stores'),
      href: '/dashboard/stores',
      icon: Store,
      current: pathname === '/dashboard/stores' || pathname.startsWith('/dashboard/stores/')
    },
    {
      name: t('dashboard.profile'),
      href: '/dashboard/profile',
      icon: User,
      current: pathname === '/dashboard/profile'
    }
  ];

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 shadow-lg transform ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 flex flex-col`}>

        {/* Sidebar header */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200 dark:border-gray-700">
          <Heading variant="h3" className="text-gray-900 dark:text-white">
            {t('dashboard.title')}
          </Heading>

          {/* Mobile close button */}
          <Button
            variant="ghost"
            size="sm"
            className="lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-6 w-6" />
          </Button>
        </div>

        {/* Navigation */}
        <nav className="mt-5 px-2 space-y-1">
          {navigation.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                item.current
                  ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                  : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
              }`}
              onClick={() => setSidebarOpen(false)}
            >
              <item.icon
                className={`mr-3 h-5 w-5 flex-shrink-0 ${
                  item.current
                    ? 'text-blue-500 dark:text-blue-400'
                    : 'text-gray-400 dark:text-gray-500 group-hover:text-gray-500 dark:group-hover:text-gray-400'
                }`}
              />
              {item.name}
            </Link>
          ))}
        </nav>

        {/* Logout button */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 dark:border-gray-700">
          <Button
            variant="ghost"
            onClick={handleLogout}
            disabled={logoutLoading}
            className="w-full justify-start text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
          >
            <LogOut className="mr-3 h-5 w-5" />
            {logoutLoading ? t('common.loading') : t('auth.logout')}
          </Button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar for mobile */}
        <div className="sticky top-0 z-10 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 lg:hidden">
          <div className="flex items-center justify-between h-16 px-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="h-6 w-6" />
            </Button>
            <Heading variant="h4" className="text-gray-900 dark:text-white">
              {t('dashboard.title')}
            </Heading>
            <div className="w-10" /> {/* Spacer for centering */}
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashLayout;
