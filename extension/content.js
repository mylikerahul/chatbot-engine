/**
 * ShopBuddy AI Assistant v8.0.0
 * Clean Architecture - Fully Object-Oriented
 */

(function() {
    "use strict";
    
    if (window.ShopBuddyInjected) return;
    window.ShopBuddyInjected = true;

    class Config {
        static API_URL = "http://127.0.0.1:8080/chat";
        static VERSION = "8.0.0";
        static MAX_ITEMS = 50;
        static CACHE_DURATION = 5 * 60 * 1000;
        
        static VALIDATION = {
            minTitleLength: 20,
            maxTitleLength: 250,
            minWords: 3,
            minScore: 40,
            minPrice: 50,
            maxPrice: 10000000
        };
        
        static BLACKLIST_PATTERNS = [
            /^continue\s*shopping/i, /^create\s*(a\s*)?account/i, /^sign\s*(in|up)/i,
            /^log\s*in/i, /^register/i, /^explore\s*all/i, /^see\s*(more|all)/i,
            /^view\s*(all|more|details|offer)/i, /^show\s*more/i, /^load\s*more/i,
            /^shop\s*now/i, /^buy\s*now/i, /^add\s*to\s*(cart|basket|bag)/i,
            /^subscribe/i, /^learn\s*more/i, /^read\s*more/i, /^click\s*here/i,
            /^get\s*started/i, /^join\s*(now|prime)/i, /^try\s*(prime|now|free)/i,
            /^deals?$/i, /^offers?$/i, /^sale$/i, /^new$/i, /^trending$/i,
            /^popular$/i, /^featured$/i, /^sponsored$/i, /^advertisement/i,
            /^home$/i, /^cart$/i, /^wishlist/i, /^account/i, /^orders?$/i,
            /^help$/i, /^contact/i, /^about/i, /^categories/i, /^deliver\s*to/i,
            /^hello,?\s*select/i, /^returns/i, /^today'?s?\s*deals/i,
            /^customer\s*service/i, /^gift\s*cards?/i, /^sell$/i, /^all$/i,
            /^amazon/i, /^back\s*to\s*top/i, /^up\s*to\s*\d+%\s*off$/i,
            /^save\s*\d+%/i, /^flat\s*\d+%/i, /^\d+%\s*off$/i,
            /^great\s*indian/i, /^prime\s*(day|deal)/i, /^lightning\s*deal/i,
            /^deal\s*of\s*the\s*day/i, /^trending\s*(now|deal)/i,
            /^emerging\s*business/i, /^become\s*a\s*seller/i,
            /^download\s*app/i, /^free\s*delivery/i, /^no\s*cost\s*emi/i,
            /^bank\s*offer/i, /^cashback/i, /^[a-z]{1,12}$/i,
            /^[\d%₹$\s,\.]+$/, /^\s*$/, /^[^a-zA-Z]*$/,
            /^shop\s*by\s*category/i, /^top\s*categories/i,
            /^customers\s*also/i, /^you\s*may\s*also/i
        ];
    }

    class PageType {
        static HOMEPAGE = 'homepage';
        static SEARCH = 'search';
        static PRODUCT = 'product';
        static CATEGORY = 'category';
        static UNKNOWN = 'unknown';
    }

    class SiteConfig {
        constructor(key, name, category, urlPatterns, selectors) {
            this.key = key;
            this.name = name;
            this.category = category;
            this.urlPatterns = urlPatterns;
            this.selectors = selectors;
        }
    }

    class SiteRegistry {
        static sites = {
            amazon: new SiteConfig(
                "amazon",
                "Amazon",
                "ecommerce",
                {
                    search: ['/s?', '/s/', '/s?k='],
                    product: ['/dp/', '/gp/product/'],
                    category: ['/b/', '/b?']
                },
                {
                    [PageType.SEARCH]: {
                        containers: ['[data-component-type="s-search-result"]', '.s-result-item[data-asin]:not([data-asin=""])'],
                        title: ['h2 a span', 'h2 span', '.a-text-normal'],
                        price: ['.a-price .a-offscreen', '.a-price-whole'],
                        rating: ['.a-icon-star-small .a-icon-alt'],
                        image: ['img.s-image']
                    },
                    [PageType.PRODUCT]: {
                        containers: ['#dp-container', '#ppd', '#centerCol'],
                        title: ['#productTitle', '#title span'],
                        price: ['.a-price .a-offscreen', '#priceblock_ourprice'],
                        rating: ['#acrPopover span'],
                        image: ['#landingImage']
                    },
                    [PageType.HOMEPAGE]: {
                        containers: ['[data-asin]:not([data-asin=""])', '.a-carousel-card', '.p13n-sc-uncoverable-faceout', '.feed-carousel-card'],
                        title: ['.p13n-sc-truncate-desktop-type2', '.p13n-sc-truncate', 'a[href*="/dp/"] span', 'h2 a span'],
                        price: ['.a-price .a-offscreen', '.p13n-sc-price'],
                        rating: ['.a-icon-star-small .a-icon-alt'],
                        image: ['img.p13n-product-image', 'img']
                    }
                }
            ),
            
            flipkart: new SiteConfig(
                "flipkart",
                "Flipkart",
                "ecommerce",
                {
                    search: ['/search?', 'q='],
                    product: ['/p/'],
                    category: ['/store/']
                },
                {
                    [PageType.SEARCH]: {
                        containers: ['[data-id]', '._1AtVbE', '._2kHMtA'],
                        title: ['._4rR01T', '.s1Q9rs', '.IRpwTa', '.KzDlHZ'],
                        price: ['._30jeq3', '._1_WHN1'],
                        rating: ['._3LWZlK'],
                        image: ['._396cs4']
                    },
                    [PageType.PRODUCT]: {
                        containers: ['._1YokD2', '.dyC4hf'],
                        title: ['.B_NuCI'],
                        price: ['._30jeq3._16Jk6d'],
                        rating: ['._3LWZlK'],
                        image: ['._396cs4._2amPTt']
                    },
                    [PageType.HOMEPAGE]: {
                        containers: ['._1dqBbG', '._4ddWXP', '[data-id]'],
                        title: ['._2WkVRV', '.IRpwTa'],
                        price: ['._30jeq3'],
                        rating: ['._3LWZlK'],
                        image: ['._2r_T1I']
                    }
                }
            )
        };
        
        static get(hostname) {
            const host = hostname.toLowerCase().replace("www.", "");
            for (const [key, config] of Object.entries(this.sites)) {
                if (host.includes(key)) return config;
            }
            return this.getGeneric();
        }
        
        static getGeneric() {
            return new SiteConfig(
                "generic",
                "Website",
                "general",
                {
                    search: ['search', 'q='],
                    product: ['/product/', '/item/'],
                    category: ['/category/']
                },
                {
                    [PageType.SEARCH]: {
                        containers: ['article', '.product', '.card'],
                        title: ['h2', 'h3', 'a'],
                        price: ['[class*="price"]'],
                        rating: ['[class*="rating"]'],
                        image: ['img']
                    },
                    [PageType.HOMEPAGE]: {
                        containers: ['article', '.product', '.card'],
                        title: ['h2', 'h3', 'a'],
                        price: ['[class*="price"]'],
                        rating: ['[class*="rating"]'],
                        image: ['img']
                    }
                }
            );
        }
    }

    class ProductValidator {
        static isValidProduct(item) {
            const nameCheck = this.isValidName(item.name || '');
            if (!nameCheck.valid) return nameCheck;
            
            const hasPrice = this.isValidPrice(item.price || '');
            const hasRating = this.isValidRating(item.rating || '');
            
            if (!hasPrice && !hasRating) {
                return { valid: false, reason: 'No price or rating' };
            }
            
            if (item.price) {
                const priceValue = this.extractPriceValue(item.price);
                if (priceValue > 0 && priceValue < Config.VALIDATION.minPrice) {
                    return { valid: false, reason: 'Price too low' };
                }
            }
            
            return { valid: true };
        }
        
        static isValidName(text) {
            if (!text || typeof text !== 'string') {
                return { valid: false, reason: 'Empty text' };
            }
            
            const cleaned = text.trim();
            const { minTitleLength, maxTitleLength, minWords } = Config.VALIDATION;
            
            if (cleaned.length < minTitleLength) return { valid: false, reason: 'Too short' };
            if (cleaned.length > maxTitleLength) return { valid: false, reason: 'Too long' };
            if (!/[a-zA-Z]/.test(cleaned)) return { valid: false, reason: 'No letters' };
            
            const words = cleaned.split(/\s+/).filter(w => w.length > 1);
            if (words.length < minWords) return { valid: false, reason: 'Too few words' };
            
            for (const pattern of Config.BLACKLIST_PATTERNS) {
                if (pattern.test(cleaned)) return { valid: false, reason: 'Blacklisted' };
            }
            
            if (/^\d+%/.test(cleaned) || /^up\s*to/i.test(cleaned)) {
                return { valid: false, reason: 'Promotional text' };
            }
            
            return { valid: true };
        }
        
        static isValidPrice(price) {
            if (!price || !/\d/.test(price)) return false;
            return this.extractPriceValue(price) >= Config.VALIDATION.minPrice;
        }
        
        static extractPriceValue(price) {
            if (!price) return 0;
            const match = price.match(/[\d,]+\.?\d*/);
            return match ? parseFloat(match[0].replace(/,/g, '')) : 0;
        }
        
        static isValidRating(rating) {
            if (!rating) return false;
            const match = rating.match(/([\d.]+)/);
            if (match) {
                const value = parseFloat(match[1]);
                return value >= 1 && value <= 5;
            }
            return false;
        }
        
        static scoreProduct(item) {
            let score = 0;
            
            if (item.price && this.isValidPrice(item.price)) {
                score += 40;
                if (/[₹$€£]/.test(item.price)) score += 10;
            }
            
            if (item.rating && this.isValidRating(item.rating)) score += 30;
            if (item.image && item.image.length > 20) score += 10;
            
            if (item.name) {
                if (item.name.length > 40) score += 10;
                
                if (/\b(samsung|apple|sony|lg|hp|dell|lenovo|asus|mi|xiaomi|realme|oppo|vivo|oneplus|boat|jbl|philips|bajaj|nike|adidas|puma)\b/i.test(item.name)) {
                    score += 25;
                }
                
                if (/\b(phone|mobile|laptop|headphone|earphone|speaker|watch|camera|tv|refrigerator|ac|mixer|microwave|charger|power\s*bank)\b/i.test(item.name)) {
                    score += 20;
                }
                
                if (/\b\d+\s*(gb|tb|mp|mah|w|inch)\b/i.test(item.name)) score += 15;
            }
            
            return score;
        }
    }

    class CacheManager {
        constructor() {
            this.store = new Map();
            this.duration = Config.CACHE_DURATION;
        }
        
        generateKey(query, url) {
            return `${query.toLowerCase().trim()}::${url}`;
        }
        
        get(key) {
            const item = this.store.get(key);
            if (!item) return null;
            if (Date.now() - item.timestamp > this.duration) {
                this.store.delete(key);
                return null;
            }
            return item.data;
        }
        
        set(key, data) {
            this.store.set(key, { data, timestamp: Date.now() });
        }
        
        clear() {
            this.store.clear();
        }
    }

    class PageDetector {
        constructor() {
            this.url = window.location.href.toLowerCase();
            this.pathname = window.location.pathname.toLowerCase();
            this.hostname = window.location.hostname;
            this.search = window.location.search.toLowerCase();
        }
        
        matchesPatterns(patterns) {
            if (!patterns) return false;
            return patterns.some(p => 
                this.url.includes(p) || this.pathname.includes(p) || this.search.includes(p)
            );
        }
        
        detect(siteConfig) {
            const { urlPatterns } = siteConfig;
            if (!urlPatterns) return PageType.UNKNOWN;
            
            if (this.matchesPatterns(urlPatterns.product)) return PageType.PRODUCT;
            if (this.matchesPatterns(urlPatterns.search)) return PageType.SEARCH;
            if (this.matchesPatterns(urlPatterns.category)) return PageType.CATEGORY;
            if (this.isHomepage()) return PageType.HOMEPAGE;
            
            return PageType.HOMEPAGE;
        }
        
        isHomepage() {
            return this.pathname === "/" || this.pathname === "" || /^\/?(in|us|uk)?\/?\??$/.test(this.pathname);
        }
    }

    class ElementExtractor {
        static extractText(element, selectors, maxLength = 200) {
            if (!element || !selectors) return "";
            
            for (const selector of selectors) {
                try {
                    const el = element.querySelector(selector);
                    if (el) {
                        const text = (el.textContent || el.innerText || el.getAttribute("alt") || "").trim();
                        if (text.length > 2 && text.length < maxLength) {
                            return text.replace(/\s+/g, " ").trim();
                        }
                    }
                } catch (e) {}
            }
            return "";
        }
        
        static extractPrice(element, selectors) {
            const raw = this.extractText(element, selectors, 50);
            if (!raw) return "";
            const match = raw.match(/[₹$€£]?\s*[\d,]+\.?\d*/);
            return match ? match[0].trim() : raw;
        }
        
        static extractRating(element, selectors) {
            const raw = this.extractText(element, selectors, 30);
            if (!raw) return "";
            const match = raw.match(/[\d.]+/);
            return match ? match[0] : raw;
        }
        
        static extractImage(element, selectors) {
            if (!element || !selectors) return "";
            for (const selector of selectors) {
                try {
                    const img = element.querySelector(selector);
                    if (img) {
                        return img.getAttribute("src") || img.getAttribute("data-src") || "";
                    }
                } catch (e) {}
            }
            return "";
        }
    }

    class ProductScraper {
        constructor() {
            this.pageDetector = null;
            this.siteConfig = null;
            this.pageType = null;
            this.selectors = null;
        }
        
        initialize() {
            this.pageDetector = new PageDetector();
            this.siteConfig = SiteRegistry.get(this.pageDetector.hostname);
            this.pageType = this.pageDetector.detect(this.siteConfig);
            this.selectors = this.getSelectors();
        }
        
        getSelectors() {
            const { selectors } = this.siteConfig;
            if (!selectors) return null;
            
            if (selectors[this.pageType]) return selectors[this.pageType];
            if (this.pageType === PageType.CATEGORY && selectors[PageType.SEARCH]) {
                return selectors[PageType.SEARCH];
            }
            return selectors[PageType.SEARCH] || selectors[PageType.HOMEPAGE] || null;
        }
        
        scrape() {
            this.initialize();
            
            if (!this.selectors) return this.createResult([]);
            
            const items = this.extractItems();
            const validated = this.validateItems(items);
            const unique = this.deduplicate(validated);
            
            if (unique.length === 0) {
                const altItems = this.alternativeScrape();
                if (altItems.length > 0) return this.createResult(altItems);
            }
            
            return this.createResult(unique);
        }
        
        extractItems() {
            const items = [];
            const { containers, title, price, rating, image } = this.selectors;
            
            for (const containerSel of containers) {
                try {
                    const elements = document.querySelectorAll(containerSel);
                    if (elements.length === 0) continue;
                    
                    elements.forEach((el, i) => {
                        const item = {
                            id: i + 1,
                            name: ElementExtractor.extractText(el, title, 200),
                            price: ElementExtractor.extractPrice(el, price),
                            rating: ElementExtractor.extractRating(el, rating),
                            image: ElementExtractor.extractImage(el, image),
                            type: this.siteConfig.category
                        };
                        
                        if (item.name) items.push(item);
                    });
                    
                    if (items.length > 0) break;
                } catch (e) {}
            }
            
            return items;
        }
        
        validateItems(items) {
            const validated = [];
            
            for (const item of items) {
                const check = ProductValidator.isValidProduct(item);
                if (!check.valid) continue;
                
                const score = ProductValidator.scoreProduct(item);
                if (score < Config.VALIDATION.minScore) continue;
                
                item._score = score;
                validated.push(item);
            }
            
            return validated.sort((a, b) => (b._score || 0) - (a._score || 0));
        }
        
        alternativeScrape() {
            const items = [];
            const productLinks = document.querySelectorAll('a[href*="/dp/"]');
            const seenAsins = new Set();
            
            productLinks.forEach((link) => {
                const asinMatch = link.href.match(/\/dp\/([A-Z0-9]{10})/);
                if (!asinMatch) return;
                
                const asin = asinMatch[1];
                if (seenAsins.has(asin)) return;
                seenAsins.add(asin);
                
                const container = link.closest('[data-asin], .a-carousel-card') || link.parentElement?.parentElement;
                if (!container) return;
                
                let title = '';
                const titleEl = container.querySelector('span.a-text-normal, .p13n-sc-truncate, h2 span');
                if (titleEl) title = titleEl.textContent?.trim() || '';
                if (!title) title = link.textContent?.trim() || '';
                
                const check = ProductValidator.isValidName(title);
                if (!check.valid) return;
                
                let price = '';
                const priceEl = container.querySelector('.a-price .a-offscreen, .p13n-sc-price');
                if (priceEl) price = priceEl.textContent?.trim() || '';
                
                let rating = '';
                const ratingEl = container.querySelector('.a-icon-alt');
                if (ratingEl) {
                    const match = ratingEl.textContent?.match(/[\d.]+/);
                    rating = match ? match[0] : '';
                }
                
                const item = {
                    id: items.length + 1,
                    name: title.slice(0, 120),
                    price: price,
                    rating: rating,
                    image: '',
                    type: 'ecommerce'
                };
                
                const score = ProductValidator.scoreProduct(item);
                if (score >= Config.VALIDATION.minScore) {
                    item._score = score;
                    items.push(item);
                }
            });
            
            return this.deduplicate(items);
        }
        
        deduplicate(items) {
            const seen = new Set();
            const unique = [];
            
            for (const item of items) {
                const key = item.name.toLowerCase().slice(0, 50);
                if (!seen.has(key)) {
                    seen.add(key);
                    unique.push({
                        ...item,
                        name: item.name.slice(0, 120)
                    });
                }
            }
            
            return unique.slice(0, Config.MAX_ITEMS);
        }
        
        createResult(items) {
            return {
                site: {
                    key: this.siteConfig.key,
                    name: this.siteConfig.name,
                    category: this.siteConfig.category
                },
                page: {
                    type: this.pageType,
                    url: window.location.href,
                    title: document.title,
                    isHomepage: this.pageDetector.isHomepage()
                },
                items: items,
                meta: {
                    count: items.length,
                    timestamp: new Date().toISOString(),
                    version: Config.VERSION
                }
            };
        }
    }

    class APIClient {
        constructor() {
            this.baseUrl = Config.API_URL;
            this.timeout = 30000;
        }
        
        async send(query, data) {
            const payload = {
                query: query,
                products: data.items,
                page_url: data.page.url,
                page_title: data.page.title,
                site_type: data.site.name,
                page_type: data.site.category,
                item_count: data.meta.count
            };
            
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);
            
            try {
                const response = await fetch(this.baseUrl, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                
                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }
                
                return await response.json();
            } catch (error) {
                clearTimeout(timeoutId);
                throw error;
            }
        }
    }

    class StyleManager {
        static inject() {
            if (document.getElementById("sb-styles")) return;
            
            const style = document.createElement("style");
            style.id = "sb-styles";
            style.textContent = this.getStyles();
            document.head.appendChild(style);
        }
        
        static getStyles() {
            return `
                :root {
                    --sb-bg-primary: rgba(255, 255, 255, 0.85);
                    --sb-bg-secondary: rgba(249, 249, 251, 0.95);
                    --sb-bg-tertiary: rgba(242, 242, 247, 0.9);
                    --sb-bg-hover: rgba(235, 235, 240, 0.9);
                    --sb-text-primary: #1d1d1f;
                    --sb-text-secondary: rgba(60, 60, 67, 0.85);
                    --sb-text-tertiary: rgba(60, 60, 67, 0.6);
                    --sb-accent: #007aff;
                    --sb-accent-hover: #0051d5;
                    --sb-accent-light: rgba(0, 122, 255, 0.1);
                    --sb-green: #34c759;
                    --sb-orange: #ff9500;
                    --sb-red: #ff3b30;
                    --sb-border: rgba(0, 0, 0, 0.1);
                    --sb-border-light: rgba(0, 0, 0, 0.06);
                    --sb-shadow: 0 8px 30px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.08);
                    --sb-shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
                    --sb-radius-lg: 16px;
                    --sb-radius-md: 12px;
                    --sb-radius-sm: 8px;
                }
                
                * { box-sizing: border-box; }
                
                #sb-bubble {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    width: 56px;
                    height: 56px;
                    background: linear-gradient(135deg, #007aff 0%, #0051d5 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    box-shadow: 0 4px 16px rgba(0, 122, 255, 0.3), 0 2px 8px rgba(0, 0, 0, 0.15);
                    z-index: 2147483646;
                    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
                    border: none;
                    outline: none;
                }
                
                #sb-bubble:hover {
                    transform: scale(1.1);
                    box-shadow: 0 6px 24px rgba(0, 122, 255, 0.4), 0 4px 12px rgba(0, 0, 0, 0.2);
                }
                
                #sb-bubble:active { transform: scale(0.98); }
                
                #sb-bubble svg {
                    width: 26px;
                    height: 26px;
                    fill: white;
                    filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
                }
                
                #sb-window {
                    position: fixed;
                    bottom: 86px;
                    right: 20px;
                    width: min(380px, calc(100vw - 40px));
                    max-width: 100%;
                    height: min(580px, calc(100vh - 120px));
                    max-height: calc(100vh - 120px);
                    background: var(--sb-bg-primary);
                    backdrop-filter: blur(40px) saturate(180%);
                    -webkit-backdrop-filter: blur(40px) saturate(180%);
                    border-radius: var(--sb-radius-lg);
                    display: none;
                    flex-direction: column;
                    box-shadow: var(--sb-shadow);
                    z-index: 2147483647;
                    overflow: hidden;
                    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', system-ui, sans-serif;
                    border: 1px solid var(--sb-border-light);
                    font-size: 15px;
                    line-height: 1.47;
                    -webkit-font-smoothing: antialiased;
                    -moz-osx-font-smoothing: grayscale;
                }
                
                @media (max-width: 640px) {
                    #sb-bubble {
                        width: 52px;
                        height: 52px;
                        bottom: 16px;
                        right: 16px;
                    }
                    
                    #sb-bubble svg {
                        width: 24px;
                        height: 24px;
                    }
                    
                    #sb-window {
                        bottom: 78px;
                        right: 16px;
                        width: calc(100vw - 32px);
                        height: calc(100vh - 110px);
                        max-height: calc(100vh - 110px);
                        border-radius: 14px;
                    }
                }
                
                @media (max-width: 400px) {
                    #sb-window {
                        bottom: 78px;
                        right: 12px;
                        width: calc(100vw - 24px);
                        height: calc(100vh - 100px);
                        max-height: calc(100vh - 100px);
                    }
                }
                
                #sb-window.open {
                    display: flex;
                    animation: sb-appear 0.35s cubic-bezier(0.16, 1, 0.3, 1);
                }
                
                @keyframes sb-appear {
                    from {
                        opacity: 0;
                        transform: translateY(16px) scale(0.94);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0) scale(1);
                    }
                }
                
                .sb-titlebar {
                    height: 54px;
                    min-height: 54px;
                    background: var(--sb-bg-secondary);
                    display: flex;
                    align-items: center;
                    padding: 0 16px;
                    border-bottom: 1px solid var(--sb-border-light);
                    user-select: none;
                    flex-shrink: 0;
                }
                
                @media (max-width: 640px) {
                    .sb-titlebar {
                        height: 50px;
                        min-height: 50px;
                        padding: 0 14px;
                    }
                }
                
                .sb-traffic {
                    display: flex;
                    gap: 8px;
                    margin-right: 14px;
                }
                
                .sb-traffic button {
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    border: none;
                    cursor: pointer;
                    transition: opacity 0.2s, transform 0.15s;
                    padding: 0;
                }
                
                .sb-traffic button:hover {
                    opacity: 0.85;
                    transform: scale(1.1);
                }
                
                .sb-traffic button:active { transform: scale(0.95); }
                
                .sb-traffic-close {
                    background: #ff5f56;
                    box-shadow: 0 1px 2px rgba(255, 95, 86, 0.3);
                }
                
                .sb-traffic-min {
                    background: #ffbd2e;
                    box-shadow: 0 1px 2px rgba(255, 189, 46, 0.3);
                }
                
                .sb-traffic-max {
                    background: #27c93f;
                    box-shadow: 0 1px 2px rgba(39, 201, 63, 0.3);
                }
                
                .sb-title-content {
                    flex: 1;
                    text-align: center;
                    min-width: 0;
                }
                
                .sb-title-text {
                    font-size: 14px;
                    font-weight: 600;
                    color: var(--sb-text-primary);
                    margin: 0;
                    letter-spacing: -0.3px;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
                
                .sb-title-subtitle {
                    font-size: 11px;
                    color: var(--sb-text-tertiary);
                    margin-top: 2px;
                    font-weight: 400;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
                
                @media (max-width: 640px) {
                    .sb-title-text { font-size: 13px; }
                    .sb-title-subtitle { font-size: 10px; }
                }
                
                .sb-title-actions {
                    display: flex;
                    gap: 8px;
                }
                
                .sb-action-btn {
                    width: 32px;
                    height: 32px;
                    background: white;
                    border: 1px solid var(--sb-border-light);
                    border-radius: var(--sb-radius-sm);
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.2s;
                    padding: 0;
                    box-shadow: var(--sb-shadow-sm);
                }
                
                @media (max-width: 640px) {
                    .sb-action-btn {
                        width: 30px;
                        height: 30px;
                    }
                }
                
                .sb-action-btn:hover {
                    background: var(--sb-bg-tertiary);
                    border-color: var(--sb-border);
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }
                
                .sb-action-btn:active { transform: scale(0.96); }
                
                .sb-action-btn svg {
                    width: 16px;
                    height: 16px;
                    stroke: var(--sb-text-secondary);
                    fill: none;
                    stroke-width: 2;
                }
                
                .sb-messages {
                    flex: 1;
                    overflow-y: auto;
                    overflow-x: hidden;
                    padding: 16px 14px;
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                    background: white;
                    min-height: 0;
                }
                
                @media (max-width: 640px) {
                    .sb-messages {
                        padding: 14px 12px;
                        gap: 10px;
                    }
                }
                
                .sb-messages::-webkit-scrollbar { width: 6px; }
                .sb-messages::-webkit-scrollbar-track { background: transparent; }
                .sb-messages::-webkit-scrollbar-thumb {
                    background: rgba(0, 0, 0, 0.15);
                    border-radius: 3px;
                    border: 1px solid transparent;
                    background-clip: padding-box;
                }
                .sb-messages::-webkit-scrollbar-thumb:hover {
                    background: rgba(0, 0, 0, 0.25);
                    background-clip: padding-box;
                }
                
                .sb-message {
                    max-width: 85%;
                    padding: 11px 14px;
                    border-radius: 16px;
                    font-size: 14px;
                    line-height: 1.5;
                    animation: sb-message-in 0.25s cubic-bezier(0.16, 1, 0.3, 1);
                    word-wrap: break-word;
                }
                
                @media (max-width: 640px) {
                    .sb-message {
                        max-width: 90%;
                        padding: 10px 12px;
                        font-size: 13px;
                        border-radius: 14px;
                    }
                }
                
                @keyframes sb-message-in {
                    from {
                        opacity: 0;
                        transform: translateY(10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                
                .sb-message-user {
                    background: var(--sb-accent);
                    color: white;
                    align-self: flex-end;
                    border-bottom-right-radius: 5px;
                    box-shadow: 0 2px 8px rgba(0, 122, 255, 0.2);
                }
                
                .sb-message-bot {
                    background: var(--sb-bg-secondary);
                    color: var(--sb-text-primary);
                    align-self: flex-start;
                    border-bottom-left-radius: 5px;
                    border: 1px solid var(--sb-border-light);
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
                }
                
                .sb-card {
                    background: white;
                    border-radius: var(--sb-radius-md);
                    overflow: hidden;
                    border: 1px solid var(--sb-border-light);
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
                }
                
                .sb-card-header {
                    padding: 14px 16px;
                    border-bottom: 1px solid var(--sb-border-light);
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    background: var(--sb-bg-secondary);
                }
                
                @media (max-width: 640px) {
                    .sb-card-header { padding: 12px 14px; }
                }
                
                .sb-card-icon {
                    width: 34px;
                    height: 34px;
                    min-width: 34px;
                    background: linear-gradient(135deg, var(--sb-accent) 0%, var(--sb-accent-hover) 100%);
                    border-radius: 9px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 2px 8px rgba(0, 122, 255, 0.25);
                }
                
                .sb-card-icon svg {
                    width: 18px;
                    height: 18px;
                    stroke: white;
                    fill: none;
                    stroke-width: 2;
                }
                
                .sb-card-title {
                    font-weight: 600;
                    font-size: 14px;
                    color: var(--sb-text-primary);
                    letter-spacing: -0.2px;
                }
                
                @media (max-width: 640px) {
                    .sb-card-title { font-size: 13px; }
                }
                
                .sb-card-body {
                    padding: 14px 16px;
                    background: white;
                }
                
                @media (max-width: 640px) {
                    .sb-card-body { padding: 12px 14px; }
                }
                
                .sb-card-row {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 9px 0;
                    gap: 10px;
                }
                
                .sb-card-row:not(:last-child) { border-bottom: 1px solid var(--sb-border-light); }
                
                .sb-card-label {
                    color: var(--sb-text-secondary);
                    font-size: 13px;
                    font-weight: 400;
                }
                
                .sb-card-value {
                    color: var(--sb-text-primary);
                    font-size: 13px;
                    font-weight: 600;
                    text-align: right;
                    word-break: break-word;
                }
                
                @media (max-width: 640px) {
                    .sb-card-label,
                    .sb-card-value { font-size: 12px; }
                }
                
                .sb-badge {
                    background: var(--sb-accent);
                    color: white;
                    padding: 4px 11px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 600;
                    box-shadow: 0 2px 6px rgba(0, 122, 255, 0.2);
                    white-space: nowrap;
                }
                
                .sb-card-footer {
                    padding: 12px 16px;
                    background: var(--sb-accent-light);
                    border-top: 1px solid var(--sb-border-light);
                    font-size: 12px;
                    color: var(--sb-text-secondary);
                    font-weight: 400;
                    line-height: 1.4;
                }
                
                @media (max-width: 640px) {
                    .sb-card-footer {
                        padding: 10px 14px;
                        font-size: 11px;
                    }
                }
                
                .sb-card-footer.warning { background: rgba(255, 149, 0, 0.08); }
                
                .sb-quick-actions {
                    padding: 10px 14px;
                    display: flex;
                    flex-wrap: wrap;
                    gap: 7px;
                    border-top: 1px solid var(--sb-border-light);
                    background: var(--sb-bg-secondary);
                    flex-shrink: 0;
                }
                
                @media (max-width: 640px) {
                    .sb-quick-actions {
                        padding: 8px 12px;
                        gap: 6px;
                    }
                }
                
                .sb-quick-btn {
                    background: white;
                    border: 1px solid var(--sb-border-light);
                    color: var(--sb-text-secondary);
                    padding: 7px 14px;
                    border-radius: 16px;
                    font-size: 12px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.2s;
                    font-family: inherit;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
                    white-space: nowrap;
                }
                
                @media (max-width: 640px) {
                    .sb-quick-btn {
                        padding: 6px 12px;
                        font-size: 11px;
                    }
                }
                
                .sb-quick-btn:hover {
                    background: var(--sb-accent);
                    border-color: var(--sb-accent);
                    color: white;
                    box-shadow: 0 2px 8px rgba(0, 122, 255, 0.25);
                    transform: translateY(-1px);
                }
                
                .sb-quick-btn:active { transform: translateY(0); }
                
                .sb-input-area {
                    padding: 12px 14px;
                    display: flex;
                    gap: 10px;
                    border-top: 1px solid var(--sb-border-light);
                    background: var(--sb-bg-secondary);
                    flex-shrink: 0;
                }
                
                @media (max-width: 640px) {
                    .sb-input-area {
                        padding: 10px 12px;
                        gap: 8px;
                    }
                }
                
                .sb-input {
                    flex: 1;
                    min-width: 0;
                    background: white;
                    border: 1px solid var(--sb-border-light);
                    border-radius: var(--sb-radius-md);
                    padding: 10px 14px;
                    color: var(--sb-text-primary);
                    font-size: 14px;
                    font-family: inherit;
                    outline: none;
                    transition: all 0.2s;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
                }
                
                @media (max-width: 640px) {
                    .sb-input {
                        padding: 9px 12px;
                        font-size: 13px;
                    }
                }
                
                .sb-input:focus {
                    border-color: var(--sb-accent);
                    box-shadow: 0 0 0 3px var(--sb-accent-light), 0 1px 3px rgba(0, 0, 0, 0.05);
                }
                
                .sb-input::placeholder { color: var(--sb-text-tertiary); }
                
                .sb-input:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                    background: var(--sb-bg-tertiary);
                }
                
                .sb-send-btn {
                    width: 42px;
                    height: 42px;
                    min-width: 42px;
                    background: linear-gradient(135deg, var(--sb-accent) 0%, var(--sb-accent-hover) 100%);
                    border: none;
                    border-radius: var(--sb-radius-md);
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.2s;
                    flex-shrink: 0;
                    box-shadow: 0 2px 8px rgba(0, 122, 255, 0.25);
                }
                
                @media (max-width: 640px) {
                    .sb-send-btn {
                        width: 40px;
                        height: 40px;
                        min-width: 40px;
                    }
                }
                
                .sb-send-btn:hover:not(:disabled) {
                    box-shadow: 0 4px 12px rgba(0, 122, 255, 0.35);
                    transform: translateY(-1px);
                }
                
                .sb-send-btn:active:not(:disabled) { transform: scale(0.96); }
                .sb-send-btn:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }
                
                .sb-send-btn svg {
                    width: 19px;
                    height: 19px;
                    stroke: white;
                    fill: none;
                    stroke-width: 2.5;
                }
                
                @media (max-width: 640px) {
                    .sb-send-btn svg {
                        width: 18px;
                        height: 18px;
                    }
                }
                
                .sb-spinner { animation: sb-spin 0.8s linear infinite; }
                @keyframes sb-spin { to { transform: rotate(360deg); } }
                
                .sb-typing {
                    display: flex;
                    gap: 6px;
                    padding: 14px 18px;
                    background: var(--sb-bg-secondary);
                    border-radius: 16px;
                    border-bottom-left-radius: 5px;
                    width: fit-content;
                    border: 1px solid var(--sb-border-light);
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
                }
                
                @media (max-width: 640px) {
                    .sb-typing { padding: 12px 16px; }
                }
                
                .sb-typing span {
                    width: 8px;
                    height: 8px;
                    background: var(--sb-text-tertiary);
                    border-radius: 50%;
                    animation: sb-typing-dot 1.4s infinite ease-in-out both;
                }
                
                .sb-typing span:nth-child(1) { animation-delay: -0.32s; }
                .sb-typing span:nth-child(2) { animation-delay: -0.16s; }
                
                @keyframes sb-typing-dot {
                    0%, 80%, 100% {
                        transform: scale(0.5);
                        opacity: 0.5;
                    }
                    40% {
                        transform: scale(1);
                        opacity: 1;
                    }
                }
                
                .sb-message code {
                    background: var(--sb-bg-tertiary);
                    padding: 3px 6px;
                    border-radius: 4px;
                    font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
                    font-size: 12px;
                    border: 1px solid var(--sb-border-light);
                }
                
                .sb-message strong {
                    font-weight: 600;
                    color: var(--sb-text-primary);
                }
                
                .sb-message ul, .sb-message ol {
                    margin: 8px 0;
                    padding-left: 20px;
                }
                
                .sb-message li { margin: 5px 0; }
            `;
        }
    }

    class UIManager {
        constructor() {
            this.isOpen = false;
            this.isLoading = false;
            this.elements = {};
            this.cache = new CacheManager();
            this.api = new APIClient();
            this.scraper = new ProductScraper();
            this.currentData = null;
            
            this.init();
        }
        
        init() {
            StyleManager.inject();
            this.createBubble();
            this.createWindow();
            this.bindEvents();
        }
        
        createBubble() {
            const bubble = document.createElement("div");
            bubble.id = "sb-bubble";
            bubble.title = "ShopBuddy Assistant";
            bubble.innerHTML = `
                <svg viewBox="0 0 24 24">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                </svg>
            `;
            document.body.appendChild(bubble);
            this.elements.bubble = bubble;
        }
        
        createWindow() {
            const win = document.createElement("div");
            win.id = "sb-window";
            
            win.innerHTML = `
                <div class="sb-titlebar">
                    <div class="sb-traffic">
                        <button class="sb-traffic-close" id="sb-close" title="Close"></button>
                        <button class="sb-traffic-min" title="Minimize"></button>
                        <button class="sb-traffic-max" title="Maximize"></button>
                    </div>
                    <div class="sb-title-content">
                        <p class="sb-title-text">ShopBuddy</p>
                        <p class="sb-title-subtitle" id="sb-status">Ready</p>
                    </div>
                    <div class="sb-title-actions">
                        <button class="sb-action-btn" id="sb-refresh" title="Refresh">
                            <svg viewBox="0 0 24 24">
                                <path d="M23 4v6h-6M1 20v-6h6"/>
                                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <div class="sb-messages" id="sb-messages"></div>
                
                <div class="sb-quick-actions" id="sb-actions"></div>
                
                <div class="sb-input-area">
                    <input 
                        type="text" 
                        class="sb-input" 
                        id="sb-input" 
                        placeholder="Ask about products..." 
                        autocomplete="off"
                    >
                    <button class="sb-send-btn" id="sb-send" title="Send">
                        <svg viewBox="0 0 24 24">
                            <path d="M5 12h14M12 5l7 7-7 7"/>
                        </svg>
                    </button>
                </div>
            `;
            
            document.body.appendChild(win);
            
            this.elements.window = win;
            this.elements.messages = document.getElementById("sb-messages");
            this.elements.input = document.getElementById("sb-input");
            this.elements.send = document.getElementById("sb-send");
            this.elements.close = document.getElementById("sb-close");
            this.elements.refresh = document.getElementById("sb-refresh");
            this.elements.status = document.getElementById("sb-status");
            this.elements.actions = document.getElementById("sb-actions");
        }
        
        bindEvents() {
            this.elements.bubble.addEventListener("click", () => this.toggle());
            this.elements.close.addEventListener("click", () => this.close());
            this.elements.refresh.addEventListener("click", () => this.refresh());
            this.elements.send.addEventListener("click", () => this.send());
            
            this.elements.input.addEventListener("keypress", (e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    this.send();
                }
            });
            
            this.elements.actions.addEventListener("click", (e) => {
                const btn = e.target.closest(".sb-quick-btn");
                if (btn?.dataset.cmd) {
                    this.elements.input.value = btn.dataset.cmd;
                    this.send();
                }
            });
            
            document.addEventListener("keydown", (e) => {
                if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === "s") {
                    e.preventDefault();
                    this.toggle();
                }
                if (e.key === "Escape" && this.isOpen) {
                    this.close();
                }
            });
        }
        
        toggle() {
            this.isOpen ? this.close() : this.open();
        }
        
        open() {
            this.isOpen = true;
            this.elements.window.classList.add("open");
            setTimeout(() => {
                this.loadData();
                this.elements.input.focus();
            }, 100);
        }
        
        close() {
            this.isOpen = false;
            this.elements.window.classList.remove("open");
        }
        
        refresh() {
            this.elements.messages.innerHTML = "";
            this.cache.clear();
            this.loadData();
        }
        
        loadData() {
            this.currentData = this.scraper.scrape();
            this.updateStatus();
            this.updateActions();
            
            if (this.elements.messages.children.length === 0) {
                this.showWelcome();
            }
        }
        
        updateStatus() {
            if (!this.currentData) return;
            const { site, meta } = this.currentData;
            const itemText = meta.count === 1 ? "item" : "items";
            this.elements.status.textContent = `${site.name} - ${meta.count} ${itemText}`;
        }
        
        updateActions() {
            if (!this.currentData) return;
            
            const { meta, page } = this.currentData;
            const actions = [];
            
            if (meta.count > 0) {
                actions.push({ label: "Show All", cmd: "show all products" });
                actions.push({ label: "Best Deals", cmd: "best deals" });
                actions.push({ label: "Cheapest", cmd: "cheapest products" });
                actions.push({ label: "Top Rated", cmd: "top rated" });
            }
            
            if (page.type === PageType.PRODUCT) {
                actions.push({ label: "Analyze", cmd: "analyze this product" });
            }
            
            actions.push({ label: "Help", cmd: "help" });
            
            this.elements.actions.innerHTML = actions
                .map(a => `<button class="sb-quick-btn" data-cmd="${a.cmd}">${a.label}</button>`)
                .join("");
        }
        
        showWelcome() {
            if (!this.currentData) return;
            
            const { site, page, meta } = this.currentData;
            let content = '';
            
            if (page.type === PageType.HOMEPAGE && meta.count === 0) {
                content = this.buildCard({
                    icon: '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
                    title: 'Welcome',
                    rows: [
                        { label: 'Site', value: site.name },
                        { label: 'Page', value: 'Homepage' }
                    ],
                    footer: 'Search for products to get personalized recommendations'
                });
            } else if (page.type === PageType.PRODUCT) {
                const product = this.currentData.items[0];
                const rows = product ? [
                    { label: 'Product', value: product.name.slice(0, 40) + '...' },
                    ...(product.price ? [{ label: 'Price', value: product.price, valueStyle: 'color: var(--sb-green)' }] : [])
                ] : [];
                
                content = this.buildCard({
                    icon: '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>',
                    title: 'Product Page',
                    rows: rows,
                    footer: 'Ask me anything about this product'
                });
            } else {
                content = this.buildCard({
                    icon: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>',
                    title: 'Ready to Help',
                    rows: [
                        { label: 'Site', value: site.name },
                        { label: 'Products Found', value: meta.count, badge: true }
                    ],
                    footer: meta.count > 0 
                        ? 'Ask me to find deals, compare items, or get recommendations'
                        : 'No products found. Try scrolling down or searching for something',
                    footerWarning: meta.count === 0
                });
            }
            
            this.addMessage(content, "bot");
        }
        
        buildCard({ icon, title, rows, footer, footerWarning = false }) {
            const rowsHtml = rows.map(row => {
                if (row.badge) {
                    return `
                        <div class="sb-card-row">
                            <span class="sb-card-label">${row.label}</span>
                            <span class="sb-badge">${row.value}</span>
                        </div>
                    `;
                }
                return `
                    <div class="sb-card-row">
                        <span class="sb-card-label">${row.label}</span>
                        <span class="sb-card-value" ${row.valueStyle ? `style="${row.valueStyle}"` : ''}>${row.value}</span>
                    </div>
                `;
            }).join('');
            
            return `
                <div class="sb-card">
                    <div class="sb-card-header">
                        <div class="sb-card-icon">
                            <svg viewBox="0 0 24 24">${icon}</svg>
                        </div>
                        <span class="sb-card-title">${title}</span>
                    </div>
                    <div class="sb-card-body">${rowsHtml}</div>
                    ${footer ? `<div class="sb-card-footer ${footerWarning ? 'warning' : ''}">${footer}</div>` : ''}
                </div>
            `;
        }
        
        addMessage(content, type = "bot") {
            const div = document.createElement("div");
            div.className = `sb-message sb-message-${type}`;
            
            if (type === "bot" && !content.includes("<div")) {
                content = content
                    .replace(/\n/g, "<br>")
                    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                    .replace(/\*(.*?)\*/g, "<em>$1</em>")
                    .replace(/`(.*?)`/g, "<code>$1</code>");
            }
            
            div.innerHTML = content;
            this.elements.messages.appendChild(div);
            this.scrollToBottom();
        }
        
        scrollToBottom() {
            this.elements.messages.scrollTo({
                top: this.elements.messages.scrollHeight,
                behavior: "smooth"
            });
        }
        
        showTyping() {
            const div = document.createElement("div");
            div.className = "sb-typing";
            div.id = "sb-typing";
            div.innerHTML = "<span></span><span></span><span></span>";
            this.elements.messages.appendChild(div);
            this.scrollToBottom();
        }
        
        hideTyping() {
            document.getElementById("sb-typing")?.remove();
        }
        
        setLoading(loading) {
            this.isLoading = loading;
            this.elements.input.disabled = loading;
            this.elements.send.disabled = loading;
            
            const svg = loading ? `
                <svg class="sb-spinner" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" stroke-opacity="0.25" fill="none" stroke="currentColor" stroke-width="2.5"/>
                    <path d="M12 2a10 10 0 0 1 10 10" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
                </svg>
            ` : `
                <svg viewBox="0 0 24 24">
                    <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
            `;
            
            this.elements.send.innerHTML = svg;
        }
        
        async send() {
            const text = this.elements.input.value.trim();
            if (!text || this.isLoading) return;
            
            this.addMessage(text, "user");
            this.elements.input.value = "";
            
            this.setLoading(true);
            this.showTyping();
            
            try {
                const cacheKey = this.cache.generateKey(text, window.location.href);
                let response = this.cache.get(cacheKey);
                
                if (!response) {
                    this.currentData = this.scraper.scrape();
                    response = await this.api.send(text, this.currentData);
                    this.cache.set(cacheKey, response);
                }
                
                this.hideTyping();
                this.addMessage(response.answer || "I couldn't process that request. Please try again.", "bot");
                
            } catch (error) {
                this.hideTyping();
                this.addMessage(this.buildCard({
                    icon: '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
                    title: 'Connection Error',
                    rows: [],
                    footer: 'Unable to connect to the server. Please make sure the backend is running.',
                    footerWarning: true
                }), "bot");
            }
            
            this.setLoading(false);
            this.elements.input.focus();
        }
    }

    window.ShopBuddy = new UIManager();
    
})();