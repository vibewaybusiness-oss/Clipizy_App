"use client";

import { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark' | 'system';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  resolvedTheme: 'light' | 'dark';
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('system');
  const [mounted, setMounted] = useState(false);

  // Get the resolved theme (actual light/dark based on system preference)
  const getResolvedTheme = (currentTheme: Theme): 'light' | 'dark' => {
    if (typeof window === 'undefined') return 'light';
    if (currentTheme === 'system') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return currentTheme;
  };

  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light');

  // Initialize theme on mount with hydration-safe approach
  useEffect(() => {
    setMounted(true);
    
    // Check for saved theme preference from appSettings (same as SettingsTab)
    const savedAppSettings = localStorage.getItem('appSettings');
    let initialTheme: Theme = 'system';
    
    if (savedAppSettings) {
      try {
        const parsedSettings = JSON.parse(savedAppSettings);
        if (parsedSettings.theme && ['light', 'dark', 'system'].includes(parsedSettings.theme)) {
          initialTheme = parsedSettings.theme;
        }
      } catch (e) {
        console.warn('Failed to parse appSettings:', e);
      }
    }
    
    setTheme(initialTheme);
    
    // Apply initial theme immediately
    const resolved = getResolvedTheme(initialTheme);
    setResolvedTheme(resolved);
    
    // Apply theme to document with a small delay to ensure hydration is complete
    setTimeout(() => {
      const root = document.documentElement;
      root.classList.remove('light', 'dark');
      root.classList.add(resolved);
    }, 0);
  }, []);

  // Update theme when theme changes
  useEffect(() => {
    if (mounted) {
      // Save to appSettings (same as SettingsTab)
      const savedAppSettings = localStorage.getItem('appSettings');
      let appSettings = { theme: 'system', language: 'en', timezone: 'UTC' };
      
      if (savedAppSettings) {
        try {
          appSettings = { ...appSettings, ...JSON.parse(savedAppSettings) };
        } catch (e) {
          console.warn('Failed to parse appSettings:', e);
        }
      }
      
      appSettings.theme = theme;
      localStorage.setItem('appSettings', JSON.stringify(appSettings));
      
      const resolved = getResolvedTheme(theme);
      setResolvedTheme(resolved);
      
      // Apply theme to document with hydration-safe approach
      const root = document.documentElement;
      root.classList.remove('light', 'dark');
      root.classList.add(resolved);
    }
  }, [theme, mounted]);

  // Listen for system theme changes when theme is set to 'system'
  useEffect(() => {
    if (!mounted || theme !== 'system') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => {
      const resolved = getResolvedTheme(theme);
      setResolvedTheme(resolved);
      
      // Apply theme to document with hydration-safe approach
      const root = document.documentElement;
      root.classList.remove('light', 'dark');
      root.classList.add(resolved);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [mounted, theme]);

  const toggleTheme = () => {
    setTheme(prev => {
      if (prev === 'light') return 'dark';
      if (prev === 'dark') return 'system';
      return 'light';
    });
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggleTheme, resolvedTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
