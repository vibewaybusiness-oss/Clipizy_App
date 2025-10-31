"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Plus,
  ArrowRight,
  Coins,
  FolderOpen,
  Settings,
  CreditCard,
  BarChart3,
  Music,
  FileText,
  Zap,
  ShoppingCart,
  Calendar,
  Eye,
  Edit3,
  Clock,
  TrendingUp,
  Users,
  Video,
  Activity,
  Play,
  Download,
  Share2
} from "lucide-react";
import Link from "next/link";
import { ProtectedRoute } from "@/components/layout/protected-route";
import { useState, useEffect, useMemo, useCallback } from "react";
import { useAuth } from "@/contexts/auth-context";
import { useUserOnboarding } from "@/hooks/users/use-user-onboarding";
import { useDashboardData, useDashboardStats } from "@/hooks/dashboard";
import { getStatusColor, getStatusText, formatRelativeDate } from "@/lib/dashboard-utils";

export default function DashboardPage() {
  const { user } = useAuth();
  const userOnboarding = useUserOnboarding();
  
  // Use optimized dashboard data hooks
  const { 
    categorized: { ongoing: ongoingProjects, completed: completedProjects },
    latest: latestProjects,
    loading: dashboardLoading 
  } = useDashboardData();
  
  const { 
    totalProjects, 
    completedProjects: completedCount, 
    ongoingProjects: ongoingCount,
    creditsBalance,
    creditsLoading 
  } = useDashboardStats();

  // Welcome popup removed - no longer showing for new users

  // Utility functions are now imported from shared utilities

  // Memoized stats to prevent recalculation on every render
  const stats = useMemo(() => [
    {
      title: "Total Projects",
      value: totalProjects,
      change: "+12%",
      changeType: "positive",
      icon: FolderOpen,
    },
    {
      title: "Videos Created",
      value: completedCount,
      change: "+8%",
      changeType: "positive",
      icon: Video,
    },
    {
      title: "Processing Time",
      value: "2.3 min",
      change: "-15%",
      changeType: "positive",
      icon: Clock,
    },
    {
      title: "Active Projects",
      value: ongoingCount,
      change: "+3",
      changeType: "positive",
      icon: Activity,
    },
  ], [totalProjects, completedCount, ongoingCount]);

  const quickActions = [
    {
      title: "Create Music Clip",
      description: "AI-generated music videos",
      icon: Music,
      href: "/dashboard/create/music-clip",
      color: "bg-gradient-to-br from-purple-500 to-purple-600",
    },
    {
      title: "Create Script Video",
      description: "Videos from scripts",
      icon: FileText,
      href: "/dashboard/create/script-video",
      color: "bg-gradient-to-br from-green-500 to-green-600",
    },
    {
      title: "Automate Content",
      description: "Automated creation",
      icon: Zap,
      href: "/dashboard/create/automate",
      color: "bg-gradient-to-br from-orange-500 to-orange-600",
    },
    {
      title: "View Projects",
      description: "Manage all projects",
      icon: FolderOpen,
      href: "/dashboard/projects",
      color: "bg-gradient-to-br from-blue-500 to-blue-600",
    },
  ];

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background">
        <div className="p-4 sm:p-6 space-y-4 sm:space-y-6">
          {/* HEADER */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-foreground">Dashboard</h1>
              <p className="text-muted-foreground mt-1 text-sm sm:text-base">Welcome back! Here's your overview.</p>
            </div>
            
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="flex items-center gap-2 px-2 sm:px-3 py-2 bg-muted rounded-lg">
                <Coins className="w-4 h-4 text-yellow-500" />
                <span className="text-xs sm:text-sm font-medium text-foreground">
                  {creditsLoading ? "..." : creditsBalance?.toLocaleString() || 0}
                </span>
              </div>
              
              
              <Button className="bg-blue-600 hover:bg-blue-700 text-white text-sm sm:text-base px-3 sm:px-4" asChild>
                <Link href="/dashboard/create">
                  <Plus className="w-4 h-4 mr-1 sm:mr-2" />
                  <span className="hidden sm:inline">New Project</span>
                  <span className="sm:hidden">New</span>
                </Link>
              </Button>
            </div>
          </div>

          {/* STATS GRID */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <Card key={index}>
                  <CardContent className="p-3 sm:p-6">
                    <div className="flex items-center justify-between">
                      <div className="min-w-0 flex-1">
                        <p className="text-xs sm:text-sm font-medium text-muted-foreground truncate">{stat.title}</p>
                        <p className="text-lg sm:text-2xl font-bold text-foreground">{stat.value}</p>
                        <p className="text-xs text-green-600 dark:text-green-400 flex items-center mt-1">
                          <TrendingUp className="w-3 h-3 mr-1 flex-shrink-0" />
                          <span className="truncate">{stat.change}</span>
                        </p>
                      </div>
                      <div className="p-2 sm:p-3 bg-muted rounded-lg flex-shrink-0 ml-2">
                        <Icon className="w-4 h-4 sm:w-6 sm:h-6 text-muted-foreground" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* MAIN CONTENT GRID */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
            {/* RECENT PROJECTS */}
            <div className="lg:col-span-2">
              <Card className="overflow-hidden">
                <CardHeader className="pb-4 sm:pb-6 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 border-b">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                    <div>
                      <CardTitle className="text-lg sm:text-xl font-bold text-foreground flex items-center gap-2">
                        <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                          <FolderOpen className="w-4 h-4 sm:w-5 sm:h-5 text-blue-600 dark:text-blue-400" />
                        </div>
                        Recent Projects
                      </CardTitle>
                      <CardDescription className="mt-2 text-sm sm:text-base">Your latest work and ongoing projects</CardDescription>
                    </div>
                    <Button variant="outline" size="sm" asChild className="bg-white/50 hover:bg-white/80 dark:bg-gray-800/50 dark:hover:bg-gray-800/80 self-start sm:self-auto">
                      <Link href="/dashboard/projects" className="flex items-center gap-2">
                        View all
                        <ArrowRight className="w-4 h-4" />
                      </Link>
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="p-0">
                  {latestProjects.length > 0 ? (
                    <div className="max-h-96 overflow-y-auto">
                      <div className="space-y-3 sm:space-y-4 p-4 sm:p-6">
                        {latestProjects.map((project, index) => {
                          const IconComponent = project.type === 'music-clip' ? Music : 
                                              project.type === 'video-clip' ? Video : 
                                              project.type === 'short-clip' ? FileText : Music;
                          
                          const isCompleted = project.status === 'completed';
                          const isProcessing = ['processing', 'queued', 'analyzing', 'uploading'].includes(project.status);
                          
                          return (
                            <div key={project.id} className="group relative">
                              <Link href={`/dashboard/create/music-clip?project=${project.id}`} className="block">
                                <div className="relative overflow-hidden rounded-xl border border-border/50 bg-card hover:bg-muted/30 transition-all duration-200 hover:shadow-md hover:border-border cursor-pointer">
                                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-4 sm:p-5 gap-3 sm:gap-0">
                                    <div className="flex items-center gap-3 sm:gap-4 flex-1 min-w-0">
                                      <div className="relative flex-shrink-0">
                                        <div className={`p-2 sm:p-3 rounded-xl shadow-sm transition-colors ${
                                          isCompleted 
                                            ? 'bg-emerald-100 dark:bg-emerald-900/30' 
                                            : isProcessing 
                                            ? 'bg-blue-100 dark:bg-blue-900/30' 
                                            : 'bg-muted'
                                        }`}>
                                          <IconComponent className={`w-5 h-5 sm:w-6 sm:h-6 ${
                                            isCompleted 
                                              ? 'text-emerald-600 dark:text-emerald-400' 
                                              : isProcessing 
                                              ? 'text-blue-600 dark:text-blue-400' 
                                              : 'text-muted-foreground'
                                          }`} />
                                        </div>
                                        {isProcessing && (
                                          <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                                        )}
                                      </div>
                                      
                                      <div className="min-w-0 flex-1">
                                        <div className="flex items-center gap-2 mb-1">
                                          <h3 className="font-semibold text-foreground truncate text-base sm:text-lg">
                                            {project.name || `Untitled Project`}
                                          </h3>
                                          {isCompleted && (
                                            <div className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
                                              <Play className="w-4 h-4" />
                                            </div>
                                          )}
                                        </div>
                                        <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 text-sm text-muted-foreground">
                                          <span className="capitalize font-medium bg-muted px-2 py-1 rounded-md text-xs w-fit">
                                            {project.type?.replace('-', ' ') || 'music clip'}
                                          </span>
                                          <span className="flex items-center gap-1">
                                            <Calendar className="w-3 h-3" />
                                            {formatRelativeDate(project.created_at)}
                                          </span>
                                        </div>
                                      </div>
                                    </div>
                                    
                                    <div className="flex items-center justify-between sm:justify-end gap-2 sm:gap-3 sm:ml-4">
                                      <Badge 
                                        className={`${
                                          isCompleted 
                                            ? 'bg-emerald-500 hover:bg-emerald-600' 
                                            : isProcessing 
                                            ? 'bg-blue-500 hover:bg-blue-600 animate-pulse' 
                                            : 'bg-gray-500 hover:bg-gray-600'
                                        } text-white text-xs font-medium px-2 sm:px-3 py-1 sm:py-1.5 rounded-full shadow-sm transition-colors`}
                                      >
                                        {getStatusText(project.status)}
                                      </Badge>
                                      
                                      <div className="flex items-center gap-1 opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-all duration-200">
                                        <span className="text-sm font-medium text-green-600 dark:text-green-400">
                                          Edit
                                        </span>
                                        {isCompleted && (
                                          <Button variant="ghost" size="sm" asChild className="h-8 w-8 sm:h-9 sm:w-9 p-0 hover:bg-purple-100 dark:hover:bg-purple-900/30">
                                            <Link href={`/dashboard/projects/${project.id}`} title="Download">
                                              <Download className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                                            </Link>
                                          </Button>
                                        )}
                                      </div>
                                    </div>
                                  </div>
                                  
                                  {isProcessing && (
                                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 to-purple-500 animate-pulse"></div>
                                  )}
                                </div>
                              </Link>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-12 sm:py-16 p-4 sm:p-6">
                      <div className="relative">
                        <div className="p-4 sm:p-6 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900/20 dark:to-purple-900/20 rounded-2xl w-20 h-20 sm:w-24 sm:h-24 mx-auto mb-4 sm:mb-6 flex items-center justify-center">
                          <Music className="w-8 h-8 sm:w-10 sm:h-10 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div className="absolute -top-2 -right-2 w-5 h-5 sm:w-6 sm:h-6 bg-yellow-400 rounded-full flex items-center justify-center">
                          <Plus className="w-2.5 h-2.5 sm:w-3 sm:h-3 text-white" />
                        </div>
                      </div>
                      <h3 className="font-bold text-foreground mb-3 text-lg sm:text-xl">No projects yet</h3>
                      <p className="text-muted-foreground mb-6 max-w-sm mx-auto leading-relaxed text-sm sm:text-base">
                        Get started by creating your first music video. It's easy and fun!
                      </p>
                      <Button asChild size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg text-sm sm:text-base">
                        <Link href="/dashboard/create">
                          <Plus className="w-4 h-4 sm:w-5 sm:h-5 mr-2" />
                          Create Your First Project
                        </Link>
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* SIDEBAR */}
            <div className="space-y-4 sm:space-y-6">
              {/* QUICK ACTIONS */}
              <Card>
                <CardHeader className="pb-3 sm:pb-4">
                  <CardTitle className="text-base sm:text-lg font-semibold">Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 sm:space-y-3">
                  {quickActions.map((action, index) => {
                    const Icon = action.icon;
                    return (
                      <Link key={index} href={action.href}>
                        <div className="flex items-center gap-2 sm:gap-3 p-2 sm:p-3 rounded-lg hover:bg-muted transition-colors cursor-pointer">
                          <div className={`p-1.5 sm:p-2 rounded-lg ${action.color} flex-shrink-0`}>
                            <Icon className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-foreground text-xs sm:text-sm truncate">{action.title}</p>
                            <p className="text-xs text-muted-foreground hidden sm:block">{action.description}</p>
                          </div>
                          <ArrowRight className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-muted-foreground flex-shrink-0" />
                        </div>
                      </Link>
                    );
                  })}
                </CardContent>
              </Card>

              {/* ACCOUNT STATUS */}
              <Card>
                <CardHeader className="pb-3 sm:pb-4">
                  <CardTitle className="text-base sm:text-lg font-semibold">Account</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 sm:space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="min-w-0 flex-1">
                      <p className="text-xs sm:text-sm font-medium text-foreground">Current Plan</p>
                      <p className="text-xs text-muted-foreground">Free Plan</p>
                    </div>
                    <Badge className="text-xs">Active</Badge>
                  </div>
                  
                  <div className="flex items-center justify-between gap-2">
                    <div className="min-w-0 flex-1">
                      <p className="text-xs sm:text-sm font-medium text-foreground">Credits</p>
                      <p className="text-xs text-muted-foreground">
                        {creditsLoading ? "..." : creditsBalance?.toLocaleString() || 0} available
                      </p>
                    </div>
                    <Button variant="outline" size="sm" asChild className="text-xs px-2 sm:px-3">
                      <Link href="/dashboard/credits">
                        <Coins className="w-3 h-3 sm:w-4 sm:h-4 mr-1" />
                        <span className="hidden sm:inline">Buy</span>
                      </Link>
                    </Button>
                  </div>
                  
                </CardContent>
              </Card>
            </div>
          </div>

          {/* ONGOING PROJECTS */}
          {ongoingProjects.length > 0 && (
            <Card>
              <CardHeader className="pb-3 sm:pb-4">
                <CardTitle className="text-base sm:text-lg font-semibold">Active Projects</CardTitle>
                <CardDescription className="text-sm">Projects currently being processed</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                  {ongoingProjects.slice(0, 3).map((project) => (
                    <div key={project.id} className="p-3 sm:p-4 bg-muted rounded-lg">
                      <div className="flex items-center justify-between mb-2 sm:mb-3">
                        <h3 className="font-medium text-foreground text-sm sm:text-base truncate flex-1 min-w-0">
                          {project.name || `Project ${project.id.slice(0, 8)}`}
                        </h3>
                        <Badge className={`${getStatusColor(project.status)} text-white text-xs animate-pulse flex-shrink-0 ml-2`}>
                          {getStatusText(project.status)}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-1 text-xs sm:text-sm text-muted-foreground">
                          <Clock className="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" />
                          <span>In progress</span>
                        </div>
                        <Button variant="outline" size="sm" asChild className="text-xs px-2 sm:px-3">
                          <Link href={
                            project.status === 'processing'
                              ? `/dashboard/create/generation-overview?projectId=${project.id}`
                              : `/dashboard/create/music-clip?projectId=${project.id}`
                          }>
                            {project.status === 'processing' ? 'View' : 'Continue'}
                          </Link>
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}