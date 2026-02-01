(function() {
    "use strict";
    
    if (window.ShopBuddyInjected) return;
    window.ShopBuddyInjected = true;

    const CONFIG = {
        API_URL: "http://127.0.0.1:8080/chat",
        VERSION: "4.0.0",
        MAX_ITEMS: 50,
        DEBOUNCE_MS: 300
    };

    const SITE_SELECTORS = {
        "amazon": {
            name: "Amazon",
            category: "ecommerce",
            containers: ['[data-component-type="s-search-result"]'],
            title: ["h2 span", ".a-text-normal"],
            price: [".a-price .a-offscreen"],
            rating: [".a-icon-star-small .a-icon-alt"]
        },
        "flipkart": {
            name: "Flipkart",
            category: "ecommerce",
            containers: ["._1AtVbE", "[data-id]"],
            title: ["._4rR01T", ".s1Q9rs", ".KzDlHZ"],
            price: ["._30jeq3"],
            rating: ["._3LWZlK"]
        },
        "imdb": {
            name: "IMDB",
            category: "movies",
            containers: ["li.ipc-metadata-list-summary-item", ".lister-item"],
            title: ["h3.ipc-title__text", ".lister-item-header a"],
            price: ["span.cli-title-metadata-item", ".lister-item-year"],
            rating: ["span.ipc-rating-star--rating", ".ratings-imdb-rating strong"]
        },
        "goodreads": {
            name: "Goodreads",
            category: "books",
            containers: [".bookalike", "tr[itemtype*='Book']"],
            title: ["a.bookTitle", "span[itemprop='name']"],
            price: ["a.authorName"],
            rating: [".minirating", ".staticStars"]
        }
    };

    class UIManager {
        constructor() {
            this.isOpen = false;
            this.elements = {};
            this.init();
        }

        init() {
            this.injectStyles();
            this.createBubble();
            this.createChatWindow();
            this.bindEvents();
        }

        injectStyles() {
            const style = document.createElement("style");
            style.textContent = `
                #sb-bubble{position:fixed;bottom:24px;right:24px;width:60px;height:60px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:50%;cursor:pointer;box-shadow:0 4px 20px rgba(99,102,241,0.4);display:flex;align-items:center;justify-content:center;z-index:2147483647;font-size:24px;transition:transform 0.2s}
                #sb-bubble:hover{transform:scale(1.1)}
                #sb-chat{position:fixed;bottom:96px;right:24px;width:380px;height:520px;background:#fff;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,0.2);z-index:2147483646;display:none;flex-direction:column;overflow:hidden;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif}
                #sb-chat.open{display:flex}
                .sb-header{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;padding:16px;display:flex;justify-content:space-between;align-items:center}
                .sb-header h3{margin:0;font-size:16px}
                .sb-close{background:rgba(255,255,255,0.2);border:none;color:#fff;width:28px;height:28px;border-radius:50%;cursor:pointer;font-size:16px}
                .sb-msgs{flex:1;overflow-y:auto;padding:16px;background:#f5f7fa;display:flex;flex-direction:column;gap:10px}
                .sb-user{align-self:flex-end;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;padding:10px 14px;border-radius:16px 16px 4px 16px;max-width:80%;font-size:14px}
                .sb-bot{align-self:flex-start;background:#fff;color:#1e293b;padding:12px 16px;border-radius:16px 16px 16px 4px;max-width:85%;font-size:14px;border:1px solid #e2e8f0;line-height:1.6}
                .sb-bot strong{color:#6366f1}
                .sb-sys{align-self:center;background:#e2e8f0;color:#475569;padding:6px 14px;border-radius:16px;font-size:12px}
                .sb-input-wrap{padding:14px;background:#fff;border-top:1px solid #e5e7eb;display:flex;gap:10px}
                .sb-input{flex:1;padding:12px 16px;border:2px solid #e5e7eb;border-radius:24px;font-size:14px;outline:none}
                .sb-input:focus{border-color:#6366f1}
                .sb-send{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;border:none;width:44px;height:44px;border-radius:50%;cursor:pointer;font-size:16px}
                .sb-send:disabled{opacity:0.5}
                .sb-typing{display:flex;gap:4px;padding:10px 14px;background:#fff;border-radius:16px;align-self:flex-start}
                .sb-typing span{width:8px;height:8px;background:#6366f1;border-radius:50%;animation:bounce 1.4s infinite ease-in-out}
                .sb-typing span:nth-child(2){animation-delay:0.2s}
                .sb-typing span:nth-child(3){animation-delay:0.4s}
                @keyframes bounce{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-8px)}}
            `;
            document.head.appendChild(style);
        }

        createBubble() {
            const bubble = document.createElement("div");
            bubble.id = "sb-bubble";
            bubble.textContent = "AI";
            document.body.appendChild(bubble);
            this.elements.bubble = bubble;
        }

        createChatWindow() {
            const chat = document.createElement("div");
            chat.id = "sb-chat";
            chat.innerHTML = `
                <div class="sb-header">
                    <h3>ShopBuddy AI</h3>
                    <button class="sb-close" id="sb-close">x</button>
                </div>
                <div class="sb-msgs" id="sb-msgs"></div>
                <div class="sb-input-wrap">
                    <input class="sb-input" id="sb-input" placeholder="Ask anything...">
                    <button class="sb-send" id="sb-send">Go</button>
                </div>
            `;
            document.body.appendChild(chat);
            
            this.elements.chat = chat;
            this.elements.msgs = document.getElementById("sb-msgs");
            this.elements.input = document.getElementById("sb-input");
            this.elements.send = document.getElementById("sb-send");
            this.elements.close = document.getElementById("sb-close");
        }

        bindEvents() {
            this.elements.bubble.addEventListener("click", () => this.toggle());
            this.elements.close.addEventListener("click", () => this.close());
            this.elements.send.addEventListener("click", () => this.handleSend());
            this.elements.input.addEventListener("keypress", (e) => {
                if (e.key === "Enter") this.handleSend();
            });
        }

        toggle() {
            this.isOpen = !this.isOpen;
            this.elements.chat.classList.toggle("open", this.isOpen);
            
            if (this.isOpen) {
                const data = Scraper.scrape();
                this.addMessage(`Site: ${data.siteName} | Items: ${data.items.length}`, "sys");
                this.elements.input.focus();
            }
        }

        close() {
            this.isOpen = false;
            this.elements.chat.classList.remove("open");
        }

        addMessage(text, type) {
            const div = document.createElement("div");
            div.className = `sb-${type}`;
            div.innerHTML = text
                .replace(/\n/g, "<br>")
                .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
            this.elements.msgs.appendChild(div);
            this.elements.msgs.scrollTop = this.elements.msgs.scrollHeight;
        }

        showTyping() {
            const div = document.createElement("div");
            div.className = "sb-typing";
            div.id = "sb-typing";
            div.innerHTML = "<span></span><span></span><span></span>";
            this.elements.msgs.appendChild(div);
            this.elements.msgs.scrollTop = this.elements.msgs.scrollHeight;
        }

        hideTyping() {
            const el = document.getElementById("sb-typing");
            if (el) el.remove();
        }

        setLoading(loading) {
            this.elements.input.disabled = loading;
            this.elements.send.disabled = loading;
        }

        async handleSend() {
            const text = this.elements.input.value.trim();
            if (!text) return;

            this.addMessage(text, "user");
            this.elements.input.value = "";
            this.setLoading(true);
            this.showTyping();

            try {
                const response = await APIClient.send(text);
                this.hideTyping();
                this.addMessage(response.answer || "No response", "bot");
            } catch (error) {
                this.hideTyping();
                this.addMessage("Connection error. Check if server is running.", "sys");
            }

            this.setLoading(false);
            this.elements.input.focus();
        }
    }

    class Scraper {
        static detectSite() {
            const host = window.location.hostname.toLowerCase();
            
            for (const [key, config] of Object.entries(SITE_SELECTORS)) {
                if (host.includes(key)) {
                    return { key, ...config };
                }
            }
            
            return {
                key: "generic",
                name: "Website",
                category: "general",
                containers: ["article", ".product", ".card", ".item"],
                title: ["h2", "h3", "a"],
                price: ['[class*="price"]'],
                rating: ['[class*="rating"]']
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

                    for (const sel of site.title) {
                        const titleEl = el.querySelector(sel);
                        if (titleEl && titleEl.textContent.trim()) {
                            name = titleEl.textContent.trim().replace(/^\d+\.\s*/, "");
                            break;
                        }
                    }

                    for (const sel of site.price) {
                        const priceEl = el.querySelector(sel);
                        if (priceEl) {
                            price = priceEl.textContent.trim();
                            break;
                        }
                    }

                    for (const sel of site.rating) {
                        const ratingEl = el.querySelector(sel);
                        if (ratingEl) {
                            rating = ratingEl.textContent.trim().split("/")[0];
                            break;
                        }
                    }

                    if (name && name.length > 2) {
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

            const uniqueItems = [];
            const seen = new Set();
            
            for (const item of items) {
                if (!seen.has(item.name)) {
                    seen.add(item.name);
                    uniqueItems.push(item);
                }
            }

            return {
                siteName: site.name,
                siteCategory: site.category,
                items: uniqueItems.slice(0, CONFIG.MAX_ITEMS),
                url: window.location.href,
                title: document.title
            };
        }
    }

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

    new UIManager();
})();