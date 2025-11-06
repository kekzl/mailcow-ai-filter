# Sieve Filter Rules
# Generated: 2025-11-06 21:05:05
# Filter: AI-Generated Email Filters
# Description: Automatically generated filters for 31 categories
#
# IMPORTANT: Review these rules before activating!

require ["fileinto", "envelope", "imap4flags"];

# Rule: Amazon-Orders
# Description: Amazon order confirmations
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "bestellt,order"
) {
  fileinto "Shopping/Amazon-Orders";
  stop;
}

# Rule: Amazon-Shipping
# Description: Amazon shipping updates
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "versendet,shipped"
) {
  fileinto "Shopping/Amazon-Shipping";
  stop;
}

# Rule: Amazon-Returns
# Description: Amazon return notifications
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "rückgabe,return"
) {
  fileinto "Shopping/Amazon-Returns";
  stop;
}

# Rule: eBay-Activity
# Description: eBay notifications
if anyof (
  address :domain :is "from" "ebay.de",
  header :contains "subject" "gebot,bid,won"
) {
  fileinto "Shopping/eBay-Activity";
  stop;
}

# Rule: PayPal-Receipts
# Description: PayPal payment receipts
if anyof (
  address :domain :is "from" "paypal.com",
  header :contains "subject" "receipt,zahlung"
) {
  fileinto "Finance/PayPal-Receipts";
  stop;
}

# Rule: Stripe-Invoices
# Description: Stripe invoices
if anyof (
  address :domain :is "from" "stripe.com",
  header :contains "subject" "invoice,rechnung"
) {
  fileinto "Finance/Stripe-Invoices";
  stop;
}

# Rule: Bank-Notifications
# Description: Bank account notifications
if anyof (
  address :domain :is "from" "bank.de",
  header :contains "subject" "abhebung,deposit"
) {
  fileinto "Finance/Bank-Notifications";
  stop;
}

# Rule: Facebook-Notifications
# Description: Facebook notifications
if anyof (
  address :domain :is "from" "facebook.com",
  header :contains "subject" "friend request"
) {
  fileinto "Social/Facebook-Notifications";
  stop;
}

# Rule: LinkedIn-Invitations
# Description: LinkedIn invitations
if anyof (
  address :domain :is "from" "linkedin.com",
  header :contains "subject" "invitation"
) {
  fileinto "Social/LinkedIn-Invitations";
  stop;
}

# Rule: Twitter-Mentions
# Description: Twitter mentions and notifications
if anyof (
  address :domain :is "from" "twitter.com",
  header :contains "subject" "mention"
) {
  fileinto "Social/Twitter-Mentions";
  stop;
}

# Rule: GitHub-PRs
# Description: GitHub pull requests
if anyof (
  address :domain :is "from" "github.com",
  header :contains "subject" "pull request,PR"
) {
  fileinto "Work/GitHub-PRs";
  stop;
}

# Rule: GitLab-Issues
# Description: GitLab issues and notifications
if anyof (
  address :domain :is "from" "gitlab.com",
  header :contains "subject" "issue"
) {
  fileinto "Work/GitLab-Issues";
  stop;
}

# Rule: Slack-Messages
# Description: Slack messages and notifications
if anyof (
  address :domain :is "from" "slack.com",
  header :contains "subject" "message"
) {
  fileinto "Work/Slack-Messages";
  stop;
}

# Rule: Email-Alerts
# Description: Generic email alerts
if anyof (
  address :domain :is "from" "example.com",
  header :contains "subject" "alert,notification"
) {
  fileinto "Notifications/Email-Alerts";
  stop;
}

# Rule: Security-Warnings
# Description: Security warnings and notifications
if anyof (
  address :domain :is "from" "security.com",
  header :contains "subject" "warning,alert"
) {
  fileinto "Notifications/Security-Warnings";
  stop;
}

# Rule: App-Updates
# Description: App updates and notifications
if anyof (
  address :domain :is "from" "app.com",
  header :contains "subject" "update"
) {
  fileinto "Notifications/App-Updates";
  stop;
}

# Rule: Amazon-Specials
# Description: Amazon special offers
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "special,deal"
) {
  fileinto "Promotions/Amazon-Specials";
  stop;
}

# Rule: eBay-Deals
# Description: eBay deals and promotions
if anyof (
  address :domain :is "from" "ebay.de",
  header :contains "subject" "deal,promotion"
) {
  fileinto "Promotions/eBay-Deals";
  stop;
}

# Rule: PayPal-Promo
# Description: PayPal promotions and offers
if anyof (
  address :domain :is "from" "paypal.com",
  header :contains "subject" "promo,offer"
) {
  fileinto "Promotions/PayPal-Promo";
  stop;
}

# Rule: Amazon-Support
# Description: Amazon customer support emails
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "support"
) {
  fileinto "Support/Amazon-Support";
  stop;
}

# Rule: PayPal-Help
# Description: PayPal help and support emails
if anyof (
  address :domain :is "from" "paypal.com",
  header :contains "subject" "help"
) {
  fileinto "Support/PayPal-Help";
  stop;
}

# Rule: eBay-Assistance
# Description: eBay assistance and support emails
if anyof (
  address :domain :is "from" "ebay.de",
  header :contains "subject" "assistance"
) {
  fileinto "Support/eBay-Assistance";
  stop;
}

# Rule: Amazon-Billing
# Description: Amazon billing statements
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "billing"
) {
  fileinto "Billing/Amazon-Billing";
  stop;
}

# Rule: PayPal-Bills
# Description: PayPal billing statements
if anyof (
  address :domain :is "from" "paypal.com",
  header :contains "subject" "bill"
) {
  fileinto "Billing/PayPal-Bills";
  stop;
}

# Rule: eBay-Charges
# Description: eBay charges and billing statements
if anyof (
  address :domain :is "from" "ebay.de",
  header :contains "subject" "charges"
) {
  fileinto "Billing/eBay-Charges";
  stop;
}

# Rule: Amazon-Updates
# Description: Amazon product updates
if anyof (
  address :domain :is "from" "amazon.de",
  header :contains "subject" "update"
) {
  fileinto "Updates/Amazon-Updates";
  stop;
}

# Rule: PayPal-Software
# Description: PayPal software updates
if anyof (
  address :domain :is "from" "paypal.com",
  header :contains "subject" "software"
) {
  fileinto "Updates/PayPal-Software";
  stop;
}

# Rule: eBay-Enhancements
# Description: eBay enhancements and updates
if anyof (
  address :domain :is "from" "ebay.de",
  header :contains "subject" "enhancement"
) {
  fileinto "Updates/eBay-Enhancements";
  stop;
}

# Rule: Generic-Emails
# Description: Generic and miscellaneous emails
if anyof (
  address :domain :is "from" "example.com",
  header :contains "subject" "general"
) {
  fileinto "Miscellaneous/Generic-Emails";
  stop;
}

# Rule: Unsorted-Notifications
# Description: Unsorted notifications and alerts
if anyof (
  address :domain :is "from" "unsorted.com",
  header :contains "subject" "alert"
) {
  fileinto "Miscellaneous/Unsorted-Notifications";
  stop;
}

# Rule: Random-Messages
# Description: Random and miscellaneous messages
if anyof (
  address :domain :is "from" "random.com",
  header :contains "subject" "message"
) {
  fileinto "Miscellaneous/Random-Messages";
  stop;
}

# End of AI-generated rules
# All other mail goes to Inbox (default)