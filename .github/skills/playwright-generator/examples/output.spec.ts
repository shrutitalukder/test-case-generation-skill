import { test, expect } from '@playwright/test';

// Generated from TC-001
// Traceability: REQ-001

test('Save payment card successfully', async ({ request }) => {
  const response = await request.post('/payments', {
    data: {
      amount: 100.00,
      currency: 'USD'
    }
  });

  expect(response.status()).toBe(201);
  // TODO: Add assertions for response payload and business validation
});
