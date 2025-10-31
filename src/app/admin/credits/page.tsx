"use client";

import React from "react";
import AdminCreditsAdjustment from "@/app/admin/components/AdminCreditsAdjustment";

export default function CreditsPage() {
  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Credits Management</h1>
        <p className="text-muted-foreground">Manage user credits and transactions</p>
      </div>
      
      <AdminCreditsAdjustment />
    </div>
  );
}
