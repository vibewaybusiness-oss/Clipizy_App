"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  TrendingUp,
  TrendingDown,
  Eye,
  Play,
  Download,
  Share2,
  Calendar,
  BarChart3,
  PieChart,
  Activity
} from "lucide-react";

const analyticsData = {
  overview: [
    {
      title: "Total Views",
      value: "45.2K",
      change: "+12.5%",
      changeType: "positive" as const,
      icon: Eye,
    },
    {
      title: "Total Plays",
      value: "38.7K",
      change: "+8.3%",
      changeType: "positive" as const,
      icon: Play,
    },
    {
      title: "Downloads",
      value: "2.1K",
      change: "+15.2%",
      changeType: "positive" as const,
      icon: Download,
    },
    {
      title: "Shares",
      value: "892",
      change: "-2.1%",
      changeType: "negative" as const,
      icon: Share2,
    },
  ],
  topVideos: [
    {
      title: "Summer Vibes Mix",
      views: 12500,
      plays: 10800,
      engagement: 86.4,
      thumbnail: "/media/thumbnail_1.mp4",
    },
    {
      title: "Chill Beats",
      views: 8900,
      plays: 7600,
      engagement: 85.4,
      thumbnail: "/media/thumbnail_3.mp4",
    },
    {
      title: "Neon Nights",
      views: 7200,
      plays: 6100,
      engagement: 84.7,
      thumbnail: "/media/thumbnail_1.mp4",
    },
    {
      title: "Electronic Dreams",
      views: 5600,
      plays: 4800,
      engagement: 85.7,
      thumbnail: "/media/thumbnail_2.mp4",
    },
  ],
  engagement: [
    { label: "Views", value: 45200, color: "bg-blue-500" },
    { label: "Plays", value: 38700, color: "bg-green-500" },
    { label: "Downloads", value: 2100, color: "bg-purple-500" },
    { label: "Shares", value: 892, color: "bg-orange-500" },
  ],
  timeRange: [
    { label: "Last 7 days", value: "7d" },
    { label: "Last 30 days", value: "30d" },
    { label: "Last 90 days", value: "90d" },
    { label: "All time", value: "all" },
  ],
};

export default function AnalyticsPage() {
  return (
    <div className="p-8 space-y-6">
      {/* HEADER */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground mb-1">Analytics</h1>
          <p className="text-muted-foreground">
            Track your video performance and engagement metrics
          </p>
        </div>

        <div className="flex items-center space-x-2">
          {analyticsData.timeRange.map((range) => (
            <Button
              key={range.value}
              variant={range.value === "30d" ? "default" : "outline"}
              size="sm"
            >
              {range.label}
            </Button>
          ))}
        </div>
      </div>

      {/* OVERVIEW STATS */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {analyticsData.overview.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index} className="bg-card border border-border hover:border-border/60 transition-colors">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <Icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <div className="flex items-center space-x-1 text-xs">
                  {stat.changeType === "positive" ? (
                    <TrendingUp className="h-3 w-3 text-green-600" />
                  ) : (
                    <TrendingDown className="h-3 w-3 text-red-600" />
                  )}
                  <span className={stat.changeType === "positive" ? "text-green-600" : "text-red-600"}>
                    {stat.change}
                  </span>
                  <span className="text-muted-foreground">vs last period</span>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* CHARTS SECTION */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* ENGAGEMENT CHART */}
        <Card className="bg-card border border-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="w-5 h-5" />
              <span>Engagement Overview</span>
            </CardTitle>
            <CardDescription>
              Total engagement metrics for all your videos
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analyticsData.engagement.map((item, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">{item.label}</span>
                    <span className="text-muted-foreground">{item.value.toLocaleString()}</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${item.color}`}
                      style={{
                        width: `${(item.value / Math.max(...analyticsData.engagement.map(e => e.value))) * 100}%`
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* PERFORMANCE CHART */}
        <Card className="bg-card border border-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <PieChart className="w-5 h-5" />
              <span>Performance Trends</span>
            </CardTitle>
            <CardDescription>
              Weekly performance over the last 30 days
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center bg-muted/20 rounded-lg">
              <div className="text-center">
                <Activity className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
                <p className="text-muted-foreground">Chart visualization would go here</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Integration with charting library needed
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* TOP PERFORMING VIDEOS */}
      <Card className="bg-card border border-border">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5" />
            <span>Top Performing Videos</span>
          </CardTitle>
          <CardDescription>
            Your best performing videos ranked by total views
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {analyticsData.topVideos.map((video, index) => (
              <div key={index} className="flex items-center space-x-4 p-4 rounded-lg bg-muted/20 hover:bg-muted/30 transition-colors">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center text-sm font-semibold text-primary">
                    {index + 1}
                  </div>
                  <div className="relative w-16 h-10 bg-muted rounded overflow-hidden">
                    <video
                      src={video.thumbnail}
                      className="w-full h-full object-cover"
                      muted
                      onLoadedMetadata={(e) => {
                        e.currentTarget.currentTime = 5;
                      }}
                    />
                  </div>
                </div>

                <div className="flex-1 min-w-0">
                  <h4 className="font-semibold text-foreground truncate">
                    {video.title}
                  </h4>
                  <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                    <span>{video.views.toLocaleString()} views</span>
                    <span>{video.plays.toLocaleString()} plays</span>
                    <span>{video.engagement}% engagement</span>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Badge variant="secondary">
                    #{index + 1}
                  </Badge>
                  <Button size="sm" variant="outline">
                    View Details
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* INSIGHTS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="bg-card border border-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-green-600" />
              <span>Key Insights</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
              <p className="text-sm text-green-700 dark:text-green-400">
                <strong>Great performance!</strong> Your videos are getting 12.5% more views this month.
              </p>
            </div>
            <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
              <p className="text-sm text-blue-700 dark:text-blue-400">
                <strong>Peak hours:</strong> Your audience is most active between 7-9 PM.
              </p>
            </div>
            <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-lg">
              <p className="text-sm text-purple-700 dark:text-purple-400">
                <strong>Top genre:</strong> Electronic music videos perform 23% better than average.
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border border-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Calendar className="w-5 h-5" />
              <span>Recent Activity</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center space-x-3 text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-muted-foreground">Summer Vibes Mix reached 10K views</span>
              <span className="text-xs text-muted-foreground ml-auto">2h ago</span>
            </div>
            <div className="flex items-center space-x-3 text-sm">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="text-muted-foreground">New video "Chill Beats" published</span>
              <span className="text-xs text-muted-foreground ml-auto">1d ago</span>
            </div>
            <div className="flex items-center space-x-3 text-sm">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span className="text-muted-foreground">Electronic Dreams completed processing</span>
              <span className="text-xs text-muted-foreground ml-auto">2d ago</span>
            </div>
            <div className="flex items-center space-x-3 text-sm">
              <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
              <span className="text-muted-foreground">Neon Nights shared 15 times</span>
              <span className="text-xs text-muted-foreground ml-auto">3d ago</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
