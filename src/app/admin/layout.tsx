"use client";

import { useState } from "react";
import { ClipizyLogo } from "@/components/common/clipizy-logo";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Home,
  FileText,
  Settings,
  LogOut,
  User,
  Menu,
  X,
  Calendar,
  Package,
  DollarSign,
  Link as LinkIcon,
  Users,
  Coins,
  Database
} from "lucide-react";
import { useAuth } from "@/contexts/auth-context";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { AdminRoute } from "@/components/layout/admin-route";

const adminNavigation = [
  { name: "Overview", href: "/admin/overview", icon: Home },
  { name: "Products", href: "/admin/products", icon: Package },
  { name: "Prices", href: "/admin/prices", icon: DollarSign },
  { name: "Payment Links", href: "/admin/payment-links", icon: LinkIcon },
  { name: "Customers", href: "/admin/customers", icon: Users },
  { name: "Credits", href: "/admin/credits", icon: Coins },
  { name: "Database", href: "/admin/database", icon: Database },
  { name: "Calendar", href: "/admin/posts/calendar", icon: Calendar },
  { name: "Posts", href: "/admin/posts", icon: FileText },
  { name: "Settings", href: "/admin/settings", icon: Settings },
];

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const pathname = usePathname();
  const { user, signOut } = useAuth();
  const router = useRouter();

  return (
    <AdminRoute>
      <div className="min-h-screen bg-background">
      {/* MOBILE SIDEBAR OVERLAY */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* SIDEBAR */}
      <div className={`fixed inset-y-0 left-0 z-[60] w-64 bg-gray-900 transform transition-transform duration-200 ease-in-out md:translate-x-0 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="flex flex-col h-full">
          {/* SIDEBAR HEADER */}
          <div className="flex items-center justify-between p-4">
            <Link href="/admin" className="flex items-center gap-2 group">
              <ClipizyLogo className="w-6 h-6 group-hover:scale-110 transition-transform duration-200" />
              <span className="text-white font-semibold">Admin Panel</span>
            </Link>
            <Button
              variant="ghost"
              size="sm"
              className="md:hidden text-white hover:bg-white/10"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* NAVIGATION */}
          <nav className="flex-1 px-4 py-4">
            <ul className="space-y-2">
              {adminNavigation.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;

                return (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200 ${
                        isActive
                          ? "bg-white/20 text-white"
                          : "text-white/70 hover:text-white hover:bg-white/10"
                      }`}
                      onClick={() => setSidebarOpen(false)}
                    >
                      <Icon className="w-5 h-5" />
                      <span>{item.name}</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>

          {/* USER PROFILE */}
          <div className="p-4 border-t border-white/10">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{user?.email}</p>
                <p className="text-xs text-white/70">Administrator</p>
              </div>
            </div>
            <Button
              variant="ghost"
              className="w-full justify-start text-white/70 hover:text-white hover:bg-white/10"
              onClick={signOut}
            >
              <LogOut className="w-4 h-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="md:ml-64">
        {/* MOBILE MENU BUTTON */}
        <div className="md:hidden fixed top-4 left-4 z-40">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(true)}
            className="bg-gray-900/80 backdrop-blur border border-gray-700 text-white hover:bg-gray-800"
          >
            <Menu className="h-5 w-5" />
          </Button>
        </div>

        {/* PAGE CONTENT */}
        <main className="flex-1 min-h-screen bg-background">
          {children}
        </main>
      </div>
    </div>
    </AdminRoute>
  );
}
