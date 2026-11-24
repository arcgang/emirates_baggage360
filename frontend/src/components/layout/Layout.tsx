/**
 * Main application layout shell.
 * Contains header, sidebar, and main content area.
 */
import { ReactNode } from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="app-main flex-1 bg-ek-gray-light p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
