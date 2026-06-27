// Enterprise Multi-Gateway Allocation Configurations
const moonpayLinks = {
    single: "https://moonpay.hel.io/pay/6a3fa434b152ed0de00afb9f",
    sub: "https://moonpay.hel.io/pay/6a3bc83d9bd316f8a076ffe2"
};

// Current active tier configuration ('single' | 'sub')
let currentTier = 'single';

function setMode(type) {
    currentTier = type;
    const display = document.getElementById('price-display');
    const intervalDisplay = document.getElementById('price-interval');
    
    if (type === 'sub') {
        display.innerText = '$7,500';
        if (intervalDisplay) intervalDisplay.innerText = '/ 12-Month Rotation';
    } else {
        display.innerText = '$1,000';
        if (intervalDisplay) intervalDisplay.innerText = '/ One-Time Passport';
    }
    
    // Update the layout context immediately
    updatePaymentRoutes();
}

function updatePaymentRoutes() {
    const methodElement = document.querySelector('input[name="payment-method"]:checked');
    const method = methodElement ? methodElement.value : 'crypto';
    const linkElement = document.getElementById('payment-link');
    
    if (method === 'crypto') {
        // Route straight to MoonPay payment links
        linkElement.href = moonpayLinks[currentTier];
        linkElement.removeAttribute('onclick');
    } else {
        // Route to the local serverless Stripe Webhook Session Generator
        linkElement.href = '#';
        linkElement.setAttribute('onclick', `triggerStripeCheckout('${currentTier}')`);
    }
}

async function triggerStripeCheckout(tier) {
    console.log(`🤖 Initiating secure Stripe transaction session for: ${tier}`);
    try {
        const response = await fetch('/api/create-checkout-session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tier: tier })
        });
        
        const session = await response.json();
        if (session.url) {
            window.location.href = session.url;
        } else {
            alert('Stripe Route Initialization Error. Falling back to alternative gateway.');
        }
    } catch (err) {
        console.error('❌ Secure Checkout Pipeline Fault:', err);
    }
}

// Add DOM listener to handle gateway toggles if present
document.addEventListener('DOMContentLoaded', () => {
    const selectors = document.querySelectorAll('input[name="payment-method"]');
    selectors.forEach(el => el.addEventListener('change', updatePaymentRoutes));
    // Set baseline state
    setMode('single');
});
