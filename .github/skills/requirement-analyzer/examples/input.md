# User Story

As a registered shopper,
I want to save my payment card information,
so that I can checkout faster on future orders.

## Acceptance Criteria

- Given I am logged in, when I enter a valid card and save it, then the card is stored securely.
- Given I have no saved payment methods, when I attempt to checkout, then I am prompted to add a payment card.
- The saved card must expire after 3 years and require CVV entry for verification.

## Business Requirements

- Payment card data must be encrypted at rest.
- The system must support card expiration validation.
