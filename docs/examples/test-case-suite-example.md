# Test Case Suite: E-Commerce Checkout System

**Project:** ShopFlow E-Commerce Platform - Checkout Module Enhancement  
**Version:** 1.0  
**Created By:** Emily Rodriguez, Senior Test Engineer  
**Date:** 2024-01-20  
**Total Test Cases:** 12 (Sample Suite)

---

## Overview

This test case suite covers the enhanced checkout functionality for the ShopFlow E-Commerce Platform Release 3.5. The suite includes functional, integration, and negative test scenarios for the multi-step checkout process, guest checkout, and payment gateway integrations.

**Module Coverage:**
- Guest Checkout Flow
- Payment Processing
- Shipping Calculation
- Promotional Codes
- Order Confirmation

**Related Documents:**
- Test Plan: test-plan-example.md
- Requirements: SHOP-1250 (Jira Epic)
- User Stories: SHOP-1251 through SHOP-1289

---

## Test Case Index

| Test Case ID | Title | Priority | Type | Status |
|-------------|-------|----------|------|--------|
| TC-CHK-001 | Successful Guest Checkout with Credit Card | High | Functional | Ready |
| TC-CHK-002 | Guest Checkout with PayPal Payment | High | Functional | Ready |
| TC-CHK-003 | Registered User Checkout with Saved Payment | High | Functional | Ready |
| TC-CHK-004 | Apply Valid Promotional Code at Checkout | Medium | Functional | Ready |
| TC-CHK-005 | Multiple Items Checkout with Different Shipping | Medium | Integration | Ready |
| TC-CHK-006 | Checkout with Invalid Credit Card | High | Negative | Ready |
| TC-CHK-007 | Checkout with Expired Promotional Code | Medium | Negative | Ready |
| TC-CHK-008 | Edit Cart During Checkout Process | Medium | Functional | Ready |
| TC-CHK-009 | Checkout with Guest Email Already Registered | Medium | Functional | Ready |
| TC-CHK-010 | Mobile Checkout Flow on iPhone | High | Functional | Ready |
| TC-CHK-011 | Real-time Shipping Cost Calculation | High | Integration | Ready |
| TC-CHK-012 | Checkout Session Timeout Handling | Low | Functional | Ready |

---

## Test Cases

### TC-CHK-001: Successful Guest Checkout with Credit Card

**Test Case Information:**

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHK-001 |
| **Module** | Checkout - Guest Flow |
| **Priority** | High |
| **Type** | Functional, Smoke |
| **Estimated Execution Time** | 5 minutes |
| **Automation** | Yes |
| **Requirements Traceability** | REQ-CHK-001, REQ-CHK-015, REQ-PAY-001 |

**Test Objective:**  
Verify that a guest user can successfully complete a purchase using a credit card, proceeding through all checkout steps and receiving order confirmation.

**Preconditions:**
- ShopFlow application is accessible
- Test environment is in clean state
- At least one product is available in catalog
- Payment gateway (test mode) is operational
- Email service is configured for order confirmations

