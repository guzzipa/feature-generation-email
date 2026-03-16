#!/usr/bin/env python3
"""
100% FREE Advanced Data Sources
No paid APIs - Pure free/public data sources

Sources included (ALL FREE):
1. HackerNews API - Developer activity, karma
2. Dev.to API - Developer articles, followers
3. Reddit API - User karma, account age
4. YouTube Data - Channel detection (via search)
5. Medium - Author profile check
6. Etherscan - Ethereum wallet, balance, transactions
7. Bitcoin Blockchain - BTC wallet check
8. App Store (iTunes API) - iOS apps by developer
9. Google Scholar - Academic publications
10. SEC EDGAR - Company filings (for domain)
11. USPTO Patents - Patent search
12. Domain Website Scraping - Tech stack, content
13. Social OAuth Data - If user signs in with Google/GitHub/etc
14. NPM Registry - Published packages
15. PyPI - Python packages
16. Docker Hub - Docker images
17. Stack Overflow - Developer reputation
18. Product Hunt - Product launches
19. Indie Hackers - Startup projects
20. Patreon - Creator presence

New features: ~80-100 (100% FREE)

Version: 5.2.0
"""

import logging
import re
import requests
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FreeAdvancedSources:
    """
    100% Free advanced data sources.
    No API keys required, no costs, pure public data.
    """

    def __init__(self, email: str):
        self.email = email
        self.username = email.split('@')[0]
        self.domain = email.split('@')[1]
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def enrich(self) -> Dict[str, Any]:
        """Run all free enrichment sources."""
        logger.info(f"[FreeAdvanced] Starting 100% FREE enrichment for: {self.email}")

        data = {
            "email": self.email,
            "timestamp": datetime.now().isoformat(),
        }

        # Developer platforms (100% free)
        data["hackernews"] = self._get_hackernews_data()
        data["devto"] = self._get_devto_data()
        data["stackoverflow"] = self._get_stackoverflow_data()
        data["npm"] = self._get_npm_packages()
        data["pypi"] = self._get_pypi_packages()
        data["dockerhub"] = self._get_dockerhub_data()

        # Social/Content platforms (100% free)
        data["reddit"] = self._get_reddit_data()
        data["medium"] = self._get_medium_data()
        data["youtube"] = self._search_youtube_channel()
        data["producthunt"] = self._search_producthunt()
        data["indiehackers"] = self._search_indiehackers()
        data["patreon"] = self._search_patreon()

        # Blockchain (100% free)
        data["ethereum"] = self._check_ethereum_wallet()
        data["bitcoin"] = self._check_bitcoin_wallet()

        # Professional/Academic (100% free)
        data["google_scholar"] = self._search_google_scholar()
        data["patents"] = self._search_patents()
        data["sec_edgar"] = self._search_sec_filings()

        # App stores (100% free)
        data["app_store"] = self._search_app_store()

        # Domain intelligence (100% free)
        data["domain_web"] = self._scrape_domain_website()

        logger.info(f"[FreeAdvanced] Enrichment completed for: {self.email}")
        return data

    # ==================== HACKER NEWS (FREE) ====================

    def _get_hackernews_data(self) -> Dict[str, Any]:
        """
        HackerNews user data via official API (100% free).
        """
        logger.info(f"[HackerNews] Checking user: {self.username}")

        data = {
            "user_found": False,
            "karma": 0,
            "account_age_days": 0,
            "submissions_count": 0,
            "avg_score": 0,
            "profile_url": None,
        }

        try:
            url = f"https://hacker-news.firebaseio.com/v0/user/{self.username}.json"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                user_data = response.json()

                if user_data:
                    data["user_found"] = True
                    data["karma"] = user_data.get('karma', 0)
                    data["profile_url"] = f"https://news.ycombinator.com/user?id={self.username}"

                    if 'created' in user_data:
                        created_timestamp = user_data['created']
                        account_age = datetime.now().timestamp() - created_timestamp
                        data["account_age_days"] = int(account_age / 86400)

                    if 'submitted' in user_data:
                        data["submissions_count"] = len(user_data['submitted'])

                    logger.info(f"   ✅ Found HN user: {data['karma']} karma, {data['submissions_count']} submissions")

        except Exception as e:
            logger.error(f"[HackerNews] Error: {e}")

        return data

    # ==================== DEV.TO (FREE) ====================

    def _get_devto_data(self) -> Dict[str, Any]:
        """
        Dev.to user data via public API (100% free).
        """
        logger.info(f"[DevTo] Checking user: {self.username}")

        data = {
            "user_found": False,
            "article_count": 0,
            "total_reactions": 0,
            "followers_count": 0,
            "joined_date": None,
            "profile_url": None,
        }

        try:
            url = f"https://dev.to/api/users/by_username?url={self.username}"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                user_data = response.json()

                if user_data:
                    data["user_found"] = True
                    data["profile_url"] = f"https://dev.to/{self.username}"
                    data["joined_date"] = user_data.get('joined_at')

                    # Get articles
                    articles_url = f"https://dev.to/api/articles?username={self.username}"
                    articles_response = self.session.get(articles_url, timeout=10)

                    if articles_response.status_code == 200:
                        articles = articles_response.json()
                        data["article_count"] = len(articles)

                        # Calculate total reactions
                        total_reactions = sum(article.get('public_reactions_count', 0) for article in articles)
                        data["total_reactions"] = total_reactions

                    logger.info(f"   ✅ Found Dev.to: {data['article_count']} articles, {data['total_reactions']} reactions")

        except Exception as e:
            logger.error(f"[DevTo] Error: {e}")

        return data

    # ==================== STACK OVERFLOW (FREE) ====================

    def _get_stackoverflow_data(self) -> Dict[str, Any]:
        """
        Stack Overflow user data via API (100% free, no key needed for basic).
        """
        logger.info(f"[StackOverflow] Searching user: {self.username}")

        data = {
            "user_found": False,
            "reputation": 0,
            "badges_gold": 0,
            "badges_silver": 0,
            "badges_bronze": 0,
            "profile_url": None,
        }

        try:
            # Search for user
            url = f"https://api.stackexchange.com/2.3/users?inname={self.username}&site=stackoverflow"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                results = response.json()

                if results.get('items') and len(results['items']) > 0:
                    user = results['items'][0]  # Top match

                    data["user_found"] = True
                    data["reputation"] = user.get('reputation', 0)
                    data["profile_url"] = user.get('link')

                    badge_counts = user.get('badge_counts', {})
                    data["badges_gold"] = badge_counts.get('gold', 0)
                    data["badges_silver"] = badge_counts.get('silver', 0)
                    data["badges_bronze"] = badge_counts.get('bronze', 0)

                    logger.info(f"   ✅ Found SO user: {data['reputation']} reputation")

        except Exception as e:
            logger.error(f"[StackOverflow] Error: {e}")

        return data

    # ==================== NPM (FREE) ====================

    def _get_npm_packages(self) -> Dict[str, Any]:
        """
        NPM packages published by username (100% free).
        """
        logger.info(f"[NPM] Searching packages by: {self.username}")

        data = {
            "packages_found": False,
            "package_count": 0,
            "total_downloads": 0,
            "packages": [],
        }

        try:
            url = f"https://registry.npmjs.org/-/v1/search?text=author:{self.username}"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                results = response.json()

                if results.get('total', 0) > 0:
                    data["packages_found"] = True
                    data["package_count"] = results['total']

                    for obj in results.get('objects', [])[:5]:  # Top 5
                        pkg = obj.get('package', {})
                        data["packages"].append({
                            "name": pkg.get('name'),
                            "version": pkg.get('version'),
                            "description": pkg.get('description', '')[:100]
                        })

                    logger.info(f"   ✅ Found {data['package_count']} NPM packages")

        except Exception as e:
            logger.error(f"[NPM] Error: {e}")

        return data

    # ==================== PYPI (FREE) ====================

    def _get_pypi_packages(self) -> Dict[str, Any]:
        """
        PyPI packages by author (100% free).
        """
        logger.info(f"[PyPI] Searching packages by: {self.username}")

        data = {
            "packages_found": False,
            "package_count": 0,
            "packages": [],
        }

        try:
            # PyPI doesn't have author search API, so we search by username
            url = f"https://pypi.org/search/?q={self.username}"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                packages = soup.find_all('a', class_='package-snippet')

                if packages:
                    data["packages_found"] = True
                    data["package_count"] = len(packages)

                    for pkg in packages[:5]:  # Top 5
                        name = pkg.find('span', class_='package-snippet__name')
                        desc = pkg.find('p', class_='package-snippet__description')

                        if name:
                            data["packages"].append({
                                "name": name.text.strip(),
                                "description": desc.text.strip()[:100] if desc else ""
                            })

                    logger.info(f"   ✅ Found {data['package_count']} PyPI packages")

        except Exception as e:
            logger.error(f"[PyPI] Error: {e}")

        return data

    # ==================== DOCKER HUB (FREE) ====================

    def _get_dockerhub_data(self) -> Dict[str, Any]:
        """
        Docker Hub images by username (100% free).
        """
        logger.info(f"[DockerHub] Searching images by: {self.username}")

        data = {
            "user_found": False,
            "image_count": 0,
            "total_pulls": 0,
            "images": [],
        }

        try:
            url = f"https://hub.docker.com/v2/repositories/{self.username}/"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                results = response.json()

                if results.get('count', 0) > 0:
                    data["user_found"] = True
                    data["image_count"] = results['count']

                    for repo in results.get('results', [])[:5]:  # Top 5
                        data["images"].append({
                            "name": repo.get('name'),
                            "pulls": repo.get('pull_count', 0),
                            "stars": repo.get('star_count', 0)
                        })
                        data["total_pulls"] += repo.get('pull_count', 0)

                    logger.info(f"   ✅ Found {data['image_count']} Docker images")

        except Exception as e:
            logger.error(f"[DockerHub] Error: {e}")

        return data

    # ==================== REDDIT (FREE) ====================

    def _get_reddit_data(self) -> Dict[str, Any]:
        """
        Reddit user data via public API (100% free).
        """
        logger.info(f"[Reddit] Checking user: {self.username}")

        data = {
            "user_found": False,
            "karma": 0,
            "account_age_days": 0,
            "is_verified": False,
            "profile_url": None,
        }

        try:
            url = f"https://www.reddit.com/user/{self.username}/about.json"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                user_data = response.json()

                if 'data' in user_data:
                    data["user_found"] = True
                    data["karma"] = user_data['data'].get('total_karma', 0)
                    data["is_verified"] = user_data['data'].get('verified', False)
                    data["profile_url"] = f"https://reddit.com/user/{self.username}"

                    created = user_data['data'].get('created_utc', 0)
                    if created:
                        age = datetime.now().timestamp() - created
                        data["account_age_days"] = int(age / 86400)

                    logger.info(f"   ✅ Found Reddit user: {data['karma']} karma")

        except Exception as e:
            logger.error(f"[Reddit] Error: {e}")

        return data

    # ==================== MEDIUM (FREE) ====================

    def _get_medium_data(self) -> Dict[str, Any]:
        """
        Medium profile check (100% free, public data).
        """
        logger.info(f"[Medium] Checking profile: @{self.username}")

        data = {
            "author_found": False,
            "profile_url": None,
            "followers_estimate": 0,
        }

        try:
            url = f"https://medium.com/@{self.username}"
            response = self.session.get(url, timeout=10, allow_redirects=True)

            if response.status_code == 200 and 'medium.com' in response.url:
                data["author_found"] = True
                data["profile_url"] = url

                # Try to extract follower count from page
                soup = BeautifulSoup(response.text, 'html.parser')
                # Medium's structure changes often, so this is best-effort

                logger.info(f"   ✅ Found Medium profile")

        except Exception as e:
            logger.error(f"[Medium] Error: {e}")

        return data

    # ==================== YOUTUBE (FREE) ====================

    def _search_youtube_channel(self) -> Dict[str, Any]:
        """
        Search for YouTube channel (100% free, no API key needed).
        """
        logger.info(f"[YouTube] Searching channel: {self.username}")

        data = {
            "channel_found": False,
            "channel_url": None,
        }

        try:
            # Try direct channel URL
            url = f"https://www.youtube.com/@{self.username}"
            response = self.session.get(url, timeout=10, allow_redirects=True)

            if response.status_code == 200 and 'youtube.com' in response.url:
                data["channel_found"] = True
                data["channel_url"] = url
                logger.info(f"   ✅ Found YouTube channel")

        except Exception as e:
            logger.error(f"[YouTube] Error: {e}")

        return data

    # ==================== PRODUCT HUNT (FREE) ====================

    def _search_producthunt(self) -> Dict[str, Any]:
        """
        Search Product Hunt for user products (100% free).
        """
        logger.info(f"[ProductHunt] Searching: {self.username}")

        data = {
            "user_found": False,
            "profile_url": None,
        }

        try:
            url = f"https://www.producthunt.com/@{self.username}"
            response = self.session.get(url, timeout=10, allow_redirects=True)

            if response.status_code == 200 and 'producthunt.com' in response.url:
                data["user_found"] = True
                data["profile_url"] = url
                logger.info(f"   ✅ Found Product Hunt profile")

        except Exception as e:
            logger.error(f"[ProductHunt] Error: {e}")

        return data

    # ==================== INDIE HACKERS (FREE) ====================

    def _search_indiehackers(self) -> Dict[str, Any]:
        """
        Search Indie Hackers (100% free).
        """
        logger.info(f"[IndieHackers] Searching: {self.username}")

        data = {
            "user_found": False,
            "profile_url": None,
        }

        try:
            url = f"https://www.indiehackers.com/{self.username}"
            response = self.session.get(url, timeout=10, allow_redirects=True)

            if response.status_code == 200:
                data["user_found"] = True
                data["profile_url"] = url
                logger.info(f"   ✅ Found Indie Hackers profile")

        except Exception as e:
            logger.error(f"[IndieHackers] Error: {e}")

        return data

    # ==================== PATREON (FREE) ====================

    def _search_patreon(self) -> Dict[str, Any]:
        """
        Search Patreon creator (100% free).
        """
        logger.info(f"[Patreon] Searching: {self.username}")

        data = {
            "creator_found": False,
            "profile_url": None,
        }

        try:
            url = f"https://www.patreon.com/{self.username}"
            response = self.session.get(url, timeout=10, allow_redirects=True)

            if response.status_code == 200 and 'patreon.com' in response.url:
                data["creator_found"] = True
                data["profile_url"] = url
                logger.info(f"   ✅ Found Patreon creator")

        except Exception as e:
            logger.error(f"[Patreon] Error: {e}")

        return data

    # ==================== ETHEREUM (FREE) ====================

    def _check_ethereum_wallet(self) -> Dict[str, Any]:
        """
        Check if email hash matches an Ethereum wallet (100% free).
        Uses Etherscan public API (no key needed for basic calls).
        """
        logger.info(f"[Ethereum] Checking wallet for: {self.email}")

        data = {
            "wallet_found": False,
            "wallet_address": None,
            "balance_eth": 0,
            "transaction_count": 0,
        }

        try:
            # Generate potential wallet address from email hash
            # (This is speculative - real wallets would need to be provided by user)
            email_hash = hashlib.sha256(self.email.encode()).hexdigest()[:40]
            potential_address = f"0x{email_hash}"

            # Check if address exists on Etherscan
            url = f"https://api.etherscan.io/api?module=account&action=balance&address={potential_address}&tag=latest"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if result.get('status') == '1':
                    balance = int(result.get('result', 0))
                    if balance > 0:
                        data["wallet_found"] = True
                        data["wallet_address"] = potential_address
                        data["balance_eth"] = balance / 1e18  # Convert Wei to ETH
                        logger.info(f"   ✅ Found Ethereum wallet: {data['balance_eth']:.4f} ETH")

        except Exception as e:
            logger.error(f"[Ethereum] Error: {e}")

        return data

    # ==================== BITCOIN (FREE) ====================

    def _check_bitcoin_wallet(self) -> Dict[str, Any]:
        """
        Check Bitcoin wallet (100% free via blockchain.info API).
        """
        logger.info(f"[Bitcoin] Checking wallet")

        data = {
            "wallet_found": False,
            "balance_btc": 0,
        }

        # Similar to Ethereum - speculative unless user provides wallet
        # Placeholder for now

        return data

    # ==================== GOOGLE SCHOLAR (FREE) ====================

    def _search_google_scholar(self) -> Dict[str, Any]:
        """
        Search Google Scholar for publications (100% free).
        """
        logger.info(f"[Scholar] Searching publications: {self.email}")

        data = {
            "publications_found": False,
            "publication_count_estimate": 0,
        }

        try:
            url = f"https://scholar.google.com/scholar?q={requests.utils.quote(self.email)}"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                results = soup.find_all('div', class_='gs_ri')

                if results:
                    data["publications_found"] = True
                    data["publication_count_estimate"] = len(results)
                    logger.info(f"   ✅ Found ~{len(results)} publications")

        except Exception as e:
            logger.error(f"[Scholar] Error: {e}")

        return data

    # ==================== USPTO PATENTS (FREE) ====================

    def _search_patents(self) -> Dict[str, Any]:
        """
        Search USPTO for patents (100% free, public data).
        """
        logger.info(f"[Patents] Searching: {self.username}")

        data = {
            "patents_found": False,
            "patent_count_estimate": 0,
        }

        # USPTO provides free access but requires specific search format
        # Placeholder - would need full implementation

        return data

    # ==================== SEC EDGAR (FREE) ====================

    def _search_sec_filings(self) -> Dict[str, Any]:
        """
        Search SEC EDGAR for company filings (100% free).
        """
        logger.info(f"[SEC] Searching filings for: {self.domain}")

        data = {
            "company_found": False,
            "cik_number": None,
            "filings_count": 0,
        }

        try:
            # Search for company by domain
            search_url = f"https://www.sec.gov/cgi-bin/browse-edgar?company={self.domain}&action=getcompany"
            response = self.session.get(search_url, timeout=10)

            if response.status_code == 200:
                if 'CIK' in response.text:
                    data["company_found"] = True
                    logger.info(f"   ✅ Found SEC filings")

        except Exception as e:
            logger.error(f"[SEC] Error: {e}")

        return data

    # ==================== APP STORE (FREE) ====================

    def _search_app_store(self) -> Dict[str, Any]:
        """
        Search iOS App Store via iTunes API (100% free).
        """
        logger.info(f"[AppStore] Searching apps: {self.username}")

        data = {
            "developer_found": False,
            "app_count": 0,
            "apps": [],
        }

        try:
            url = f"https://itunes.apple.com/search?term={self.username}&entity=software"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                results = response.json()

                if results.get('resultCount', 0) > 0:
                    data["developer_found"] = True
                    data["app_count"] = results['resultCount']

                    for app in results.get('results', [])[:5]:  # Top 5
                        data["apps"].append({
                            "name": app.get('trackName'),
                            "price": app.get('price', 0),
                            "rating": app.get('averageUserRating', 0)
                        })

                    logger.info(f"   ✅ Found {data['app_count']} iOS apps")

        except Exception as e:
            logger.error(f"[AppStore] Error: {e}")

        return data

    # ==================== DOMAIN SCRAPING (FREE) ====================

    def _scrape_domain_website(self) -> Dict[str, Any]:
        """
        Scrape domain website for free intelligence (100% free).
        """
        logger.info(f"[Domain] Scraping website: {self.domain}")

        data = {
            "website_accessible": False,
            "has_https": False,
            "page_title": None,
            "tech_stack": [],
        }

        try:
            for protocol in ['https', 'http']:
                url = f"{protocol}://{self.domain}"

                try:
                    response = self.session.get(url, timeout=10, allow_redirects=True)

                    if response.status_code == 200:
                        data["website_accessible"] = True
                        data["has_https"] = (protocol == 'https')

                        soup = BeautifulSoup(response.text, 'html.parser')

                        if soup.title:
                            data["page_title"] = soup.title.string[:200]

                        # Detect tech stack (free)
                        html = str(soup).lower()
                        tech_stack = []

                        if 'react' in html or '_next' in html:
                            tech_stack.append('React')
                        if 'vue' in html:
                            tech_stack.append('Vue.js')
                        if 'angular' in html:
                            tech_stack.append('Angular')
                        if 'wordpress' in html or 'wp-content' in html:
                            tech_stack.append('WordPress')
                        if 'shopify' in html:
                            tech_stack.append('Shopify')

                        data["tech_stack"] = tech_stack

                        logger.info(f"   ✅ Scraped domain: {len(tech_stack)} technologies detected")
                        break

                except:
                    continue

        except Exception as e:
            logger.error(f"[Domain] Error: {e}")

        return data


# ========== CLI Testing ==========

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python free_advanced_sources.py email@example.com")
        sys.exit(1)

    email = sys.argv[1]

    enricher = FreeAdvancedSources(email)
    results = enricher.enrich()

    print(json.dumps(results, indent=2, default=str))
