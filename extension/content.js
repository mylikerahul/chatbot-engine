// content.js - ShopBuddy AI with macOS Glass UI
(function() {
    "use strict";
    
    // Prevent multiple injections
    if (window.ShopBuddyInjected) return;
    window.ShopBuddyInjected = true;

    // ============================================
    // CONFIGURATION
    // ============================================
    
    const CONFIG = {
        API_URL: "http://127.0.0.1:8080/chat",
        VERSION: "4.0.0",
        MAX_ITEMS: 50,
        CACHE_DURATION: 5 * 60 * 1000 // 5 minutes
    };

    // ============================================
    // SITE SELECTORS
    // ============================================
    
    const SITE_SELECTORS = {
        "amazon": {
            name: "Amazon",
            icon: "🛒",
            category: "ecommerce",
            containers: ['[data-component-type="s-search-result"]', '.s-result-item[data-asin]'],
            title: ["h2 span", ".a-text-normal", "h2 a span"],
            price: [".a-price .a-offscreen", ".a-price-whole"],
            rating: [".a-icon-star-small .a-icon-alt", ".a-icon-alt"]
        },
        "flipkart": {
            name: "Flipkart",
            icon: "🛍️",
            category: "ecommerce",
            containers: ["._1AtVbE", "._2kHMtA", "[data-id]", "._4ddWXP"],
            title: ["._4rR01T", ".s1Q9rs", ".IRpwTa", "._2WkVRV", ".KzDlHZ"],
            price: ["._30jeq3", "._1_WHN1", "._25b18c"],
            rating: ["._3LWZlK"]
        },
        "imdb": {
            name: "IMDB",
            icon: "🎬",
            category: "movies",
            containers: ["li.ipc-metadata-list-summary-item", ".lister-item", ".ipc-poster-card"],
            title: ["h3.ipc-title__text", ".lister-item-header a"],
            price: ["span.cli-title-metadata-item", ".lister-item-year"],
            rating: ["span.ipc-rating-star--rating", ".ratings-imdb-rating strong"]
        },
        "goodreads": {
            name: "Goodreads",
            icon: "📚",
            category: "books",
            containers: [".bookalike", "tr[itemtype*='Book']"],
            title: ["a.bookTitle", "span[itemprop='name']"],
            price: ["a.authorName"],
            rating: [".minirating", ".staticStars"]
        }
    };

    // ============================================
    // CACHE CLASS
    // ============================================
    
    class Cache {
        constructor() {
            this.store = new Map();
        }
        
        get(key) {
            const item = this.store.get(key);
            if (!item) return null;
            if (Date.now() - item.timestamp > CONFIG.CACHE_DURATION) {
                this.store.delete(key);
                return null;
            }
            return item.data;
        }
        
        set(key, data) {
            this.store.set(key, { data, timestamp: Date.now() });
        }
    }

    // ============================================
    // SCRAPER CLASS
    // ============================================
    
    class Scraper {
        static detectSite() {
            const host = window.location.hostname.toLowerCase().replace("www.", "");
            
            for (const [key, config] of Object.entries(SITE_SELECTORS)) {
                if (host.includes(key)) {
                    return { key, ...config };
                }
            }
            
            return {
                key: "generic",
                name: "Website",
                icon: "🌐",
                category: "general",
                containers: ["article", ".product", ".card", ".item", "[class*='product']"],
                title: ["h1", "h2", "h3", "a"],
                price: ['[class*="price"]', '[data-price]'],
                rating: ['[class*="rating"]', '[class*="star"]']
            };
        }

        static scrape() {
            const site = this.detectSite();
            const items = [];

            for (const containerSel of site.containers) {
                const containers = document.querySelectorAll(containerSel);
                
                if (containers.length < 2) continue;

                containers.forEach((el, i) => {
                    let name = "", price = "", rating = "";

                    // Extract title
                    for (const sel of site.title) {
                        const titleEl = el.querySelector(sel);
                        if (titleEl) {
                            const text = titleEl.textContent?.trim() || titleEl.getAttribute("alt") || "";
                            if (text.length > 2) {
                                name = text.replace(/^\d+\.\s*/, "");
                                break;
                            }
                        }
                    }

                    // Extract price
                    for (const sel of site.price) {
                        const priceEl = el.querySelector(sel);
                        if (priceEl) {
                            price = priceEl.textContent?.trim() || "";
                            if (price) break;
                        }
                    }

                    // Extract rating
                    for (const sel of site.rating) {
                        const ratingEl = el.querySelector(sel);
                        if (ratingEl) {
                            rating = ratingEl.textContent?.trim().split("/")[0] || "";
                            if (rating) break;
                        }
                    }

                    if (name && name.length > 2 && name.length < 200) {
                        items.push({
                            id: i + 1,
                            name: name.slice(0, 120),
                            price: price.slice(0, 50),
                            rating: rating.slice(0, 20),
                            type: site.category
                        });
                    }
                });

                if (items.length > 0) break;
            }

            // Remove duplicates
            const uniqueItems = [];
            const seen = new Set();
            
            for (const item of items) {
                const key = item.name.toLowerCase();
                if (!seen.has(key)) {
                    seen.add(key);
                    uniqueItems.push(item);
                }
            }

            return {
                siteName: `${site.icon} ${site.name}`,
                siteCategory: site.category,
                items: uniqueItems.slice(0, CONFIG.MAX_ITEMS),
                url: window.location.href,
                title: document.title
            };
        }
    }

    // ============================================
    // API CLIENT CLASS
    // ============================================
    
    class APIClient {
        static async send(query) {
            const data = Scraper.scrape();

            const response = await fetch(CONFIG.API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query: query,
                    products: data.items,
                    page_url: data.url,
                    page_title: data.title,
                    site_type: data.siteName,
                    page_type: data.siteCategory
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            return response.json();
        }
    }

    // ============================================
    // UI MANAGER CLASS
    // ============================================
    
    class UIManager {
        constructor() {
            this.isOpen = false;
            this.elements = {};
            this.cache = new Cache();
            this.init();
        }

        init() {
            this.createBubble();
            this.createChatWindow();
            this.bindEvents();
        }

        createBubble() {
            const bubble = document.createElement("div");
            bubble.id = "sb-bubble";
            bubble.innerHTML = `<span id="sb-bubble-icon">🤖</span>`;
            bubble.setAttribute("title", "Open ShopBuddy AI (Ctrl+Shift+S)");
            document.body.appendChild(bubble);
            this.elements.bubble = bubble;
        }

        createChatWindow() {
            const chat = document.createElement("div");
            chat.id = "sb-chat";
            chat.innerHTML = `
                <!-- Header -->
                <header class="sb-header">
                    <div class="sb-window-controls">
                        <button class="sb-control-btn sb-control-close" id="sb-close" title="Close"></button>
                        <button class="sb-control-btn sb-control-minimize" title="Minimize"></button>
                        <button class="sb-control-btn sb-control-maximize" title="Maximize"></button>
                    </div>
                    <div class="sb-header-content">
                        <h3 class="sb-header-title">
                            ShopBuddy AI
                            <span class="sb-version-badge">v${CONFIG.VERSION}</span>
                        </h3>
                        <div class="sb-header-status">
                            <span class="sb-status-dot"></span>
                            <span id="sb-status-text">Ready</span>
                        </div>
                    </div>
                    <div class="sb-header-spacer"></div>
                </header>
                
                <!-- Messages -->
                <main class="sb-messages" id="sb-messages"></main>
                
                <!-- Quick Actions -->
                <div class="sb-quick-actions" id="sb-quick-actions"></div>
                
                <!-- Input Area -->
                <footer class="sb-input-area">
                    <input 
                        type="text" 
                        class="sb-input-field" 
                        id="sb-input" 
                        placeholder="Ask anything..." 
                        autocomplete="off"
                        spellcheck="false"
                    >
                    <button class="sb-send-btn" id="sb-send" title="Send message">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                            <path d="M5 12h14M12 5l7 7-7 7"/>
                        </svg>
                    </button>
                </footer>
            `;
            
            document.body.appendChild(chat);
            
            // Store element references
            this.elements.chat = chat;
            this.elements.messages = document.getElementById("sb-messages");
            this.elements.input = document.getElementById("sb-input");
            this.elements.send = document.getElementById("sb-send");
            this.elements.close = document.getElementById("sb-close");
            this.elements.status = document.getElementById("sb-status-text");
            this.elements.quickActions = document.getElementById("sb-quick-actions");
        }

        bindEvents() {
            // Toggle chat
            this.elements.bubble.addEventListener("click", () => this.toggle());
            
            // Close chat
            this.elements.close.addEventListener("click", () => this.close());
            
            // Send message
            this.elements.send.addEventListener("click", () => this.handleSend());
            
            // Enter to send
            this.elements.input.addEventListener("keypress", (e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    this.handleSend();
                }
            });

            // Quick action buttons (event delegation)
            this.elements.quickActions.addEventListener("click", (e) => {
                const btn = e.target.closest(".sb-quick-btn");
                if (btn) {
                    const cmd = btn.getAttribute("data-cmd");
                    if (cmd) {
                        this.elements.input.value = cmd;
                        this.handleSend();
                    }
                }
            });

            // Keyboard shortcut: Ctrl/Cmd + Shift + S
            document.addEventListener("keydown", (e) => {
                if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === "s") {
                    e.preventDefault();
                    this.toggle();
                }
            });
            
            // Close on Escape
            document.addEventListener("keydown", (e) => {
                if (e.key === "Escape" && this.isOpen) {
                    this.close();
                }
            });
        }

        toggle() {
            this.isOpen = !this.isOpen;
            this.elements.chat.classList.toggle("open", this.isOpen);
            
            if (this.isOpen) {
                // Delay to allow animation to start
                setTimeout(() => {
                    const data = Scraper.scrape();
                    this.updateStatus(data);
                    this.updateQuickActions(data);
                    
                    // Show welcome only if no messages
                    if (this.elements.messages.children.length === 0) {
                        this.showWelcome(data);
                    }
                    
                    this.elements.input.focus();
                }, 100);
            }
        }

        close() {
            this.isOpen = false;
            this.elements.chat.classList.remove("open");
        }

        updateStatus(data) {
            const itemText = data.items.length === 1 ? "item" : "items";
            this.elements.status.textContent = `${data.siteName} • ${data.items.length} ${itemText}`;
        }

        updateQuickActions(data) {
            const actions = [];
            
            if (data.items.length > 0) {
                actions.push({ label: "📋 Show All", cmd: "show all items" });
                actions.push({ label: "⭐ Best Rated", cmd: "best rated" });
                
                if (data.siteCategory === "ecommerce") {
                    actions.push({ label: "💰 Cheapest", cmd: "cheapest items" });
                    actions.push({ label: "📊 Compare", cmd: "compare top 3" });
                }
            }
            
            actions.push({ label: "❓ Help", cmd: "help" });
            
            this.elements.quickActions.innerHTML = actions.map(a => 
                `<button class="sb-quick-btn" data-cmd="${a.cmd}">${a.label}</button>`
            ).join("");
        }

        showWelcome(data) {
            const html = `
                <div class="sb-welcome-card">
                    <h4>👋 Welcome to ShopBuddy</h4>
                    <p>
                        <strong>Site:</strong> ${data.siteName}
                        ${data.siteCategory ? `(${data.siteCategory})` : ""}<br>
                        <strong>Items Found:</strong> ${data.items.length}
                    </p>
                </div>
            `;
            this.addMessage(html, "bot");
        }

        addMessage(text, type) {
            const div = document.createElement("div");
            
            // Set appropriate class
            switch(type) {
                case "user":
                    div.className = "sb-msg-user";
                    break;
                case "bot":
                    div.className = "sb-msg-bot";
                    break;
                case "system":
                    div.className = "sb-msg-system";
                    break;
                default:
                    div.className = "sb-msg-bot";
            }
            
            // Format text for bot messages (if not HTML)
            if (type === "bot" && !text.includes("<div")) {
                text = text
                    .replace(/\n/g, "<br>")
                    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                    .replace(/\*(.*?)\*/g, "<em>$1</em>")
                    .replace(/`(.*?)`/g, "<code>$1</code>");
            }
            
            div.innerHTML = text;
            this.elements.messages.appendChild(div);
            
            // Smooth scroll to bottom
            this.elements.messages.scrollTo({
                top: this.elements.messages.scrollHeight,
                behavior: "smooth"
            });
        }

        showTyping() {
            const div = document.createElement("div");
            div.className = "sb-typing-indicator";
            div.id = "sb-typing";
            div.innerHTML = "<span></span><span></span><span></span>";
            this.elements.messages.appendChild(div);
            
            this.elements.messages.scrollTo({
                top: this.elements.messages.scrollHeight,
                behavior: "smooth"
            });
        }

        hideTyping() {
            const el = document.getElementById("sb-typing");
            if (el) el.remove();
        }

        setLoading(loading) {
            this.elements.input.disabled = loading;
            this.elements.send.disabled = loading;
            
            if (loading) {
                this.elements.send.innerHTML = `
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="animation: spin 1s linear infinite;">
                        <circle cx="12" cy="12" r="10" stroke-opacity="0.3"/>
                        <path d="M12 2a10 10 0 0 1 10 10"/>
                    </svg>
                    <style>@keyframes spin { to { transform: rotate(360deg); } }</style>
                `;
            } else {
                this.elements.send.innerHTML = `
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <path d="M5 12h14M12 5l7 7-7 7"/>
                    </svg>
                `;
            }
        }

        async handleSend() {
            const text = this.elements.input.value.trim();
            if (!text) return;

            // Add user message
            this.addMessage(text, "user");
            this.elements.input.value = "";
            
            // Set loading state
            this.setLoading(true);
            this.showTyping();

            try {
                // Check cache first
                const cacheKey = `${text}:${window.location.href}`;
                let response = this.cache.get(cacheKey);

                if (!response) {
                    response = await APIClient.send(text);
                    this.cache.set(cacheKey, response);
                }

                this.hideTyping();
                this.addMessage(response.answer || "No response received.", "bot");
                
            } catch (error) {
                console.error("ShopBuddy Error:", error);
                this.hideTyping();
                this.addMessage(
                    "⚠️ **Connection Error**\n\nCouldn't connect to the server. Make sure it's running:\n\n`python main.py`",
                    "bot"
                );
            }

            // Reset loading state
            this.setLoading(false);
            this.elements.input.focus();
        }
    }

    // ============================================
    // INITIALIZE
    // ============================================
    
    // Log initialization
    console.log(
        `%c🤖 ShopBuddy AI v${CONFIG.VERSION}`,
        "color: #007aff; font-size: 14px; font-weight: 600;"
    );
    console.log(
        "%cPress Ctrl+Shift+S (⌘+Shift+S on Mac) to toggle",
        "color: #6b7280; font-size: 11px;"
    );

    // Initialize UI
    new UIManager();
    
})();