**Test Data:**
- Product: "Wireless Bluetooth Headphones" ($79.99)
- Guest Email: `guest.test001@example.com`
- Shipping Address: 123 Main St, Springfield, IL 62701, USA
- Test Credit Card: 4111 1111 1111 1111, Exp: 12/25, CVV: 123
- Cardholder Name: Test User

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to https://shopflow.example.com | Homepage displays successfully |
| 2 | Search for "Wireless Bluetooth Headphones" | Product search results display |
| 3 | Click on "Wireless Bluetooth Headphones" product | Product detail page opens with price $79.99 |
| 4 | Click "Add to Cart" button | Success message "Item added to cart" appears, Cart icon shows (1) |
| 5 | Click shopping cart icon in header | Cart page displays with product, quantity 1, subtotal $79.99 |
| 6 | Click "Proceed to Checkout" button | System redirects to checkout page, Step 1: Email/Login |
| 7 | Select "Continue as Guest" option | Guest email input field appears |
| 8 | Enter email: `guest.test001@example.com` | Email field accepts input |
| 9 | Click "Continue to Shipping" button | System validates email format and proceeds to Step 2: Shipping Address |
| 10 | Fill shipping form:<br>- First Name: Test<br>- Last Name: User<br>- Address: 123 Main St<br>- City: Springfield<br>- State: IL<br>- ZIP: 62701<br>- Phone: (555) 123-4567 | All fields accept input without errors |
| 11 | Click "Continue to Shipping Method" | System validates address and displays Step 3: Shipping Method with calculated rates |
| 12 | Verify shipping options display:<br>- Standard (5-7 days): $5.99<br>- Express (2-3 days): $12.99<br>- Overnight: $24.99 | All three shipping methods display with correct prices |
| 13 | Select "Standard Shipping ($5.99)" | Radio button selects, order total updates to $85.98 ($79.99 + $5.99) |
| 14 | Click "Continue to Payment" button | System proceeds to Step 4: Payment Information |
| 15 | Enter credit card details:<br>- Card Number: 4111 1111 1111 1111<br>- Expiry: 12/25<br>- CVV: 123<br>- Name: Test User | All payment fields accept input, card type icon shows Visa |
| 16 | Verify order summary shows:<br>- Subtotal: $79.99<br>- Shipping: $5.99<br>- Tax: $5.16<br>- Total: $91.14 | Order summary displays correct calculations |
| 17 | Click "Continue to Review Order" | System proceeds to Step 5: Order Review |
| 18 | Verify all order details display correctly:<br>- Product info<br>- Shipping address<br>- Shipping method<br>- Payment method (last 4 digits: 1111)<br>- Order total: $91.14 | All information displays accurately |
| 19 | Check "I agree to Terms and Conditions" | Checkbox becomes checked |
| 20 | Click "Place Order" button | Processing indicator appears |
| 21 | Wait for order confirmation | Order Confirmation page displays within 5 seconds |
| 22 | Verify confirmation page shows:<br>- Order number (format: ORD-XXXXXXXX)<br>- "Thank you for your order" message<br>- Order summary<br>- Estimated delivery date<br>- Email confirmation message | All elements present and correct |
| 23 | Check email inbox for `guest.test001@example.com` | Order confirmation email received within 2 minutes |
| 24 | Verify email contains:<br>- Order number<br>- Order details<br>- Shipping info<br>- Track order link | Email contains all required information |

**Expected Result:**  
Guest user successfully completes checkout with credit card payment. Order is confirmed with order number, confirmation page displays, and email confirmation is received.

**Actual Result:** _(To be filled during execution)_

**Status:** _(To be filled during execution)_  
☐ Pass  
☐ Fail  
☐ Blocked  
☐ Not Executed

**Defects Found:** _(To be filled during execution)_

**Notes:** _(To be filled during execution)_

**Executed By:** ________________  **Date:** ________________

---

### TC-CHK-002: Guest Checkout with PayPal Payment

**Test Case Information:**

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHK-002 |
| **Module** | Checkout - Payment Integration |
| **Priority** | High |
| **Type** | Integration, Functional |
| **Estimated Execution Time** | 6 minutes |
| **Automation** | Yes |
| **Requirements Traceability** | REQ-PAY-005, REQ-CHK-015 |

**Test Objective:**  
Verify that guest users can complete checkout using PayPal Express Checkout integration, including redirection to PayPal and return to complete order.

**Preconditions:**
- ShopFlow application accessible
- PayPal sandbox integration configured
- Test PayPal account available (testbuyer@paypal.com / password: test1234)
- Product available in catalog

