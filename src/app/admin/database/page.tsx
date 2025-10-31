"use client";

import React from "react";
import DatabaseViewer from "@/app/admin/components/DatabaseViewer";

export default function DatabasePage() {
  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Database Viewer</h1>
        <p className="text-muted-foreground">Browse and manage your database</p>
      </div>
      
      <DatabaseViewer />
    </div>
  );
}
