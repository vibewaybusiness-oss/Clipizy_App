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
  const { email, source = 'website' } = await request.json();

  if (!email || !email.includes('@')) {
    throw new ValidationError('Valid email address is required');
  }

  // Read existing mailing list
  let mailingList: MailingList;
  try {
    const fileContent = await fs.readFile(MAILING_FILE_PATH, 'utf-8');
    mailingList = JSON.parse(fileContent);
  } catch (error) {
    // Create new mailing list if file doesn't exist
    mailingList = {
      subscribers: [],
      metadata: {
        created_at: new Date().toISOString(),
        last_updated: new Date().toISOString(),
        total_subscribers: 0,
        description: 'Product updates and feature announcements mailing list'
      }
    };
  }

  // Check if email already exists
  const existingSubscriber = mailingList.subscribers.find(
    sub => sub.email.toLowerCase() === email.toLowerCase()
  );

  if (existingSubscriber) {
    if (existingSubscriber.status === 'unsubscribed') {
      // Reactivate subscription
      existingSubscriber.status = 'active';
      existingSubscriber.subscribed_at = new Date().toISOString();
      existingSubscriber.source = source;
    } else {
      return NextResponse.json(
        { error: 'Email is already subscribed' },
        { status: 409 }
      );
    }
  } else {
    // Add new subscriber
    const newSubscriber: Subscriber = {
      email: email.toLowerCase(),
      subscribed_at: new Date().toISOString(),
      source,
      status: 'active'
    };
    mailingList.subscribers.push(newSubscriber);
  }

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
    message: 'Successfully subscribed to product updates',
    subscriber: {
      email: email.toLowerCase(),
      subscribed_at: new Date().toISOString()
    }
  });
});

export const GET = withErrorHandling(async () => {
  try {
    const fileContent = await fs.readFile(MAILING_FILE_PATH, 'utf-8');
    const mailingList: MailingList = JSON.parse(fileContent);

    return NextResponse.json({
      success: true,
      data: {
        total_subscribers: mailingList.metadata.total_subscribers,
        last_updated: mailingList.metadata.last_updated,
        subscribers: mailingList.subscribers.filter(sub => sub.status === 'active')
      }
    });
  } catch (error) {
    console.error('Error reading mailing list:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
});