**Test Data:**
- Product: "Smart Watch Pro" ($299.99)
- Guest Email: `guest.paypal@example.com`
- PayPal Test Account: testbuyer@paypal.com
- Shipping Address: (Auto-filled from PayPal)

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Add "Smart Watch Pro" to cart | Product added, cart shows 1 item, subtotal $299.99 |
| 2 | Navigate to checkout as guest with email `guest.paypal@example.com` | Checkout flow starts at shipping address step |
| 3 | Enter shipping address and select Standard Shipping | Shipping address validated, order total: $305.98 (product + shipping) |
| 4 | On payment page, click "PayPal" button | Browser redirects to PayPal sandbox (paypal.com/checkoutnow) |
| 5 | On PayPal login page, enter:<br>- Email: testbuyer@paypal.com<br>- Password: test1234 | PayPal login successful, user account page displays |
| 6 | Verify order summary on PayPal shows:<br>- Merchant: ShopFlow<br>- Amount: $305.98 | PayPal displays correct merchant and amount |
| 7 | Click "Pay Now" button on PayPal | PayPal processes payment and redirects back to ShopFlow |
| 8 | Verify return to ShopFlow order review page | Order review page displays with PayPal payment method selected |
| 9 | Verify payment method shows "PayPal (testbuyer@p***l.com)" | PayPal email displayed in masked format |
| 10 | Click "Place Order" button | Order processes successfully |
| 11 | Verify order confirmation displays with order number | Confirmation page shows successful PayPal payment |

**Expected Result:**  
Guest successfully completes checkout using PayPal. Payment processes through PayPal, user returns to ShopFlow, and order is confirmed.

**Status:** ☐ Pass ☐ Fail ☐ Blocked ☐ Not Executed

---

### TC-CHK-003: Registered User Checkout with Saved Payment

**Test Case Information:**

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHK-003 |
| **Module** | Checkout - Registered User |
| **Priority** | High |
| **Type** | Functional, Regression |
| **Estimated Execution Time** | 4 minutes |
| **Automation** | Yes |
| **Requirements Traceability** | REQ-CHK-020, REQ-PAY-010 |

**Test Objective:**  
Verify that registered users can use saved payment methods and shipping addresses for expedited checkout.

**Preconditions:**
- User account exists: testuser001@example.com / password: TestPass123!
- User has saved payment method (card ending in 4242)
- User has saved shipping address

**Test Data:**
- User: testuser001@example.com / TestPass123!
- Product: "Running Shoes" ($89.99)

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Login with testuser001@example.com | User successfully logged in, dashboard displays |
| 2 | Add "Running Shoes" to cart and proceed to checkout | Checkout flow starts, user recognized as registered |
| 3 | On shipping page, verify saved addresses display | Previous addresses appear as selectable options |
| 4 | Select saved address "123 Main St, Springfield, IL" | Address auto-fills all fields correctly |
| 5 | Select Standard Shipping and continue | Shipping method selected, proceed to payment |
| 6 | On payment page, verify saved payment methods display | "Visa ending in 4242" appears as option |
| 7 | Select saved card "Visa ending in 4242" | Payment method selected, no need to re-enter card details |
| 8 | Enter CVV: 123 (security requirement) | CVV field accepts input |
| 9 | Review order and place order | Order completes successfully with saved information |
| 10 | Verify order history shows new order | Order appears in user's account order history |

**Expected Result:**  
Registered user completes checkout using saved payment method and address. Process is faster than guest checkout.

**Status:** ☐ Pass ☐ Fail ☐ Blocked ☐ Not Executed

---

### TC-CHK-004: Apply Valid Promotional Code at Checkout

**Test Case Information:**

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHK-004 |
| **Module** | Checkout - Promotions |
| **Priority** | Medium |
| **Type** | Functional |
| **Estimated Execution Time** | 4 minutes |
| **Automation** | Yes |
| **Requirements Traceability** | REQ-PROMO-001, REQ-PROMO-002 |

**Test Objective:**  
Verify that users can apply valid promotional codes at checkout and receive correct discounts.

