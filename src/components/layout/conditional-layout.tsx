"use client";

import { usePathname } from "next/navigation";
import { Navigation } from "@/components/layout/navigation";
import { Footer } from "@/components/layout/footer";

export function ConditionalLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isAuthPage = pathname.startsWith("/auth");
  const isDashboardPage = pathname.startsWith("/dashboard");
  const isAdminPage = pathname.startsWith("/admin");

  if (isAuthPage || isDashboardPage || isAdminPage) {
    return <>{children}</>;
  }

  return (
    <>
      <Navigation />
      <main>
        {children}
      </main>
      <Footer />
    </>
  );
}
