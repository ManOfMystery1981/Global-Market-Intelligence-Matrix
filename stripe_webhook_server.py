import os
import stripe
from flask import Flask, request, jsonify
from supabase import create_client

app = Flask(__name__)

# Secure Config
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
ENDPOINT_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_ROLE_KEY"))

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, ENDPOINT_SECRET)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    # Triggered on successful payment
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get('customer_details', {}).get('email')
        
        # Insert user into Supabase to enable them for the next DeliveryAgent run
        supabase.table("subscribers").insert({
            "email": customer_email,
            "status": "active_annual",
            "subscription_id": session.get('id')
        }).execute()
        
        print(f"✅ New subscriber provisioned: {customer_email}")

    return '', 200

if __name__ == '__main__':
    app.run(port=4242)