**Preconditions:**
- Active promotional code exists: "SAVE20" (20% off entire order)
- Promo code valid for orders over $50
- Product in cart exceeds minimum

**Test Data:**
- Product: "Laptop Backpack" ($59.99)
- Promo Code: SAVE20 (20% discount)

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Add "Laptop Backpack" ($59.99) to cart | Cart subtotal: $59.99 |
| 2 | Proceed to checkout as guest | Checkout flow starts |
| 3 | Complete shipping information | Shipping address entered, standard shipping $5.99 selected |
| 4 | On payment page, locate "Promotional Code" section | Promo code input field and "Apply" button visible |
| 5 | Enter promo code: "SAVE20" | Code entered in input field |
| 6 | Click "Apply" button | Success message: "Promotional code SAVE20 applied" displays |
| 7 | Verify order summary updates:<br>- Subtotal: $59.99<br>- Discount (20%): -$12.00<br>- Shipping: $5.99<br>- Tax: $3.24<br>- Total: $57.22 | All calculations correct, discount properly applied |
| 8 | Verify promo code badge displays "SAVE20" with remove (X) option | Promo badge appears with removal option |
| 9 | Complete payment and place order | Order processes with discounted amount |
| 10 | Verify confirmation shows discount applied | Order confirmation reflects $12.00 savings |

**Expected Result:**  
Promotional code applies successfully, 20% discount calculated correctly, and order completes with reduced total.

**Status:** ☐ Pass ☐ Fail ☐ Blocked ☐ Not Executed

---

### TC-CHK-005: Multiple Items Checkout with Different Shipping

**Test Case Information:**

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHK-005 |
| **Module** | Checkout - Cart Management |
| **Priority** | Medium |
| **Type** | Integration, Functional |
| **Estimated Execution Time** | 6 minutes |
| **Automation** | Partial |
| **Requirements Traceability** | REQ-CART-005, REQ-SHIP-003 |

**Test Objective:**  
Verify checkout handles multiple items with different quantities and calculates combined shipping correctly.

**Preconditions:**
- Multiple products available
- Shipping calculation service operational

**Test Data:**
- Product 1: "Coffee Maker" ($49.99) x 1
- Product 2: "Coffee Beans" ($14.99) x 3
- Product 3: "Travel Mug" ($19.99) x 2

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Add Coffee Maker (qty: 1) to cart | Cart shows 1 item, subtotal $49.99 |
| 2 | Add Coffee Beans (qty: 3) to cart | Cart shows 4 items, subtotal $94.96 |
| 3 | Add Travel Mug (qty: 2) to cart | Cart shows 6 items, subtotal $134.94 |
| 4 | View cart and verify line items:<br>- Coffee Maker: $49.99<br>- Coffee Beans: $44.97 (3 x $14.99)<br>- Travel Mug: $39.98 (2 x $19.99) | All items listed with correct quantities and prices |
| 5 | Click "Proceed to Checkout" | Checkout starts with correct cart total |
| 6 | Enter shipping address | Address accepted |
| 7 | View shipping options and verify calculated rates based on total weight/value | Standard: $7.99, Express: $15.99, Overnight: $29.99 |
| 8 | Select Express Shipping ($15.99) | Shipping method selected, total updates |
| 9 | Verify order summary:<br>- Subtotal: $134.94<br>- Shipping: $15.99<br>- Tax: $9.06<br>- Total: $159.99 | Calculations correct for multiple items |
| 10 | Complete payment and place order | Order confirms with all 6 items |

**Expected Result:**  
Multiple items checkout successfully with correct pricing, quantity calculations, and combined shipping cost.

**Status:** ☐ Pass ☐ Fail ☐ Blocked ☐ Not Executed

---

### TC-CHK-006: Checkout with Invalid Credit Card

