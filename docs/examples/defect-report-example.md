# Defect Report Examples: E-Commerce Checkout System

**Project:** ShopFlow E-Commerce Platform - Checkout Module Enhancement  
**Version:** 1.0  
**Created By:** QA Team  
**Date:** 2024-02-05

---

## Overview

This document contains realistic defect report examples demonstrating different severity levels, types, and statuses encountered during testing of the ShopFlow Checkout Module Enhancement project. These examples follow industry best practices for defect documentation.

**Related Documents:**
- Test Plan: test-plan-example.md
- Test Cases: test-case-suite-example.md
- Traceability Matrix: traceability-matrix-example.md

---

## Defect Index

| Defect ID | Title | Severity | Priority | Status | Date Found |
|-----------|-------|----------|----------|--------|------------|
| DEF-001 | Payment fails when using PayPal with special characters in address | Critical | P1 | Closed | 2024-02-01 |
| DEF-002 | Checkout page crashes on iOS Safari when adding promo code | Critical | P1 | Closed | 2024-02-03 |
| DEF-003 | Shipping cost doubles when switching between carriers | High | P1 | Closed | 2024-02-02 |
| DEF-004 | Guest checkout allows proceeding without accepting terms and conditions | High | P2 | Closed | 2024-02-04 |
| DEF-005 | Order confirmation email contains incorrect shipping address | High | P1 | Closed | 2024-02-01 |
| DEF-006 | Promo code "SAVE20" applies 25% discount instead of 20% | Medium | P2 | Closed | 2024-02-05 |
| DEF-007 | "Continue to Payment" button remains disabled after filling all fields | Medium | P2 | Closed | 2024-02-03 |
| DEF-008 | State dropdown displays states in random order instead of alphabetical | Low | P3 | Open | 2024-02-05 |
| DEF-009 | Shipping method icons not aligned properly on mobile devices | Low | P4 | Open | 2024-02-04 |
| DEF-010 | Tooltip text for CVV field has typo: "securty" instead of "security" | Low | P4 | Open | 2024-02-05 |

---

## Defect Reports

### DEF-001: Payment fails when using PayPal with special characters in address

**Defect Information:**

