'use client';

import { ReactNode } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { Chrome as Home, Upload, FileText, ChartBar as BarChart3, Sparkles, Folder } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DashboardLayoutProps {
  children: ReactNode;
}

const navigation = [
  { name: 'Home', href: '/', icon: Home },
  { name: 'Projects', href: '/projects', icon: Folder },
  { name: 'Upload Dataset', href: '/upload', icon: Upload },
  { name: 'Preview Dataset', href: '/preview', icon: FileText },
  { name: 'Analysis Dashboard', href: '/analysis', icon: BarChart3 },
  { name: 'Reports', href: '/reports', icon: FileText },
];

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="flex h-screen">
        <aside className="w-64 bg-white border-r border-slate-200 flex flex-col">
          <div className="p-6 border-b border-slate-200">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-blue-500 rounded-lg">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="font-bold text-slate-900">AI Data Cleaner</h1>
                <p className="text-xs text-slate-500">Powered by AI</p>
              </div>
            </div>
          </div>

          <nav className="flex-1 p-4">
            <ul className="space-y-2">
              {navigation.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;

                return (
                  <li key={item.name}>
                    <button
                      onClick={() => router.push(item.href)}
                      className={cn(
                        'w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors',
                        isActive
                          ? 'bg-blue-50 text-blue-700'
                          : 'text-slate-700 hover:bg-slate-100'
                      )}
                    >
                      <Icon className="h-5 w-5" />
                      {item.name}
                    </button>
                  </li>
                );
              })}
            </ul>
          </nav>

          <div className="p-4 border-t border-slate-200">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-xs font-semibold text-blue-900 mb-1">Need Help?</p>
              <p className="text-xs text-blue-700">
                Check our documentation for detailed guides and examples.
              </p>
            </div>
          </div>
        </aside>

        <main className="flex-1 overflow-auto">
          <div className="p-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
