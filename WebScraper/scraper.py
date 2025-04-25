import os
import time
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class AdvancedWebScraper:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Web Scraper")
        self.root.geometry("900x700")
        self.dark_mode = False
        self.driver = None
        self.scraped_data = ""
        
        # Configure styles
        self.style = ttk.Style()
        self.configure_styles()
        
        # Create main container
        self.create_main_frame()
        self.create_url_section()
        self.create_options_section()
        self.create_output_section()
        self.create_button_panel()
        self.create_status_bar()
        
        # Set grid weights
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(4, weight=1)
        
    def configure_styles(self):
        """Configure light and dark mode styles"""
        self.style.configure('TFrame', background='white')
        self.style.configure('TLabel', background='white', foreground='black')
        self.style.configure('TButton', background='#f0f0f0', foreground='black')
        self.style.configure('TEntry', fieldbackground='white', foreground='black')
        self.style.configure('TRadiobutton', background='white', foreground='black')
        self.style.configure('TCheckbutton', background='white', foreground='black')
        self.style.configure('Dark.TFrame', background='#2d2d2d')
        self.style.configure('Dark.TLabel', background='#2d2d2d', foreground='white')
        self.style.configure('Dark.TButton', background='#4d4d4d', foreground='white')
        
    def create_main_frame(self):
        """Create the main container frame"""
        self.main_frame = ttk.Frame(self.root, padding="15")
        self.main_frame.pack(fill=BOTH, expand=True)
        
    def create_url_section(self):
        """Create URL input section"""
        url_frame = ttk.Frame(self.main_frame)
        url_frame.grid(row=0, column=0, columnspan=3, sticky=EW, pady=(0, 15))
        
        ttk.Label(url_frame, text="Website URL:").pack(side=LEFT, padx=(0, 10))
        self.url_entry = ttk.Entry(url_frame, width=70)
        self.url_entry.pack(side=LEFT, expand=True, fill=X)
        self.url_entry.insert(0, "https://www.example.com")
        
    def create_options_section(self):
        """Create scraping options section"""
        options_frame = ttk.LabelFrame(self.main_frame, text="Scraping Options", padding=10)
        options_frame.grid(row=1, column=0, columnspan=3, sticky=EW, pady=(0, 15))
        
        # Scraping type selection
        self.scraping_type = StringVar(value="single")
        ttk.Radiobutton(options_frame, text="Single Page", 
                        variable=self.scraping_type, value="single").grid(row=0, column=0, sticky=W, padx=5)
        ttk.Radiobutton(options_frame, text="Multiple Pages", 
                        variable=self.scraping_type, value="multi").grid(row=0, column=1, sticky=W, padx=5)
        ttk.Radiobutton(options_frame, text="Infinite Scroll", 
                        variable=self.scraping_type, value="scroll").grid(row=0, column=2, sticky=W, padx=5)
        
        # Options for multiple pages
        self.pages_frame = ttk.Frame(options_frame)
        self.pages_frame.grid(row=1, column=0, columnspan=3, sticky=W, pady=(10, 0))
        ttk.Label(self.pages_frame, text="Pages to scrape:").pack(side=LEFT)
        self.pages_entry = ttk.Entry(self.pages_frame, width=5)
        self.pages_entry.pack(side=LEFT, padx=5)
        self.pages_entry.insert(0, "3")
        self.pages_frame.grid_remove()
        
        # Options for infinite scroll
        self.scroll_frame = ttk.Frame(options_frame)
        self.scroll_frame.grid(row=2, column=0, columnspan=3, sticky=W, pady=(10, 0))
        ttk.Label(self.scroll_frame, text="Scroll iterations:").pack(side=LEFT)
        self.scroll_entry = ttk.Entry(self.scroll_frame, width=5)
        self.scroll_entry.pack(side=LEFT, padx=5)
        self.scroll_entry.insert(0, "5")
        ttk.Label(self.scroll_frame, text="Wait time (sec):").pack(side=LEFT, padx=(10, 0))
        self.wait_entry = ttk.Entry(self.scroll_frame, width=5)
        self.wait_entry.pack(side=LEFT, padx=5)
        self.wait_entry.insert(0, "2")
        self.scroll_frame.grid_remove()
        
        # Bind radio button changes
        self.scraping_type.trace('w', self.update_options_visibility)
        
    def create_output_section(self):
        """Create output display section"""
        ttk.Label(self.main_frame, text="Scraped Content:").grid(row=2, column=0, sticky=W, pady=(0, 5))
        
        # Text widget with scrollbar
        self.output_text = Text(self.main_frame, wrap=WORD, width=100, height=25)
        self.output_text.grid(row=3, column=0, columnspan=3, sticky=NSEW)
        
        scrollbar = ttk.Scrollbar(self.main_frame, orient=VERTICAL, command=self.output_text.yview)
        scrollbar.grid(row=3, column=3, sticky=NS)
        self.output_text['yscrollcommand'] = scrollbar.set
        
    def create_button_panel(self):
        """Create control buttons panel"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=(15, 0), sticky=EW)
        
        # Scrape button
        self.scrape_btn = ttk.Button(button_frame, text="Start Scraping", command=self.start_scraping)
        self.scrape_btn.pack(side=LEFT, padx=5)
        
        # Save button
        self.save_btn = ttk.Button(button_frame, text="Save Results", state=DISABLED, command=self.save_results)
        self.save_btn.pack(side=LEFT, padx=5)
        
        # Dark mode toggle
        self.dark_mode_btn = ttk.Button(button_frame, text="Toggle Dark Mode", command=self.toggle_dark_mode)
        self.dark_mode_btn.pack(side=RIGHT, padx=5)
        
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_var = StringVar(value="Ready")
        status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=SUNKEN)
        status_bar.grid(row=6, column=0, columnspan=3, sticky=EW, pady=(15, 0))
        
    def update_options_visibility(self, *args):
        """Show/hide options based on selected scraping type"""
        self.pages_frame.grid_remove()
        self.scroll_frame.grid_remove()
        
        if self.scraping_type.get() == "multi":
            self.pages_frame.grid()
        elif self.scraping_type.get() == "scroll":
            self.scroll_frame.grid()
    
    def toggle_dark_mode(self):
        """Toggle between dark and light themes"""
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            # Dark theme colors
            bg_color = '#2d2d2d'
            fg_color = '#ffffff'
            entry_bg = '#3d3d3d'
            text_bg = '#3d3d3d'
            
            self.main_frame.configure(style='Dark.TFrame')
            self.output_text.config(bg=text_bg, fg=fg_color, insertbackground=fg_color)
            
            # Apply dark style to all widgets
            for widget in self.main_frame.winfo_children():
                if isinstance(widget, (ttk.Label, ttk.Button, ttk.Radiobutton)):
                    widget.configure(style='Dark.TLabel' if isinstance(widget, ttk.Label) else 'Dark.TButton')
        else:
            # Light theme colors
            bg_color = 'white'
            fg_color = 'black'
            entry_bg = 'white'
            text_bg = 'white'
            
            self.main_frame.configure(style='TFrame')
            self.output_text.config(bg=text_bg, fg=fg_color, insertbackground=fg_color)
            
            # Revert to default styles
            for widget in self.main_frame.winfo_children():
                if isinstance(widget, (ttk.Label, ttk.Button, ttk.Radiobutton)):
                    widget.configure(style='TLabel' if isinstance(widget, ttk.Label) else 'TButton')
    
    def initialize_driver(self):
        """Initialize Chrome WebDriver"""
        if self.driver:
            self.driver.quit()
            
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        
        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize browser: {str(e)}")
            return False
    
    def start_scraping(self):
        """Start the scraping process based on user selection"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a valid URL")
            return
            
        if not self.initialize_driver():
            return
            
        self.scraped_data = ""
        self.output_text.delete(1.0, END)
        self.save_btn.config(state=DISABLED)
        self.status_var.set("Initializing scraping...")
        self.root.update()
        
        try:
            scrape_type = self.scraping_type.get()
            
            if scrape_type == "single":
                self.scrape_single_page(url)
            elif scrape_type == "multi":
                self.scrape_multiple_pages(url)
            elif scrape_type == "scroll":
                self.scrape_infinite_scroll(url)
                
            self.status_var.set("Scraping completed successfully")
            self.save_btn.config(state=NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"Scraping failed: {str(e)}")
            self.status_var.set("Scraping failed")
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
    
    def scrape_single_page(self, url):
        """Scrape content from a single page"""
        self.status_var.set(f"Loading page: {url}")
        self.root.update()
        
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        self.process_page_content()
    
    def scrape_multiple_pages(self, url):
        """Scrape content from multiple pages with pagination"""
        try:
            pages = int(self.pages_entry.get())
            if pages < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of pages (≥1)")
            return
            
        base_url = url.split('?')[0] if '?' in url else url
        query = url.split('?')[1] if '?' in url else ""
        
        for page in range(1, pages + 1):
            self.status_var.set(f"Scraping page {page} of {pages}...")
            self.root.update()
            
            # Construct page URL (this may need adjustment for different websites)
            if query:
                page_url = f"{base_url}?{query}&page={page}"
            else:
                page_url = f"{base_url}?page={page}"
                
            self.driver.get(page_url)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            self.process_page_content(f"\n=== PAGE {page} ===\n")
            
            # Check if there's a next page (optional enhancement)
            # Could add logic to detect when we've reached the last page
    
    def scrape_infinite_scroll(self, url):
        """Scrape content from infinite scroll page"""
        try:
            scrolls = int(self.scroll_entry.get())
            wait_time = float(self.wait_entry.get())
            if scrolls < 1 or wait_time < 0.5:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter valid scroll settings (iterations ≥1, wait ≥0.5)")
            return
            
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for i in range(1, scrolls + 1):
            self.status_var.set(f"Scrolling ({i}/{scrolls}), current height: {last_height}px")
            self.root.update()
            
            # Scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(wait_time)
            
            # Calculate new scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                self.status_var.set(f"Stopped scrolling - no new content (iteration {i})")
                break
            last_height = new_height
        
        self.process_page_content("\n=== SCROLLED CONTENT ===\n")
    
    def process_page_content(self, prefix=""):
        """Extract and display structured content from current page"""
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        # Remove unwanted elements
        for tag in soup(['script', 'style', 'noscript', 'meta', 'link', 'svg']):
            tag.decompose()

        output_lines = [prefix] if prefix else []

        # Example structure: H1-H6, Paragraphs, and Links
        for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'a']):
            text = tag.get_text(strip=True)
            if not text:
                continue
            if tag.name.startswith('h'):
                level = int(tag.name[1])
                output_lines.append(f"{'#' * level} {text}")
            elif tag.name == 'p':
                output_lines.append(f"\n{text}\n")
            elif tag.name == 'a':
                href = tag.get('href')
                output_lines.append(f"[{text}]({href})")

        structured_text = '\n'.join(output_lines)
        self.scraped_data += structured_text + "\n"
        self.output_text.insert(END, structured_text + "\n")
        self.output_text.see(END)
        self.root.update()

    
    def save_results(self):
        """Save scraped content to a file"""
        if not self.scraped_data.strip():
            messagebox.showwarning("Warning", "No content to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save Scraped Content"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.scraped_data)
                messagebox.showinfo("Success", f"Content saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

if __name__ == "__main__":
    root = Tk()
    app = AdvancedWebScraper(root)
    root.mainloop()