**Test Case Information:**

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHK-006 |
| **Module** | Checkout - Payment Validation |
| **Priority** | High |
| **Type** | Negative Testing |
| **Estimated Execution Time** | 4 minutes |
| **Automation** | Yes |
| **Requirements Traceability** | REQ-PAY-008, REQ-VAL-002 |

**Test Objective:**  
Verify that system properly validates credit card information and displays appropriate error messages for invalid card details.

**Preconditions:**
- Checkout process accessible
- Product in cart

**Test Data:**
- Invalid Card Numbers:
  - Invalid Luhn check: 4111 1111 1111 1112
  - Expired card: 4111 1111 1111 1111, Exp: 01/20
  - Invalid CVV: 12 (too short)

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Add product to cart and proceed to payment step | Payment page displays |
| 2 | Enter invalid card number: 4111 1111 1111 1112 | Card number field accepts input |
| 3 | Enter expiry: 12/25, CVV: 123, Name: Test User | Fields accept input |
| 4 | Click "Continue to Review" | System validates card number |
| 5 | Verify error message displays | Error: "Invalid card number. Please check and try again." |
| 6 | Correct card to: 4111 1111 1111 1111 | Card number updated |
| 7 | Change expiry to: 01/20 (expired) | Expired date entered |
| 8 | Click "Continue to Review" | System validates expiry date |
| 9 | Verify error message displays | Error: "Card has expired. Please use a valid card." |
| 10 | Correct expiry to: 12/25 | Expiry updated |
| 11 | Change CVV to: 12 (only 2 digits) | CVV updated |
| 12 | Click "Continue to Review" | System validates CVV |
| 13 | Verify error message displays | Error: "CVV must be 3 digits." |
| 14 | Correct CVV to: 123 | All fields now valid |
| 15 | Click "Continue to Review" | Successfully proceeds to order review |

**Expected Result:**  
System validates all payment fields and displays specific, helpful error messages for each type of invalid input. User cannot proceed until all validation passes.

**Status:** ☐ Pass ☐ Fail ☐ Blocked ☐ Not Executed

---

### TC-CHK-007: Checkout with Expired Promotional Code

**Test Case Information:**

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHK-007 |
| **Module** | Checkout - Promotions |
| **Priority** | Medium |
| **Type** | Negative Testing |
| **Estimated Execution Time** | 3 minutes |
| **Automation** | Yes |
| **Requirements Traceability** | REQ-PROMO-004 |

**Test Objective:**  
Verify that system rejects expired promotional codes with appropriate error message.

**Preconditions:**
- Expired promo code exists: "EXPIRED10" (expired on 2023-12-31)
- Product in cart

**Test Data:**
- Product: "Keyboard" ($79.99)
- Expired Promo Code: EXPIRED10

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Add product to cart, proceed to payment | Payment page displays |
| 2 | In promo code field, enter: "EXPIRED10" | Code entered |
| 3 | Click "Apply" button | System validates promo code |
| 4 | Verify error message | Error message: "This promotional code has expired." displays in red |
| 5 | Verify promo code is not applied | Order total remains unchanged, no discount applied |
| 6 | Verify no promo badge appears | No promotional code badge displayed |
| 7 | Attempt to proceed with checkout | Can proceed without promo code |

**Expected Result:**  
Expired promotional code is rejected with clear error message. Order total remains unchanged, and checkout can proceed without discount.

**Status:** ☐ Pass ☐ Fail ☐ Blocked ☐ Not Executed

---

### TC-CHK-008: Edit Cart During Checkout Process

**Test Case Information:**

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHK-008 |
| **Module** | Checkout - Cart Management |
| **Priority** | Medium |
| **Type** | Functional |
| **Estimated Execution Time** | 5 minutes |
| **Automation** | No |
| **Requirements Traceability** | REQ-CART-008, REQ-CHK-012 |

**Test Objective:**  
Verify that users can edit cart contents during checkout and pricing/shipping updates correctly.

**Preconditions:**
- Multiple products in cart
- Checkout process started

