import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ClipizyLogo } from "@/components/common/clipizy-logo";
import { Home, ArrowLeft, Search } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center max-w-md mx-auto px-4">
        <div className="mb-8">
          <ClipizyLogo className="w-16 h-16 mx-auto mb-4" />
          <h1 className="text-6xl font-bold gradient-text mb-2">404</h1>
          <h2 className="text-2xl font-semibold mb-4">Page Not Found</h2>
          <p className="text-muted-foreground mb-8">
            Sorry, we couldn't find the page you're looking for.
            It might have been moved, deleted, or doesn't exist.
          </p>
        </div>

        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild>
              <Link href="/">
                <Home className="w-4 h-4 mr-2" />
                Go Home
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/dashboard/create">
                <Search className="w-4 h-4 mr-2" />
                Create Video
              </Link>
            </Button>
          </div>

          <div className="pt-4">
            <Button variant="ghost" asChild>
              <Link href="/contact">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Contact Support
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
