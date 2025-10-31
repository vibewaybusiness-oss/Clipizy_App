import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling, ValidationError } from '../../../middleware/error-handling';
import { promises as fs } from 'fs';
import path from 'path';

interface Subscriber {
  email: string;
  subscribed_at: string;
  source: string;
  status: 'active' | 'unsubscribed';
}

interface MailingList {
  subscribers: Subscriber[];
  metadata: {
    created_at: string;
    last_updated: string;
    total_subscribers: number;
    description: string;
  };
}

const MAILING_FILE_PATH = path.join(process.cwd(), 'storage', 'admin', 'mailing', 'mailingProductUpdates.json');

export const POST = withErrorHandling(async (request: NextRequest) => {
  const { email } = await request.json();

  if (!email || !email.includes('@')) {
    throw new ValidationError('Valid email address is required');
  }

  // Read existing mailing list
  let mailingList: MailingList;
  try {
    const fileContent = await fs.readFile(MAILING_FILE_PATH, 'utf-8');
    mailingList = JSON.parse(fileContent);
  } catch (error) {
    return NextResponse.json(
      { error: 'Mailing list not found' },
      { status: 404 }
    );
  }

  // Find and unsubscribe the subscriber
  const subscriber = mailingList.subscribers.find(
    sub => sub.email.toLowerCase() === email.toLowerCase()
  );

  if (!subscriber) {
    return NextResponse.json(
      { error: 'Email not found in mailing list' },
      { status: 404 }
    );
  }

  if (subscriber.status === 'unsubscribed') {
    return NextResponse.json(
      { error: 'Email is already unsubscribed' },
      { status: 409 }
    );
  }

  // Unsubscribe the user
  subscriber.status = 'unsubscribed';

  // Update metadata
  mailingList.metadata.last_updated = new Date().toISOString();
  mailingList.metadata.total_subscribers = mailingList.subscribers.filter(
    sub => sub.status === 'active'
  ).length;

  // Write updated mailing list
  await fs.writeFile(
    MAILING_FILE_PATH,
    JSON.stringify(mailingList, null, 2),
    'utf-8'
  );

  return NextResponse.json({
    success: true,
    message: 'Successfully unsubscribed from product updates',
    subscriber: {
      email: email.toLowerCase(),
      unsubscribed_at: new Date().toISOString()
    }
  });
});