| Field | Value |
|-------|-------|
| **Defect ID** | DEF-001 |
| **Title** | Payment fails when using PayPal with special characters in address |
| **Reported By** | Emily Rodriguez, Senior Test Engineer |
| **Reported Date** | 2024-02-01 10:23 AM |
| **Assigned To** | Mark Thompson, Senior Developer |
| **Environment** | QA Environment - https://qa.shopflow.example.com |
| **Build Version** | 3.5.0-RC1 (Build #245) |
| **Browser/Device** | Chrome 120.0.6099.129 / Windows 11 |
| **Module** | Checkout - Payment Gateway Integration |
| **Severity** | Critical |
| **Priority** | P1 - Urgent |
| **Status** | Closed |
| **Resolution** | Fixed |
| **Fixed In Version** | 3.5.0-RC2 (Build #248) |
| **Verified By** | Emily Rodriguez |
| **Closed Date** | 2024-02-02 4:45 PM |

**Description:**

When a user attempts to complete checkout using PayPal Express Checkout with a shipping address containing special characters (specifically apostrophes in street names like "O'Brien Street"), the payment processing fails with a generic error message. The order is not created, and the user is unable to complete the purchase.

This is a critical defect as it prevents legitimate users from completing their purchases and directly impacts revenue.

**Preconditions:**
1. User has items in cart
2. User proceeds to checkout
3. Shipping address contains special characters (apostrophe)
4. User selects PayPal as payment method

**Steps to Reproduce:**

1. Navigate to https://qa.shopflow.example.com
2. Log in as test user or continue as guest with email: `test.paypal@example.com`
3. Add any product to cart (e.g., "Wireless Headphones" - $79.99)
4. Click "Proceed to Checkout"
5. Enter shipping address:
   - First Name: John
   - Last Name: O'Brien
   - Address: 123 O'Hare Avenue
   - City: Springfield
   - State: IL
   - ZIP: 62701
   - Phone: (555) 123-4567
6. Select "Standard Shipping"
7. On payment page, click "PayPal" button
8. On PayPal sandbox, log in with: `testbuyer@paypal.com` / `test1234`
9. Click "Pay Now" on PayPal
10. Observe the result after redirect back to ShopFlow

**Expected Result:**

- User is redirected back to ShopFlow order review page
- Payment method shows "PayPal (testbuyer@p***l.com)"
- User can click "Place Order" and complete the purchase
- Order confirmation page displays with order number
- Order is created in database with status "Completed"

**Actual Result:**

- User is redirected back to ShopFlow
- Error message displays: "Payment processing failed. Please try again or use a different payment method."
- User is returned to payment method selection page
- Order is NOT created in database
- PayPal transaction shows as "Authorized" but not captured in PayPal sandbox

**Impact:**

- **User Impact:** HIGH - Users with addresses containing apostrophes (common in Irish names like O'Brien, O'Connor, etc.) cannot complete PayPal checkout
- **Business Impact:** HIGH - Estimated 2-3% of user addresses contain apostrophes, directly affecting revenue
- **Frequency:** Occurs 100% of the time with addresses containing apostrophes
- **Workaround:** Users can use credit card payment instead, but may abandon purchase if they prefer PayPal

**Root Cause (Added by Developer):**

The PayPal API integration was not properly escaping special characters in the shipping address before sending to PayPal API. The apostrophe in the address was breaking the JSON payload structure, causing PayPal to reject the request.

**Fix Description:**

Implemented proper encoding/escaping of all address fields before sending to PayPal API. Added input sanitization middleware that handles special characters while preserving user input integrity.

**Attachments:**
- Screenshot: `DEF-001-error-screen.png` - Error message displayed to user
- Screenshot: `DEF-001-paypal-status.png` - PayPal sandbox showing orphaned authorization
- Browser Console Log: `DEF-001-console-log.txt` - JavaScript errors
- Network Log: `DEF-001-network-trace.har` - HTTP request/response showing malformed JSON
- Server Log: `DEF-001-server-log.txt` - Backend error stack trace

**Test Data:**
- Test Account: test.paypal@example.com
- Product: Wireless Headphones ($79.99)
- Shipping Address: 123 O'Hare Avenue, Springfield, IL 62701
- PayPal Sandbox Account: testbuyer@paypal.com

**Related Test Cases:**
- TC-CHK-002: Guest Checkout with PayPal Payment

**Verification Steps:**

1. Follow same steps to reproduce with apostrophe in address
2. Verify PayPal payment completes successfully
3. Verify order is created with correct shipping address (apostrophe preserved)
4. Test with other special characters: hyphens, accented characters, ampersands
5. Verify all special character variations work correctly

**Verification Result:** ✅ **PASSED** - Fixed and verified on 2024-02-02

**Notes:**
- Also tested with addresses containing accented characters (é, ñ, ü) - all working correctly
- Regression test added to automated suite to prevent recurrence

---

### DEF-002: Checkout page crashes on iOS Safari when adding promo code

**Defect Information:**

| Field | Value |
|-------|-------|
| **Defect ID** | DEF-002 |
| **Title** | Checkout page crashes on iOS Safari when adding promo code |
| **Reported By** | Lisa Patel, Test Engineer |
| **Reported Date** | 2024-02-03 2:15 PM |
| **Assigned To** | Rachel Kim, Frontend Developer |
| **Environment** | QA Environment - https://qa.shopflow.example.com |
| **Build Version** | 3.5.0-RC1 (Build #245) |
| **Browser/Device** | Safari on iPhone 13 / iOS 16.6 |
| **Module** | Checkout - Promotions |
| **Severity** | Critical |
| **Priority** | P1 - Urgent |
| **Status** | Closed |
| **Resolution** | Fixed |
| **Fixed In Version** | 3.5.0-RC2 (Build #247) |
| **Verified By** | Lisa Patel |
| **Closed Date** | 2024-02-04 11:30 AM |

**Description:**

On iOS Safari (tested on iPhone 13 and iPhone 14), when a user taps into the promotional code input field and enters a promo code, the entire checkout page becomes unresponsive and crashes/reloads. The issue appears to be related to keyboard input handling on iOS Safari specifically.

This is critical as it prevents iOS users (approximately 30% of mobile traffic) from using promotional codes and may cause cart abandonment.

**Preconditions:**
1. User is on iOS device with Safari browser
2. User has items in cart and is at payment step
3. Promotional code section is visible

**Steps to Reproduce:**

1. On iPhone 13 (iOS 16.6), open Safari
2. Navigate to https://qa.shopflow.example.com
3. Add product to cart and proceed to checkout
4. Complete shipping address and shipping method selection
5. On payment page, scroll to "Promotional Code" section
6. Tap on the promo code input field
7. iOS keyboard appears
8. Begin typing promo code "SAVE20"
9. Observe page behavior

**Expected Result:**

- Promo code input field accepts keyboard input
- User can type promo code without issues
- Page remains stable and responsive
- User can complete code entry and click "Apply"

**Actual Result:**

- After typing 2-3 characters, page becomes unresponsive
- Screen flickers briefly
- Page reloads automatically
- Cart contents are lost (if guest user)
- User is redirected to cart page or homepage

**Impact:**

- **User Impact:** CRITICAL - All iOS Safari users cannot use promotional codes
- **Business Impact:** HIGH - Affects ~30% of mobile users, promotional codes drive conversion
- **Frequency:** 100% reproducible on iOS Safari (versions 15, 16, 17 tested)
- **Workaround:** None - users cannot apply promo codes on iOS Safari

**Environment Details:**
- Devices Tested: iPhone 13 (iOS 16.6), iPhone 14 (iOS 17.2), iPad Air (iOS 16.6)
- Browser: Safari (default iOS browser)
- Network: WiFi and Cellular both reproduce issue
- Not reproducible on: Chrome iOS, Android devices, Desktop browsers

**Root Cause (Added by Developer):**

JavaScript event listener conflict with iOS Safari's keyboard handling. The promo code input field had an `onInput` event handler that was triggering a state update causing a re-render loop when combined with iOS Safari's autocorrect/autocomplete behavior. This created an infinite re-render cycle that caused the page crash.

**Fix Description:**

- Replaced `onInput` with `onBlur` event handler for promo code validation
- Added debouncing to input handling with 300ms delay
- Implemented proper state management to prevent re-render loops
- Added iOS Safari-specific handling for keyboard events
- Disabled autocorrect/autocomplete for promo code field on mobile

**Attachments:**
- Video: `DEF-002-ios-crash-recording.mp4` - Screen recording showing crash
- Screenshot: `DEF-002-before-crash.jpg` - Page state before crash
- Safari Console: `DEF-002-safari-console.txt` - JavaScript errors from iOS
- React DevTools: `DEF-002-react-profiler.json` - Component re-render profiling

**Test Data:**
- Product: Running Shoes ($89.99)
- Promo Code: SAVE20
- Device: iPhone 13, iOS 16.6

**Related Test Cases:**
- TC-CHK-004: Apply Valid Promotional Code at Checkout
- TC-CHK-010: Mobile Checkout Flow on iPhone

**Verification Steps:**

1. Test on iPhone 13 (iOS 16.6) with Safari
2. Complete checkout flow to payment page
3. Tap promo code input field
4. Enter "SAVE20" completely
5. Verify page remains stable
6. Tap "Apply" button
7. Verify promo code applies successfully
8. Complete checkout
9. Repeat test on iPhone 14 (iOS 17.2) and iPad Air

**Verification Result:** ✅ **PASSED** - Fixed and verified on 2024-02-04 across all iOS devices

**Notes:**
- Also tested with other promo codes of varying lengths - all working
- Added automated mobile testing for this scenario to CI pipeline
- Recommended iOS Safari testing be included in standard smoke test suite

---

### DEF-003: Shipping cost doubles when switching between carriers

**Defect Information:**

| Field | Value |
|-------|-------|
| **Defect ID** | DEF-003 |
| **Title** | Shipping cost doubles when switching between carriers |
| **Reported By** | David Kim, Test Engineer |
| **Reported Date** | 2024-02-02 9:45 AM |
| **Assigned To** | Alex Johnson, Backend Developer |
| **Environment** | QA Environment |
| **Build Version** | 3.5.0-RC1 (Build #245) |
| **Module** | Checkout - Shipping Calculation |
| **Severity** | High |
| **Priority** | P1 - Urgent |
| **Status** | Closed |
| **Resolution** | Fixed |
| **Fixed In Version** | 3.5.0-RC2 (Build #246) |
| **Verified By** | David Kim |
| **Closed Date** | 2024-02-03 3:20 PM |

**Description:**

When a user selects a shipping method, then goes back and selects a different shipping method, the shipping cost is added twice to the order total instead of replacing the previous shipping cost. Each subsequent change adds another shipping charge to the total.

**Steps to Reproduce:**

1. Add product to cart ($99.99)
2. Proceed to checkout, enter shipping address
3. On shipping method page, select "Standard Shipping" ($5.99)
4. Note order total: $105.98 (product + shipping)
5. Click "Back" button
6. Select "Express Shipping" ($12.99)
7. Note order total

**Expected Result:**
Order total should be $112.98 ($99.99 product + $12.99 shipping)

**Actual Result:**
Order total is $118.97 ($99.99 + $5.99 + $12.99) - both shipping charges included

**Impact:**
High - Overcharges customers, could result in cart abandonment and reputation damage

**Root Cause:**
Shipping cost was being appended to total instead of replaced when user changed selection. Cart total calculation logic was not clearing previous shipping charge.

**Attachments:**
- Screenshot: `DEF-003-doubled-shipping.png`
- Video: `DEF-003-reproduction.mp4`

**Verification Result:** ✅ **PASSED** - Shipping cost now properly replaces previous selection

---

### DEF-004: Guest checkout allows proceeding without accepting terms and conditions

**Defect Information:**

| Field | Value |
|-------|-------|
| **Defect ID** | DEF-004 |
| **Title** | Guest checkout allows proceeding without accepting terms and conditions |
| **Reported By** | Emily Rodriguez, Senior Test Engineer |
| **Reported Date** | 2024-02-04 11:05 AM |
| **Assigned To** | Sarah Chen, Frontend Developer |
| **Environment** | QA Environment |
| **Build Version** | 3.5.0-RC1 (Build #245) |
| **Module** | Checkout - Order Review |
| **Severity** | High |
| **Priority** | P2 - High |
| **Status** | Closed |
| **Resolution** | Fixed |
| **Fixed In Version** | 3.5.0-RC2 (Build #247) |
| **Verified By** | Emily Rodriguez |
| **Closed Date** | 2024-02-05 9:15 AM |

**Description:**

On the order review page, the "Place Order" button is enabled even when the "I agree to Terms and Conditions" checkbox is not checked. This allows users to submit orders without accepting terms, which is a legal compliance issue.

**Steps to Reproduce:**

1. Proceed through checkout as guest to order review page
2. Do NOT check the "I agree to Terms and Conditions" checkbox
3. Click "Place Order" button

**Expected Result:**
- Button should be disabled until checkbox is checked
- OR clicking button should show validation error: "Please accept Terms and Conditions to continue"

**Actual Result:**
Order processes successfully without accepting terms

**Impact:**
- Legal/Compliance risk - orders accepted without user agreement
- Severity: High (compliance issue)
- Could expose company to legal challenges

**Compliance Notes:**
- Required by company legal policy
- GDPR compliance requirement for EU customers
- Terms include liability limitations and dispute resolution

**Root Cause:**
Form validation was missing for terms acceptance checkbox. Client-side validation was implemented but not enforced before form submission.

**Fix Description:**
- Added validation to prevent form submission until terms checkbox is checked
- Disabled "Place Order" button until checkbox is checked
- Added visual indicator (button grayed out) when validation not met
- Added error message if user attempts to click disabled button

**Attachments:**
- Screenshot: `DEF-004-unchecked-terms.png`
- Screenshot: `DEF-004-order-placed.png` - Order placed without acceptance

**Related Requirements:**
- REQ-LEGAL-001: Users must accept terms before order placement
- REQ-GDPR-004: Explicit consent required for data processing

**Verification Result:** ✅ **PASSED** - Terms acceptance now properly enforced

---

### DEF-005: Order confirmation email contains incorrect shipping address

**Defect Information:**

| Field | Value |
|-------|-------|
| **Defect ID** | DEF-005 |
| **Title** | Order confirmation email contains incorrect shipping address |
| **Reported By** | Emily Rodriguez, Senior Test Engineer |
| **Reported Date** | 2024-02-01 3:30 PM |
| **Assigned To** | Chris Martinez, Backend Developer |
| **Environment** | QA Environment |
| **Build Version** | 3.5.0-RC1 (Build #245) |
| **Module** | Checkout - Email Notifications |
| **Severity** | High |
| **Priority** | P1 - Urgent |
| **Status** | Closed |
| **Resolution** | Fixed |
| **Fixed In Version** | 3.5.0-RC2 (Build #246) |

**Description:**

After completing an order, the confirmation email sent to the customer contains the billing address in place of the shipping address, even when separate billing and shipping addresses were provided during checkout.

**Steps to Reproduce:**

1. Complete checkout with:
   - Shipping Address: 123 Main St, Springfield, IL 62701
   - Billing Address: 456 Oak Ave, Chicago, IL 60601
2. Place order and check confirmation email
3. Review "Ship To" section in email

**Expected Result:**
Email shows shipping address: 123 Main St, Springfield, IL 62701

**Actual Result:**
Email shows billing address: 456 Oak Ave, Chicago, IL 60601

**Impact:**
- Customer confusion about delivery location
- Potential delivery to wrong address if customer provides billing address to shipping carrier
- Customer service inquiries increase

**Root Cause:**
Email template was using wrong variable for shipping address - referenced `billingAddress` instead of `shippingAddress` in template.

**Attachments:**
- Email HTML: `DEF-005-email-content.html`
- Screenshot: `DEF-005-incorrect-email.png`

**Verification Result:** ✅ **PASSED** - Email now displays correct shipping address

---

### DEF-006: Promo code "SAVE20" applies 25% discount instead of 20%

**Defect Information:**

| Field | Value |
|-------|-------|
| **Defect ID** | DEF-006 |
| **Title** | Promo code "SAVE20" applies 25% discount instead of 20% |
| **Reported By** | David Kim, Test Engineer |
| **Reported Date** | 2024-02-05 10:00 AM |
| **Assigned To** | Alex Johnson, Backend Developer |
| **Environment** | QA Environment |
| **Build Version** | 3.5.0-RC1 (Build #245) |
| **Module** | Checkout - Promotions |
| **Severity** | Medium |
| **Priority** | P2 - High |
| **Status** | Closed |
| **Resolution** | Fixed |
| **Fixed In Version** | 3.5.0-RC2 (Build #248) |

**Description:**

The promotional code "SAVE20" which should apply a 20% discount is incorrectly applying a 25% discount to the order subtotal.

**Steps to Reproduce:**

1. Add product to cart with price $100.00
2. Proceed to checkout
3. Apply promo code "SAVE20"
4. Check discount amount

**Expected Result:**
- Discount: $20.00 (20% of $100.00)
- Subtotal after discount: $80.00

**Actual Result:**
- Discount: $25.00 (25% of $100.00)
- Subtotal after discount: $75.00

**Impact:**
- Financial loss to company ($5 per $100 order)
- Code calculation logic error affects all "SAVE20" users
- Estimated financial impact: $2,000-5,000 if deployed to production

**Test Data:**
- Product subtotal tested: $100.00, $200.00, $50.00
- All show 25% discount instead of 20%

**Root Cause:**
Database configuration error - promo code "SAVE20" was configured with discount_percentage = 25 instead of 20 in the promotions table.

**Fix Description:**
Corrected database value from 25 to 20 for promo code SAVE20.

**Verification Result:** ✅ **PASSED** - Correct 20% discount now applies

---

### DEF-007: "Continue to Payment" button remains disabled after filling all fields

**Defect Information:**

| Field | Value |
|-------|-------|
| **Defect ID** | DEF-007 |
| **Title** | "Continue to Payment" button remains disabled after filling all fields |
| **Reported By** | Lisa Patel, Test Engineer |
| **Reported Date** | 2024-02-03 4:20 PM |
| **Assigned To** | Rachel Kim, Frontend Developer |
| **Environment** | QA Environment |
| **Build Version** | 3.5.0-RC1 (Build #245) |
| **Module** | Checkout - Shipping Form |
| **Severity** | Medium |
| **Priority** | P2 - High |
| **Status** | Closed |
| **Resolution** | Fixed |

**Description:**

On the shipping address form, after filling all required fields correctly, the "Continue to Payment" button sometimes remains disabled (grayed out). User must click into a field and out again to trigger button enablement.

**Steps to Reproduce:**

1. Navigate to shipping address page
2. Quickly fill all fields using browser autofill
3. Observe "Continue to Payment" button state

**Expected Result:**
Button becomes enabled immediately when all required fields are valid

**Actual Result:**
Button remains disabled until user clicks in/out of a field

**Impact:**
User friction, confusion about form completion

**Root Cause:**
Form validation was not triggered by autofill events, only by manual input

**Verification Result:** ✅ **PASSED** - Button now enables correctly with autofill

---

### DEF-008: State dropdown displays states in random order instead of alphabetical

**Defect Information:**

| Field | Value |
|-------|-------|
| **Defect ID** | DEF-008 |
| **Title** | State dropdown displays states in random order instead of alphabetical |
| **Reported By** | Emily Rodriguez, Senior Test Engineer |
| **Reported Date** | 2024-02-05 2:45 PM |
| **Assigned To** | Sarah Chen, Frontend Developer |
| **Environment** | QA Environment |
| **Build Version** | 3.5.0-RC1 (Build #245) |
| **Module** | Checkout - Shipping Address Form |
| **Severity** | Low |
| **Priority** | P3 - Medium |
| **Status** | Open |
| **Resolution** | In Progress |

**Description:**

In the shipping address form, the state dropdown list displays US states in random order rather than alphabetical order. This makes it difficult for users to find their state quickly.

**Steps to Reproduce:**

1. Navigate to shipping address page
2. Click on "State" dropdown
3. Observe state order

**Expected Result:**
States listed alphabetically: Alabama, Alaska, Arizona, Arkansas, California...

**Actual Result:**
States appear in random order: Texas, Oregon, Florida, New York...

**Impact:**
Minor usability issue - users must search through entire list to find state

**Priority Justification:**
Low priority as:
- Dropdown is searchable (users can type state name)
- Does not block functionality
- Cosmetic/usability improvement

**Status:** Open - Scheduled for Sprint 4

---

### DEF-009: Shipping method icons not aligned properly on mobile devices

**Defect Information:**

| Field | Value |
|-------|-------|
| **Defect ID** | DEF-009 |
| **Title** | Shipping method icons not aligned properly on mobile devices |
| **Reported By** | Lisa Patel, Test Engineer |
| **Reported Date** | 2024-02-04 1:30 PM |
| **Assigned To** | Rachel Kim, Frontend Developer |
| **Environment** | QA Environment |
| **Build Version** | 3.5.0-RC1 (Build #245) |
| **Module** | Checkout - Shipping Method Selection |
| **Severity** | Low |
| **Priority** | P4 - Low |
| **Status** | Open |
| **Resolution** | Backlog |

**Description:**

On mobile devices (tested on iPhone and Android), the carrier icons (FedEx, UPS, USPS) next to shipping method options are not vertically aligned with the text. Icons appear slightly below the text baseline.

**Steps to Reproduce:**

1. Access checkout on mobile device
2. Navigate to shipping method selection
3. Observe icon alignment

**Expected Result:**
Icons vertically centered with shipping method text

**Actual Result:**
Icons positioned slightly below text, creating uneven appearance

**Impact:**
Cosmetic only - does not affect functionality

**Attachments:**
- Screenshot: `DEF-009-mobile-alignment.png`

**Status:** Open - Low priority, scheduled for polish sprint

---

### DEF-010: Tooltip text for CVV field has typo: "securty" instead of "security"

**Defect Information:**

| Field | Value |
|-------|-------|
| **Defect ID** | DEF-010 |
| **Title** | Tooltip text for CVV field has typo: "securty" instead of "security" |
| **Reported By** | David Kim, Test Engineer |
| **Reported Date** | 2024-02-05 3:50 PM |
| **Assigned To** | Sarah Chen, Frontend Developer |
| **Environment** | QA Environment |
| **Build Version** | 3.5.0-RC1 (Build #245) |
| **Module** | Checkout - Payment Form |
| **Severity** | Low |
| **Priority** | P4 - Low |
| **Status** | Open |
| **Resolution** | Backlog |

**Description:**

The tooltip that appears when hovering over the CVV information icon contains a typo: "The CVV is your card securty code" should be "security code"

**Steps to Reproduce:**

1. Navigate to payment page
2. Hover over (i) icon next to CVV field
3. Read tooltip text

**Expected Result:**
"The CVV is your card security code located on the back of your card"

**Actual Result:**
"The CVV is your card securty code located on the back of your card"

**Impact:**
Cosmetic issue - typo in user-facing text, unprofessional appearance

**Status:** Open - Will be fixed in next content update

---

## Defect Statistics

### By Severity

| Severity | Count | Percentage |
|----------|-------|------------|
| Critical | 2 | 20% |
| High | 3 | 30% |
| Medium | 2 | 20% |
| Low | 3 | 30% |
| **Total** | **10** | **100%** |

### By Status

| Status | Count | Percentage |
|--------|-------|------------|
| Closed | 7 | 70% |
| Open | 3 | 30% |
| **Total** | **10** | **100%** |

### By Priority

| Priority | Count | Percentage |
|----------|-------|------------|
| P1 - Urgent | 4 | 40% |
| P2 - High | 3 | 30% |
| P3 - Medium | 1 | 10% |
| P4 - Low | 2 | 20% |
| **Total** | **10** | **100%** |

### By Module

| Module | Count |
|--------|-------|
| Checkout - Payment | 3 |
| Checkout - Shipping | 2 |
| Checkout - Promotions | 2 |
| Checkout - Forms | 2 |
| Checkout - Email | 1 |
| **Total** | **10** |

### Resolution Time

| Severity | Average Resolution Time |
|----------|------------------------|
| Critical | 18 hours |
| High | 24 hours |
| Medium | 48 hours |
| Low | Not yet resolved |

---

## Defect Report Template

Use this template when creating new defect reports:

**Defect ID:** [Auto-generated by Jira]  
**Title:** [Brief, descriptive title]  
**Reported By:** [Your name and role]  
**Reported Date:** [Date and time]  
**Environment:** [QA/Staging/Production]  
**Build Version:** [Version number]  
**Module:** [Feature area]  
**Severity:** [Critical/High/Medium/Low]  
**Priority:** [P1/P2/P3/P4]  
**Status:** [Open/In Progress/Fixed/Closed]

**Description:**
[Clear, concise description of the issue]

**Steps to Reproduce:**
1. [First step]
2. [Second step]
3. [And so on...]

**Expected Result:**
[What should happen]

**Actual Result:**
[What actually happens]

**Impact:**
[Business and user impact]

**Attachments:**
[Screenshots, logs, videos]

---

## Best Practices for Defect Reporting

### 1. Title Guidelines
- Be specific and descriptive
- Include location/module
- Use action words
- ✅ Good: "Payment fails when using PayPal with special characters in address"
- ❌ Bad: "PayPal doesn't work"

### 2. Severity Guidelines

**Critical:**
- System crash or data loss
- Security vulnerabilities
- Payment processing failures
- Complete feature breakdown
- Blocker for testing or release

**High:**
- Major feature malfunction
- Significant user impact
- Data integrity issues
- Incorrect calculations
- No reasonable workaround

**Medium:**
- Feature partially working
- Moderate user impact
- Workaround exists
- UI/UX issues affecting usability

**Low:**
- Cosmetic issues
- Minor UI problems
- Typos in non-critical text
- Enhancement suggestions
- Minimal user impact

### 3. What to Include
- **Environment details:** Browser, OS, device, build version
- **Steps to reproduce:** Clear, numbered, reproducible steps
- **Expected vs Actual:** What should happen vs what does happen
- **Attachments:** Screenshots, videos, logs to support the issue
- **Impact assessment:** Business and user impact analysis
- **Test data:** Specific data used to reproduce

### 4. What NOT to Include
- ❌ Vague descriptions: "It doesn't work"
- ❌ Multiple issues in one defect
- ❌ Solutions (unless specifically requested)
- ❌ Blame or emotional language
- ❌ Assumptions without evidence

---

**Document End**
