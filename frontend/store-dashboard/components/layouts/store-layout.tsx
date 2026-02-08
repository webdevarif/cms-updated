'use client';

import React, { useState, use, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { setCurrentStoreId } from '@/lib/current-store';
// UI components are used through their respective props
import {
  Users,
  Key,
  Settings,
  Menu,
  // X icon is not currently used
  ArrowLeft,
  Shield,
  LayoutDashboard,
  FileText,
  ChevronDown,
  ChevronRight,
  Palette,
  Hammer
} from 'lucide-react';

interface StoreLayoutProps {
  children: React.ReactNode;
  params: Promise<{
    id: string;
  }>;
}

const StoreLayout: React.FC<StoreLayoutProps> = ({ children, params }) => {
  const t = useTranslations('store');
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [postsOpen, setPostsOpen] = useState(false);

  // Unwrap async params with React.use()
  const resolvedParams = use(params);
  const storeId = resolvedParams.id;

  // Set current store ID for API requests
  useEffect(() => {
    if (storeId) {
      console.log('Setting current store ID:', storeId);
      setCurrentStoreId(storeId);
    }
  }, [storeId]);

  const navigation = [
    { name: 'overview', href: `/stores/${storeId}`, icon: LayoutDashboard },
    { name: 'themes', href: `/stores/${storeId}/themes`, icon: Palette },
    { name: 'builder', href: `/stores/${storeId}/builder`, icon: Hammer },
    { name: 'users', href: `/stores/${storeId}/users`, icon: Users },
    { name: 'roles', href: `/stores/${storeId}/roles`, icon: Shield },
    { name: 'api-keys', href: `/stores/${storeId}/api-keys`, icon: Key },
    { name: 'settings', href: `/stores/${storeId}/settings`, icon: Settings },
  ];

  const postsNavigation = [
    { name: 'posts', href: `/stores/${storeId}/posts`, icon: FileText },
    { name: 'pages', href: `/stores/${storeId}/posts/pages`, icon: FileText },
    { name: 'categories', href: `/stores/${storeId}/posts/categories`, icon: FileText },
    { name: 'comments', href: `/stores/${storeId}/posts/comments`, icon: FileText },
    { name: 'post-types', href: `/stores/${storeId}/posts/post-types`, icon: FileText },
    { name: 'metadata', href: `/stores/${storeId}/posts/metadata`, icon: FileText },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex">
{/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-label="Close sidebar"
        >
          <span className="sr-only">Close sidebar</span>
        </button>
      )}

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 flex flex-col`}>
        <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
          <div className="flex items-center flex-shrink-0 px-4">
            <Link href="/dashboard" className="flex items-center text-gray-900">
              <ArrowLeft className="h-5 w-5 mr-2" />
              <span className="text-lg font-semibold">{t('backToDashboard')}</span>
            </Link>
          </div>
          <nav className="mt-5 flex-1 px-2 space-y-1">
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                    isActive
                      ? 'bg-gray-100 text-gray-900'
                      : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon
                    className={`mr-3 h-5 w-5 ${
                      isActive ? 'text-gray-600' : 'text-gray-500 group-hover:text-gray-600'
                    }`}
                    aria-hidden="true"
                  />
                  {t(`navigation.${item.name}`)}
                </Link>
              );
            })}

            {/* Posts Submenu */}
            <div className="space-y-1">
              <button
                onClick={() => setPostsOpen(!postsOpen)}
                className={`w-full group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                  pathname.startsWith('/posts')
                    ? 'bg-gray-100 text-gray-900'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <FileText
                  className={`mr-3 h-5 w-5 ${
                    pathname.startsWith('/posts') ? 'text-gray-600' : 'text-gray-500 group-hover:text-gray-600'
                  }`}
                  aria-hidden="true"
                />
                <span className="flex-1 text-left">Posts</span>
                {postsOpen ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                )}
              </button>

              {postsOpen && (
                <div className="ml-6 space-y-1">
                  {postsNavigation.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                      <Link
                        key={item.name}
                        href={item.href}
                        className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                          isActive
                            ? 'bg-gray-100 text-gray-900'
                            : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                        }`}
                        onClick={() => setSidebarOpen(false)}
                      >
                        <item.icon
                          className={`mr-3 h-4 w-4 ${
                            isActive ? 'text-gray-600' : 'text-gray-500 group-hover:text-gray-600'
                          }`}
                          aria-hidden="true"
                        />
                        {item.name.charAt(0).toUpperCase() + item.name.slice(1).replace('-', ' ')}
                      </Link>
                    );
                  })}
                </div>
              )}
            </div>
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar for mobile */}
        <div className="sticky top-0 z-10 bg-white border-b border-gray-200 lg:hidden">
          <div className="flex items-center justify-between h-16 px-4">
            <button
              type="button"
              className="text-gray-500 hover:text-gray-600"
              onClick={() => setSidebarOpen(true)}
            >
              <span className="sr-only">Open sidebar</span>
              <Menu className="h-6 w-6" aria-hidden="true" />
            </button>
            <div className="flex-1 text-center">
              <h1 className="text-lg font-medium text-gray-900">
                {t('storeManagement')}
              </h1>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default StoreLayout;