**Test Data:**
- Initial Product: "Desk Lamp" ($45.99) x 1
- Add During Checkout: "Light Bulbs" ($9.99)

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Add "Desk Lamp" to cart, proceed to checkout | Checkout starts with 1 item, subtotal $45.99 |
| 2 | Complete shipping address form | Address entered, proceed to shipping method |
| 3 | On shipping method page, note displayed total | Standard shipping $5.99, total $51.98 |
| 4 | Click "Edit Cart" link in order summary | System returns to shopping cart page |
| 5 | In cart, add "Light Bulbs" ($9.99) x 1 | Cart updates to 2 items, new subtotal $55.98 |
| 6 | Click "Proceed to Checkout" | System returns to checkout |
| 7 | Verify shipping address is preserved | Previously entered address still populated |
| 8 | Proceed to shipping method page | Shipping options display |
| 9 | Verify shipping cost recalculated | Standard shipping now $6.99 (increased due to added item) |
| 10 | Verify order summary reflects cart changes:<br>- 2 items<br>- Subtotal: $55.98<br>- Shipping: $6.99 | Order summary correctly updated |
| 11 | Complete checkout | Order places successfully with both items |

**Expected Result:**  
User can edit cart during checkout. System preserves entered information, recalculates shipping and totals, and allows checkout completion with updated cart.

**Status:** ☐ Pass ☐ Fail ☐ Blocked ☐ Not Executed

---

### TC-CHK-009: Checkout with Guest Email Already Registered

**Test Case Information:**

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHK-009 |
| **Module** | Checkout - User Management |
| **Priority** | Medium |
| **Type** | Functional |
| **Estimated Execution Time** | 4 minutes |
| **Automation** | Yes |
| **Requirements Traceability** | REQ-CHK-016, REQ-USER-005 |

**Test Objective:**  
Verify that when a guest attempts checkout with an email already registered, system prompts login or option to continue as guest.

**Preconditions:**
- Registered user exists: existinguser@example.com / TestPass123!
- Product in cart

**Test Data:**
- Existing Email: existinguser@example.com
- Guest attempting checkout

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Add product to cart as guest | Cart contains item |
| 2 | Proceed to checkout | Checkout email/login page displays |
| 3 | Select "Continue as Guest" | Email input field appears |
| 4 | Enter email: existinguser@example.com | Email entered |
| 5 | Click "Continue to Shipping" | System checks if email exists |
| 6 | Verify notification displays | Message: "This email is already registered. Please log in or use a different email." |
| 7 | Verify "Log In" button appears | Button displays to proceed with login |
| 8 | Verify "Use Different Email" button appears | Button displays to change email |
| 9 | Click "Log In" button | Login form displays |
| 10 | Enter password: TestPass123! | Password accepted |
| 11 | Submit login | User logs in, checkout continues as registered user |
| 12 | Verify checkout pre-fills saved information | Shipping address and payment methods auto-populate |

**Expected Result:**  
System detects existing registered email, prompts user to login, and seamlessly continues checkout with account benefits after authentication.

**Status:** ☐ Pass ☐ Fail ☐ Blocked ☐ Not Executed

---

### TC-CHK-010: Mobile Checkout Flow on iPhone

**Test Case Information:**

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHK-010 |
| **Module** | Checkout - Mobile Responsiveness |
| **Priority** | High |
| **Type** | Functional, Mobile |
| **Estimated Execution Time** | 6 minutes |
| **Automation** | No (Manual mobile testing) |
| **Requirements Traceability** | REQ-MOB-001, REQ-CHK-025 |

**Test Objective:**  
Verify that entire checkout flow works correctly on mobile devices (iPhone) with touch interactions and responsive design.

**Preconditions:**
- iPhone 13 or newer with iOS 16+
- Safari browser
- Network connectivity

