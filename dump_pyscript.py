from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge")
        page = browser.new_page()
        page.goto("http://127.0.0.1:5000/cours/Informatique/Variables_Python")
        
        # Wait for PyScript to initialize
        time.sleep(5)
        
        # Check if login is required
        if "Connexion" in page.title():
            page.fill("input[name='email']", "alice@ecole.fr")
            page.fill("input[name='password']", "password123")
            page.click("button[type='submit']")
            page.wait_for_load_state('networkidle')
            time.sleep(3)
            # Re-navigate to the course because login redirects to dashboard
            page.goto("http://127.0.0.1:5000/cours/Informatique/Variables_Python")
        
        # Wait 10 seconds unconditionally for PyScript to load
        time.sleep(10)
        
        # Serialize entire DOM including shadow roots
        js_code = """
        () => {
            function serializeTree(node) {
                let result = '';
                if (node.nodeType === 3) return node.textContent;
                if (node.nodeType !== 1) return '';
                
                result += `<${node.tagName.toLowerCase()}`;
                for (let attr of node.attributes) {
                    result += ` ${attr.name}="${attr.value}"`;
                }
                result += '>';
                
                if (node.shadowRoot) {
                    result += '\\n<SHADOW-ROOT>\\n';
                    for (let child of node.shadowRoot.childNodes) {
                        result += serializeTree(child);
                    }
                    result += '\\n</SHADOW-ROOT>\\n';
                }
                
                for (let child of node.childNodes) {
                    result += serializeTree(child);
                }
                result += `</${node.tagName.toLowerCase()}>\n`;
                return result;
            }
            return serializeTree(document.body);
        }
        """
        html = page.evaluate(js_code)
        
        with open("pyscript_dom_dump.txt", "w", encoding="utf-8") as f:
            f.write(html)
            
        print("DOM dumped successfully to pyscript_dom_dump.txt")
        browser.close()

if __name__ == "__main__":
    run()
