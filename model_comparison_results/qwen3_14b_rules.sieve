# Sieve Filter Rules
# Generated: 2025-11-06 20:25:56
# Filter: AI-Generated Email Filters
# Description: Automatically generated filters for 26 categories
#
# IMPORTANT: Review these rules before activating!

require ["fileinto", "envelope", "imap4flags"];

# Rule: Amazon-Orders
# Description: Order confirmation and status updates
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "bestellt,order,confirmed"
) {
  fileinto "Shopping/Amazon-Orders";
  stop;
}

# Rule: Amazon-Shipping
# Description: Shipping and delivery updates
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "versendet,shipped,lieferung"
) {
  fileinto "Shopping/Amazon-Shipping";
  stop;
}

# Rule: Amazon-Returns
# Description: Return processing and refunds
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "rücksendung,return,refund"
) {
  fileinto "Shopping/Amazon-Returns";
  stop;
}

# Rule: Amazon-Notifications
# Description: General notifications and alerts
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "benachrichtigung,alert,update"
) {
  fileinto "Shopping/Amazon-Notifications";
  stop;
}

# Rule: Amazon-Invoices
# Description: Invoice and billing details
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "rechnung,invoice,bill"
) {
  fileinto "Shopping/Amazon-Invoices";
  stop;
}

# Rule: Amazon-Receipts
# Description: Payment and receipt confirmations
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "beleg,receipt,confirmed"
) {
  fileinto "Shopping/Amazon-Receipts";
  stop;
}

# Rule: Amazon-Cancellations
# Description: Order cancellation notifications
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "storniert,cancelled,cancellation"
) {
  fileinto "Shopping/Amazon-Cancellations";
  stop;
}

# Rule: Amazon-Inventory
# Description: Inventory and stock updates
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "lager,inventory,stock"
) {
  fileinto "Shopping/Amazon-Inventory";
  stop;
}

# Rule: Amazon-Product-Updates
# Description: Product information and changes
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "produkt,update,change"
) {
  fileinto "Shopping/Amazon-Product-Updates";
  stop;
}

# Rule: Amazon-Discounts
# Description: Promotions and discounts
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "rabatt,discount,promotion"
) {
  fileinto "Shopping/Amazon-Discounts";
  stop;
}

# Rule: Amazon-Refunds
# Description: Refund processing and status
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "rückerstattung,refund,reimbursement"
) {
  fileinto "Shopping/Amazon-Refunds";
  stop;
}

# Rule: Amazon-Tracking
# Description: Order tracking and status updates
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "verfolgen,tracking,status"
) {
  fileinto "Shopping/Amazon-Tracking";
  stop;
}

# Rule: Amazon-Contact
# Description: Customer service and support
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "kontakt,contact,support"
) {
  fileinto "Shopping/Amazon-Contact";
  stop;
}

# Rule: Amazon-Payments
# Description: Payment processing and details
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "zahlung,payment,transaction"
) {
  fileinto "Shopping/Amazon-Payments";
  stop;
}

# Rule: Amazon-Deliveries
# Description: Delivery scheduling and updates
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "lieferung,delivery,scheduling"
) {
  fileinto "Shopping/Amazon-Deliveries";
  stop;
}

# Rule: Amazon-Returns-Processing
# Description: Return processing steps and instructions
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "rückgabe,processing,instructions"
) {
  fileinto "Shopping/Amazon-Returns-Processing";
  stop;
}

# Rule: Amazon-Orders-Changes
# Description: Order modification and changes
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "änderung,change,modification"
) {
  fileinto "Shopping/Amazon-Orders-Changes";
  stop;
}

# Rule: Amazon-Inventory-Updates
# Description: Inventory level and stock changes
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "lageränderung,inventory update,stock change"
) {
  fileinto "Shopping/Amazon-Inventory-Updates";
  stop;
}

# Rule: Amazon-Product-Reviews
# Description: Product reviews and feedback
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "bewertung,review,rating"
) {
  fileinto "Shopping/Amazon-Product-Reviews";
  stop;
}

# Rule: Amazon-Newsletter
# Description: Newsletter and marketing updates
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "newsletter,news,updates"
) {
  fileinto "Shopping/Amazon-Newsletter";
  stop;
}

# Rule: Amazon-Feedback
# Description: Customer feedback and suggestions
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "feedback,comment,suggestion"
) {
  fileinto "Shopping/Amazon-Feedback";
  stop;
}

# Rule: Amazon-Complaints
# Description: Complaints and issue resolution
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "beschwerde,complaint,issue"
) {
  fileinto "Shopping/Amazon-Complaints";
  stop;
}

# Rule: Amazon-Returns-Instructions
# Description: Return instructions and steps
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "rücksendeanweisung,instructions,steps"
) {
  fileinto "Shopping/Amazon-Returns-Instructions";
  stop;
}

# Rule: Amazon-Shopping-Cart
# Description: Shopping cart updates and changes
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "warenkorb,shopping cart,cart"
) {
  fileinto "Shopping/Amazon-Shopping-Cart";
  stop;
}

# Rule: Amazon-Checkout
# Description: Checkout and payment process
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "kasse,checkout,payment"
) {
  fileinto "Shopping/Amazon-Checkout";
  stop;
}

# Rule: Amazon-Order-Details
# Description: Order information and details
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "bestelldetails,order details,information"
) {
  fileinto "Shopping/Amazon-Order-Details";
  stop;
}

# End of AI-generated rules
# All other mail goes to Inbox (default)