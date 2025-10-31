"use client";

import React from 'react';

interface ContentCalendarProps {
  calendar: any;
  onPostClick: (post: any) => void;
  onGeneratePost: (post: any) => void;
  onEditPost: (post: any) => void;
}

export function ContentCalendar({
  calendar,
  onPostClick,
  onGeneratePost,
  onEditPost
}: ContentCalendarProps) {
  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold mb-4">Content Calendar</h2>
      <p className="text-muted-foreground">Content calendar component coming soon...</p>
    </div>
  );
}