**Test Data:**
- Device: iPhone 13, iOS 16.5
- Browser: Safari
- Product: "Phone Case" ($24.99)

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open Safari on iPhone, navigate to shopflow.example.com | Mobile site loads, responsive layout displays |
| 2 | Search and select "Phone Case" | Product page displays in mobile view |
| 3 | Tap "Add to Cart" button | Cart icon updates, success toast appears |
| 4 | Tap cart icon | Cart drawer slides in from right or full cart page displays |
| 5 | Tap "Checkout" button | Checkout page loads in mobile layout |
| 6 | Enter guest email using iOS keyboard | Email input works with iOS autocomplete |
| 7 | Fill shipping form using touch keyboard | All form fields accessible and usable |
| 8 | Verify address fields stack vertically | Mobile layout: fields full-width, single column |
| 9 | Use iOS autofill for shipping address | Autofill populates fields correctly |
| 10 | Select shipping method by tapping radio button | Selection works with touch, price updates |
| 11 | Scroll to view order summary | Sticky "Continue" button remains accessible |
| 12 | Tap "Continue to Payment" | Payment page loads |
| 13 | Enter credit card using iOS keyboard | Card number input auto-formats with spaces |
| 14 | Verify expiry date picker works on mobile | Date picker opens iOS native selector |
| 15 | Review order on mobile layout | All order details readable without horizontal scroll |
| 16 | Tap "Place Order" button | Processing animation displays |
| 17 | Verify confirmation page mobile layout | Confirmation displays properly, all text readable |
| 18 | Verify email link opens in native Mail app | Order email link triggers Mail app |

**Expected Result:**  
Complete checkout flow works seamlessly on iPhone. All interactive elements respond to touch, layout is mobile-optimized, iOS native features integrate properly, and no horizontal scrolling required.

**Status:** ☐ Pass ☐ Fail ☐ Blocked ☐ Not Executed

---

### TC-CHK-011: Real-time Shipping Cost Calculation

**Test Case Information:**

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHK-011 |
| **Module** | Checkout - Shipping Integration |
| **Priority** | High |
| **Type** | Integration |
| **Estimated Execution Time** | 5 minutes |
| **Automation** | Yes |
| **Requirements Traceability** | REQ-SHIP-001, REQ-SHIP-002 |

**Test Objective:**  
Verify that shipping costs are calculated in real-time based on carrier APIs, destination, and package weight.

**Preconditions:**
- Shipping carrier APIs accessible (FedEx, UPS, USPS test APIs)
- Product weights configured in system
- Various shipping destinations

**Test Data:**
- Product: "Laptop Computer" (5 lbs)
- Destination 1: Local (same state): Springfield, IL 62701
- Destination 2: Cross-country: Los Angeles, CA 90001
- Destination 3: Hawaii: Honolulu, HI 96801

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Add "Laptop Computer" to cart | Cart shows item with weight: 5 lbs |
| 2 | Proceed to checkout, enter local address (Springfield, IL 62701) | Address accepted |
| 3 | On shipping method page, verify loading indicator appears | "Calculating shipping rates..." displays |
| 4 | Verify shipping options appear within 3 seconds | Three options display with carrier names and delivery times |
| 5 | Verify local rates (approximate):<br>- Standard (USPS): $8-12<br>- Express (FedEx): $20-30<br>- Overnight (UPS): $40-60 | Rates displayed are within expected ranges for local delivery |
| 6 | Click "Back" to change address | Returns to address form |
| 7 | Change address to cross-country (Los Angeles, CA 90001) | Address updated |
| 8 | Verify shipping rates recalculate | Loading indicator appears, new rates display |
| 9 | Verify cross-country rates are higher than local | Standard: $15-25, Express: $35-50, Overnight: $75-100 |
| 10 | Change address to Hawaii (Honolulu, HI 96801) | Address updated |
| 11 | Verify shipping calculation displays | Rates appear (may have longer calculation time) |
| 12 | Verify Hawaii rates reflect special handling:<br>- Standard: $25-40<br>- Express: $60-80<br>- Note about extended delivery | Hawaii shipping costs higher, delivery times longer noted |
| 13 | Verify each option shows carrier name and estimated delivery | Format: "FedEx 2-Day - Estimated: Jan 25" |

