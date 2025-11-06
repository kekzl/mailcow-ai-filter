# Sieve Filter Rules
# Generated: 2025-11-06 21:13:50
# Filter: AI-Generated Email Filters
# Description: Automatically generated filters for 22 categories
#
# IMPORTANT: Review these rules before activating!

require ["fileinto", "envelope", "imap4flags"];

# Rule: Amazon-Orders
# Description: Amazon order confirmations and updates
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "bestellt,order,bestellung"
) {
  fileinto "Shopping/Amazon-Orders";
  stop;
}

# Rule: Amazon-Shipping
# Description: Amazon shipping notifications
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "versendet,geschickt,shipped"
) {
  fileinto "Shopping/Amazon-Shipping";
  stop;
}

# Rule: Amazon-Returns
# Description: Amazon return notifications
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "zurückgenommen,return"
) {
  fileinto "Shopping/Amazon-Returns";
  stop;
}

# Rule: Amazon-Invoices
# Description: Amazon invoice notifications
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "rechnung,receipt"
) {
  fileinto "Shopping/Amazon-Invoices";
  stop;
}

# Rule: Amazon-Wishlist
# Description: Amazon wishlist notifications
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "wunschliste,wishlist"
) {
  fileinto "Shopping/Amazon-Wishlist";
  stop;
}

# Rule: Amazon-Notifications
# Description: General Amazon notifications
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "benachrichtigung,notification"
) {
  fileinto "Shopping/Amazon-Notifications";
  stop;
}

# Rule: Amazon-Sales
# Description: Amazon sales notifications
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "verkauft,sale"
) {
  fileinto "Shopping/Amazon-Sales";
  stop;
}

# Rule: Amazon-Shipments
# Description: Amazon shipment notifications
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "lieferung,shipment"
) {
  fileinto "Shopping/Amazon-Shipments";
  stop;
}

# Rule: Amazon-Payments
# Description: Amazon payment notifications
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "zahlung,payment"
) {
  fileinto "Shopping/Amazon-Payments";
  stop;
}

# Rule: Amazon-Addresses
# Description: Amazon address notifications
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "adresse,address"
) {
  fileinto "Shopping/Amazon-Addresses";
  stop;
}

# Rule: Amazon-Cancellations
# Description: Amazon cancellation notifications
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "storniert,cancel"
) {
  fileinto "Shopping/Amazon-Cancellations";
  stop;
}

# Rule: Amazon-Refunds
# Description: Amazon refund notifications
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "ausgleich,rückerstattung"
) {
  fileinto "Shopping/Amazon-Refunds";
  stop;
}

# Rule: Amazon-Wallet
# Description: Amazon wallet notifications
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "portemonnaie,wallet"
) {
  fileinto "Shopping/Amazon-Wallet";
  stop;
}

# Rule: Amazon-Orders-FollowUp
# Description: Follow-up notifications for Amazon orders
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "nachfrage,follow-up"
) {
  fileinto "Shopping/Amazon-Orders-FollowUp";
  stop;
}

# Rule: Amazon-Shipping-Delays
# Description: Shipping delay notifications from Amazon
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "verzugsinfo,delay"
) {
  fileinto "Shopping/Amazon-Shipping-Delays";
  stop;
}

# Rule: Amazon-Inventory
# Description: Amazon inventory notifications
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "bestand,inventory"
) {
  fileinto "Shopping/Amazon-Inventory";
  stop;
}

# Rule: Amazon-Promo
# Description: Promotional notifications from Amazon
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "angebot,promo"
) {
  fileinto "Shopping/Amazon-Promo";
  stop;
}

# Rule: Amazon-Reviews
# Description: Review notifications from Amazon
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "bewertung,review"
) {
  fileinto "Shopping/Amazon-Reviews";
  stop;
}

# Rule: Amazon-Support
# Description: Support notifications from Amazon
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "support,help"
) {
  fileinto "Shopping/Amazon-Support";
  stop;
}

# Rule: Amazon-Newsletter
# Description: Newsletter notifications from Amazon
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "newsletter"
) {
  fileinto "Shopping/Amazon-Newsletter";
  stop;
}

# Rule: Amazon-Security
# Description: Security notifications from Amazon
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "sicherheit,security"
) {
  fileinto "Shopping/Amazon-Security";
  stop;
}

# Rule: Amazon-Financial
# Description: Financial notifications from Amazon
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "finanzial,financial"
) {
  fileinto "Shopping/Amazon-Financial";
  stop;
}

# End of AI-generated rules
# All other mail goes to Inbox (default)