// server-payfast.js
const express = require('express');
const bodyParser = require('body-parser');
const crypto = require('crypto');
const app = express();
app.use(bodyParser.urlencoded({ extended: false })); // PayFast posts form-encoded
app.use(bodyParser.json());

// ENV (set these)
const PAYFAST_MERCHANT_ID = process.env.PAYFAST_MERCHANT_ID;
const PAYFAST_MERCHANT_KEY = process.env.PAYFAST_MERCHANT_KEY;
const PAYFAST_HOST = process.env.PAYFAST_HOST || 'https://www.payfast.co.za'; // production

// Helper: build query string as PayFast expects (ordered)
function buildPayfastString(params) {
  return Object.keys(params).map(k => `${k}=${encodeURIComponent(params[k]).replace(/%20/g,'+')}`).join('&');
}

// 1) Create order and generate PayFast form data for client to POST to PayFast
app.post('/api/payfast/create-order', async (req, res) => {
  // TODO: validate cart, create order in DB -> orderId, amountZAR
  const { amountZAR, items, customer } = req.body;
  const order = { id: 'ORDER-'+Date.now(), amountZAR }; // replace with DB create

  const pfData = {
    merchant_id: PAYFAST_MERCHANT_ID,
    merchant_key: PAYFAST_MERCHANT_KEY,
    return_url: `${process.env.BASE_URL}/checkout/success?order=${order.id}`,
    cancel_url: `${process.env.BASE_URL}/checkout/cancel?order=${order.id}`,
    notify_url: `${process.env.BASE_URL}/webhooks/payfast-itn`,
    m_payment_id: order.id,
    amount: Number(amountZAR).toFixed(2),
    item_name: `Order ${order.id}`,
    // optional customer info...
  };

  // Create signature (md5 of query-string)
  const pfString = buildPayfastString(pfData);
  const signature = crypto.createHash('md5').update(pfString).digest('hex');

  // Return data to client to post to PayFast OR render a server-side form that POSTs to PayFast.
  return res.json({
    payfastUrl: `${PAYFAST_HOST}/eng/process`,
    pfData,
    signature
  });
});

// 2) ITN (server-to-server notification) endpoint
app.post('/webhooks/payfast-itn', bodyParser.urlencoded({ extended: false }), async (req, res) => {
  const body = req.body; // PayFast posts form fields
  // For security, you SHOULD re-query PayFast to validate IPN (recommended pattern)
  // Minimal: construct the param string and verify signature:
  const receivedSignature = body.signature || '';
  // Remove signature field before constructing raw string
  const sigCopy = { ...body };
  delete sigCopy.signature;
  const pfString = buildPayfastString(sigCopy);
  const expectedSignature = crypto.createHash('md5').update(pfString).digest('hex');

  // Basic signature check
  if (expectedSignature !== receivedSignature) {
    console.warn('PayFast ITN signature mismatch', { expected: expectedSignature, received: receivedSignature });
    return res.status(400).send('Invalid signature');
  }

  // IMPORTANT: verify transaction with PayFast server-side to avoid spoofing.
  // Implement server-side verification (HTTP POST back to PayFast with the raw data)
  // Simple pseudo-check (implement actual verification per PayFast docs)
  // TODO: fetch order by body['m_payment_id'] and reconcile.

  // Example update:
  const orderId = body.m_payment_id;
  const paymentStatus = body.payment_status; // e.g., COMPLETE
  // TODO: update DB order state only after verifying amount and status

  console.log('PayFast ITN verified for order', orderId, 'status', paymentStatus);
  res.send('OK'); // PayFast requires a 200 response text
});

app.listen(3000, ()=> console.log('PayFast demo server listening on 3000'));
