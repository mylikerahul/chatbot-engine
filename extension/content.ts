interface Product {
    id: number;
    name: string;
    price: string;
    rating: string;
    type: string;
}

interface SiteConfig {
    name: string;
    icon: string;
    category: string;
    containers: string[];
    title: string[];
    price: string[];
    rating: string[];
}

class Scraper {
    static detectSite(): SiteConfig {
        // Logic implementation...
        return {} as SiteConfig;
    }

    static scrape(): { items: Product[] } {

        return { items: [] };
    }
}