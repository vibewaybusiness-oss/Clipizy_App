import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, Calendar, FileText, BarChart3 } from 'lucide-react';
import Link from 'next/link';

interface QuickAction {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  variant?: 'default' | 'outline';
}

const defaultActions: QuickAction[] = [
  {
    label: 'Create New Post',
    href: '/admin/posts/create',
    icon: Plus,
    variant: 'default'
  },
  {
    label: 'Content Calendar',
    href: '/admin/posts/calendar',
    icon: Calendar,
    variant: 'outline'
  },
  {
    label: 'Manage Posts',
    href: '/admin/posts',
    icon: FileText,
    variant: 'outline'
  }
];

interface QuickActionsProps {
  title?: string;
  actions?: QuickAction[];
}

export function QuickActions({
  title = 'Quick Actions',
  actions = defaultActions
}: QuickActionsProps) {
  return (
    <Card>
      <CardContent className="p-6">
        <h3 className="font-semibold mb-4">{title}</h3>
        <div className="space-y-3">
          {actions.map((action) => {
            const Icon = action.icon;
            return (
              <Button
                key={action.label}
                asChild
                variant={action.variant || 'outline'}
                className="w-full justify-start"
              >
                <Link href={action.href}>
                  <Icon className="w-4 h-4 mr-2" />
                  {action.label}
                </Link>
              </Button>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
