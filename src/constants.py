"""Constants and configuration for the site testing system."""

DOMAINS_OF_INTEREST = {
    'applovin.com': {'type': 'tracking', 'critical': True},
    'axon.ai': {'type': 'analytics', 'critical': False},
    'albss.com': {'type': 'analytics', 'critical': False}
}

TRACKING_INDICATORS = {
    'shopify': ['myshopify.com', 'shopify.shop', 'link[href*="shopify"]', 'script[src*="shopify"]'],
    'gtm': ['gtm.start'],
    'axon': ['axon'],
    'ga': ['ga.js', 'analytics.js'],
    'ga4': ['gtag']
}

# Headless Shopify detection patterns
HEADLESS_SHOPIFY_INDICATORS = {
    'api_endpoints': [
        'store.myshopify.com/api/graphql',
        'shopify.com/api/graphql',
        'shopify.com/api/2023-01/graphql.json',  # Latest API version
        'shopify.com/api/2022-10/graphql.json'
    ],
    'script_patterns': [
        '@shopify/hydrogen',
        '@shopify/storefront-api',
        'shopify.loadFeatures',
        'shopify.buy.Button',
        'shopify-buy'
    ],
    'meta_tags': [
        'shopify-digital-wallet',
        'shopify-checkout-api-token',
        'shopify-storefront-api-token'
    ],
    'request_headers': [
        'X-Shopify-Storefront-Access-Token',
        'X-Shopify-Storefront-API-Version'
    ]
}

# Non-critical errors that should be ignored
IGNORED_ERRORS = [
    'ERR_ABORTED',  # Regular abort, usually not an issue
    'NS_BINDING_ABORTED',  # Firefox specific abort
    'net::ERR_BLOCKED_BY_CLIENT',  # Ad blocker behavior
    'NS_ERROR_NET_INTERRUPT'  # Connection interrupted
]

# Browser launch settings
BROWSER_SETTINGS = {
    'headless': True,
    'args': ['--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage']
}

# Timeouts
PAGE_LOAD_TIMEOUT = 10000  # 10 seconds
NETWORK_IDLE_TIMEOUT = 10000  # 10 seconds
ADDITIONAL_WAIT_TIME = 5  # seconds 