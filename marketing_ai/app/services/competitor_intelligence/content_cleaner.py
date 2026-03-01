from bs4 import BeautifulSoup

class ContentCleaner:
    """
    Cleans raw HTML by ripping out non-semantic noise (Navbars, Footers, JS, CSS).
    Focuses entirely on extracting value propositions, headlines, CTAs, and pricing strings.
    """
    
    @staticmethod
    def clean_html(raw_html: str) -> str:
        """Strip tags, scripts, styles, navs, and footers."""
        if not raw_html:
            return ""

        soup = BeautifulSoup(raw_html, "html.parser")

        # 1. Remove obvious noise
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "iframe"]):
            element.decompose()

        # 2. Rip out any div explicitly labelled nav/menu/footer
        for unwanted in soup.find_all(lambda tag: tag.has_attr('class') and any(
                c in ' '.join(tag['class']).lower() for c in ['nav', 'menu', 'footer', 'cookie', 'popup'])):
            unwanted.decompose()

        # 3. Extract purely semantic text (Headlines + paragraphs + lists)
        semantic_tags = ["h1", "h2", "h3", "h4", "p", "li", "span", "strong", "b", "div"]
        chunks = []
        for tag in soup.find_all(semantic_tags):
            text = tag.get_text(strip=True)
            if text and len(text) > 10:  # Ignore tiny 1-2 word UI blips unless semantic
                chunks.append(text)

        # 4. Join remaining semantic blocks with newlines
        clean_text = "\n".join(chunks)
        
        # Trim excess whitespace
        clean_text = "\n".join([line.strip() for line in clean_text.splitlines() if line.strip()])
        return clean_text
