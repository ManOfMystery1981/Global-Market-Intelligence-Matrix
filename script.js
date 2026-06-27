// Global configuration for checkout
const links = {
    single: "https://moonpay.hel.io/pay/6a3fa434b152ed0de00afb9f",
    sub: "https://moonpay.hel.io/pay/6a3bc83d9bd316f8a076ffe2"
};

function setMode(type) {
    const link = document.getElementById('payment-link');
    const display = document.getElementById('price-display');
    
    if (type === 'sub') {
        display.innerText = '$10,000';
        link.href = links.sub;
    } else {
        display.innerText = '$1,000';
        link.href = links.single;
    }
}
