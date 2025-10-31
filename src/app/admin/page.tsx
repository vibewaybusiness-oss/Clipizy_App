"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function AdminPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to overview page
    router.push('/admin/overview');
  }, [router]);

  return null;
}