**Expected Result:**  
Shipping costs calculate in real-time based on destination and package weight. Different locations show appropriate rate differences. Carrier names and delivery estimates display correctly.

**Status:** ☐ Pass ☐ Fail ☐ Blocked ☐ Not Executed

---

### TC-CHK-012: Checkout Session Timeout Handling

**Test Case Information:**

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHK-012 |
| **Module** | Checkout - Session Management |
| **Priority** | Low |
| **Type** | Functional |
| **Estimated Execution Time** | 20 minutes (includes wait time) |
| **Automation** | Partial |
| **Requirements Traceability** | REQ-SEC-005, REQ-CHK-030 |

**Test Objective:**  
Verify that checkout session expires after configured timeout period and user is properly notified with option to recover.

**Preconditions:**
- Session timeout configured to 15 minutes
- Product in cart

**Test Data:**
- Timeout Period: 15 minutes
- Warning Period: 13 minutes (2 minutes before timeout)

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Add product to cart, start checkout | Checkout session begins |
| 2 | Enter shipping address | Address saved in session |
| 3 | Wait idle for 13 minutes (no interaction) | System tracks inactivity |
| 4 | After 13 minutes, verify warning appears | Warning modal: "Your session will expire in 2 minutes. Click Continue to keep shopping." |
| 5 | Do not interact with warning | Timer counts down |
| 6 | Wait additional 2 minutes (total 15 minutes idle) | Session expires |
| 7 | Verify timeout notification displays | Message: "Your session has expired for security. Please restart checkout." |
| 8 | Verify "Restart Checkout" button appears | Button is visible and clickable |
| 9 | Click "Restart Checkout" | Returns to cart page |
| 10 | Verify cart contents preserved | Product still in cart (cart separate from checkout session) |
| 11 | Restart checkout | Checkout starts fresh |
| 12 | Verify previously entered data cleared | Shipping address and payment info not saved (security) |
| 13 | (Alternative) Re-run test and click "Continue" when warning appears at 13 min | Session extends, no timeout occurs |
| 14 | Verify checkout can proceed normally after extending | Can complete checkout after session extension |

**Expected Result:**  
Checkout session times out after 15 minutes of inactivity. User receives warning at 13 minutes with option to extend. After timeout, cart contents preserved but checkout data cleared for security. User can restart checkout smoothly.

**Status:** ☐ Pass ☐ Fail ☐ Blocked ☐ Not Executed

---

## Test Execution Summary

**Suite Statistics:**
- Total Test Cases: 12
- Automated: 9 (75%)
- Manual: 3 (25%)

**Execution Results:** _(To be updated during test execution)_

| Status | Count | Percentage |
|--------|-------|------------|
| Pass | - | - |
| Fail | - | - |
| Blocked | - | - |
| Not Executed | - | - |

**Defects Summary:** _(To be updated during test execution)_

| Severity | Count |
|----------|-------|
| Critical | - |
| High | - |
| Medium | - |
| Low | - |

---

## Notes

**Test Environment:**
- URL: https://shopflow-qa.example.com
- Build Version: 3.5.0-RC1
- Browser: Chrome 120.x, Firefox 121.x, Safari 17.x
- Mobile: iOS 16+, Android 12+

**Test Data Location:**
- Test accounts: `/test-data/user-accounts.csv`
- Test products: `/test-data/products.json`
- Promo codes: `/test-data/promo-codes.xlsx`

**Related Documents:**
- Test Plan: `test-plan-example.md`
- Defect Reports: `defect-report-example.md`
- Traceability Matrix: `traceability-matrix-example.md`

---

**Document End**
