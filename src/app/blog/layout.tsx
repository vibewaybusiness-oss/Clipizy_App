import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Blog - clipizy',
  description: 'Discover the latest insights, tutorials, and tips for creating amazing AI-powered music videos.',
  keywords: 'AI, music video, blog, tutorials, tips, content creation, video generation',
};

export default function BlogLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="bg-background">
      {children}
    </div>
  );
}
