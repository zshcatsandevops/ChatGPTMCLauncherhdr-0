import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import json
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import hashlib
import ssl
import requests  # Added for dynamic Java version fetching

# Define constants for directories and URLs
CATCLIENT_DIR = os.path.expanduser("~/.catclient")
VERSIONS_DIR = os.path.join(CATCLIENT_DIR, "versions")
JAVA_DIR = os.path.expanduser("~/.catclient/java")
VERSION_MANIFEST_URL = "https://launchermeta.mojang.com/mc/game/version_manifest.json"

# CatClientHDR theme colors - Fiery cat theme!
THEME = {
    'bg': '#1a1a2e',
    'sidebar': '#16213e',
    'accent': '#e94560',  # CatClient fiery red
    'accent_light': '#ff6b6b',
    'text': '#ffffff',
    'text_secondary': '#a8a8a8',
    'button': '#e94560',
    'button_hover': '#ff6b6b',
    'input_bg': '#0f3460',
    'header_bg': '#0a0e27',
    'tab_active': '#e94560',
    'tab_inactive': '#1a1a2e'
}

class CatClientHDRLauncher(tk.Tk):
    def __init__(self):
        """Initialize the CatClientHDR launcher window and UI."""
        super().__init__()
        self.title("CatClientHDR v1.0 🐱🔥")
        self.geometry("900x550")
        self.minsize(800, 500)
        self.configure(bg=THEME['bg'])
        self.versions = {}  # Dictionary to store version IDs and their URLs
        self.version_categories = {
            "Latest Release": [],
            "Latest Snapshot": [],
            "Release": [],
            "Snapshot": [],
            "Old Beta": [],
            "Old Alpha": []
        }
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles for CatClientHDR look
        self.style.configure("TFrame", background=THEME['bg'])
        self.style.configure("TLabel", background=THEME['bg'], foreground=THEME['text'])
        self.style.configure("TButton", 
                           background=THEME['button'],
                           foreground=THEME['text'],
                           borderwidth=0,
                           focuscolor='none')
        self.style.map("TButton",
                      background=[('active', THEME['button_hover']),
                                 ('pressed', THEME['accent'])])
        
        self.style.configure("TCombobox", 
                           fieldbackground=THEME['input_bg'],
                           background=THEME['input_bg'],
                           foreground=THEME['text'],
                           arrowcolor=THEME['text'],
                           borderwidth=0)
        
        self.style.configure("TScale", 
                           background=THEME['bg'],
                           troughcolor=THEME['input_bg'])
        
        self.style.configure("TNotebook", 
                           background=THEME['header_bg'],
                           borderwidth=0)
        self.style.configure("TNotebook.Tab", 
                           background=THEME['tab_inactive'],
                           foreground=THEME['text_secondary'],
                           padding=[15, 5],
                           borderwidth=0)
        self.style.map("TNotebook.Tab",
                      background=[('selected', THEME['tab_active'])],
                      foreground=[('selected', THEME['text'])])
        
        self.init_ui()

    def init_ui(self):
        """Set up the graphical user interface with CatClientHDR styling."""
        # Header
        header = tk.Frame(self, bg=THEME['header_bg'], height=40)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        # Header title with cat emoji
        title = tk.Label(header, text="🐱 CatClientHDR 🔥", font=("Arial", 14, "bold"), 
                        bg=THEME['header_bg'], fg=THEME['accent'])
        title.pack(side="left", padx=15, pady=10)
        
        # Header version
        version = tk.Label(header, text="v1.0", font=("Arial", 10), 
                          bg=THEME['header_bg'], fg=THEME['text_secondary'])
        version.pack(side="right", padx=15, pady=10)
        
        # Main container
        main_container = tk.Frame(self, bg=THEME['bg'])
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Left panel - Game settings
        left_panel = tk.Frame(main_container, bg=THEME['sidebar'], width=300)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)

        # Game version selection
        version_frame = tk.Frame(left_panel, bg=THEME['sidebar'])
        version_frame.pack(fill="x", padx=15, pady=15)
        
        tk.Label(version_frame, text="VERSION", font=("Arial", 9, "bold"), 
                bg=THEME['sidebar'], fg=THEME['text_secondary']).pack(anchor="w")
        
        self.category_combo = ttk.Combobox(version_frame, values=list(self.version_categories.keys()),
                                         state="readonly", font=("Arial", 10))
        self.category_combo.pack(fill="x", pady=(5, 0))
        self.category_combo.set("Latest Release")
        self.category_combo.bind("<<ComboboxSelected>>", self.update_version_list)

        self.version_combo = ttk.Combobox(version_frame, state="readonly", font=("Arial", 10))
        self.version_combo.pack(fill="x", pady=5)

        # Account settings
        account_frame = tk.Frame(left_panel, bg=THEME['sidebar'])
        account_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(account_frame, text="ACCOUNT", font=("Arial", 9, "bold"), 
                bg=THEME['sidebar'], fg=THEME['text_secondary']).pack(anchor="w")
        
        self.username_input = tk.Entry(account_frame, font=("Arial", 10), bg=THEME['input_bg'],
                                     fg=THEME['text'], insertbackground=THEME['text'], bd=0, relief="flat")
        self.username_input.pack(fill="x", pady=(5, 0))
        self.username_input.insert(0, "CatGamer")
        self.username_input.bind("<FocusIn>", lambda e: self.username_input.delete(0, tk.END) 
                               if self.username_input.get() == "CatGamer" else None)

        # RAM settings
        ram_frame = tk.Frame(left_panel, bg=THEME['sidebar'])
        ram_frame.pack(fill="x", padx=15, pady=10)
        
        ram_header = tk.Frame(ram_frame, bg=THEME['sidebar'])
        ram_header.pack(fill="x")
        
        tk.Label(ram_header, text="RAM", font=("Arial", 9, "bold"),
                bg=THEME['sidebar'], fg=THEME['text_secondary']).pack(side="left")
        
        self.ram_value_label = tk.Label(ram_header, text="4 GB", font=("Arial", 9),
                                      bg=THEME['sidebar'], fg=THEME['text'])
        self.ram_value_label.pack(side="right")

        self.ram_scale = tk.Scale(ram_frame, from_=1, to=16, orient="horizontal",
                                bg=THEME['sidebar'], fg=THEME['text'],
                                activebackground=THEME['accent'],
                                highlightthickness=0, bd=0,
                                troughcolor=THEME['input_bg'],
                                sliderrelief="flat",
                                command=lambda v: self.ram_value_label.config(text=f"{int(float(v))} GB"))
        self.ram_scale.set(4)
        self.ram_scale.pack(fill="x")

        # Skin button
        skin_button = tk.Button(left_panel, text="🎨 Change Skin", font=("Arial", 10),
                              bg=THEME['button'], fg=THEME['text'],
                              bd=0, padx=20, pady=8, command=self.select_skin)
        skin_button.pack(padx=15, pady=10, fill="x")

        # Launch button
        launch_button = tk.Button(left_panel, text="🚀 PLAY NOW", font=("Arial", 12, "bold"),
                                bg=THEME['accent'], fg=THEME['text'],
                                bd=0, padx=20, pady=12, command=self.prepare_and_launch)
        launch_button.pack(side="bottom", padx=15, pady=15, fill="x")

        # Right panel - Tabs and content
        right_panel = tk.Frame(main_container, bg=THEME['bg'])
        right_panel.pack(side="left", fill="both", expand=True)

        # Create notebook for tabs
        notebook = ttk.Notebook(right_panel)
        notebook.pack(fill="both", expand=True)

        # News tab
        news_tab = ttk.Frame(notebook)
        notebook.add(news_tab, text="News")

        # Versions tab
        versions_tab = ttk.Frame(notebook)
        notebook.add(versions_tab, text="Versions")

        # Settings tab
        settings_tab = ttk.Frame(notebook)
        notebook.add(settings_tab, text="Settings")

        # Populate news tab with CatClientHDR content
        news_content = tk.Frame(news_tab, bg=THEME['bg'])
        news_content.pack(fill="both", expand=True, padx=10, pady=10)

        # News title
        news_title = tk.Label(news_content, text="🐱 CATCLIENTHDR - MEOW EDITION 🔥", 
                             font=("Arial", 16, "bold"), bg=THEME['bg'], fg=THEME['accent'])
        news_title.pack(anchor="w", pady=(0, 15))

        # News items with cat-themed messaging
        news_items = [
            "🐾 Custom Minecraft Launcher with fiery cat-powered interface",
            "🎮 Support for all Minecraft versions (even the ancient ones!)",
            "☕ Automatic Java installation - no hairballs included",
            "🎨 Easy skin changing - dress your cat character",
            "⚡ Optimized performance settings for smooth gameplay",
            "🪶 Lightweight and fast - purrs along nicely",
            "🔄 Regular updates and improvements from the cat crew",
            "🔥 SAMSOFT CO powered technology"
        ]

        for item in news_items:
            item_frame = tk.Frame(news_content, bg=THEME['bg'])
            item_frame.pack(fill="x", pady=2)
            tk.Label(item_frame, text=item, font=("Arial", 10),
                    bg=THEME['bg'], fg=THEME['text'], justify="left", anchor="w").pack(fill='x')

        # Version list in versions tab
        versions_content = tk.Frame(versions_tab, bg=THEME['bg'])
        versions_content.pack(fill="both", expand=True, padx=10, pady=10)

        versions_title = tk.Label(versions_content, text="AVAILABLE VERSIONS", 
                                 font=("Arial", 12, "bold"), bg=THEME['bg'], fg=THEME['text'])
        versions_title.pack(anchor="w", pady=(0, 10))

        # Version listbox
        version_list_frame = tk.Frame(versions_content, bg=THEME['bg'])
        version_list_frame.pack(fill="both", expand=True)

        # Scrollbar for version list
        scrollbar = ttk.Scrollbar(version_list_frame)
        scrollbar.pack(side="right", fill="y")

        self.version_listbox = tk.Listbox(version_list_frame, bg=THEME['input_bg'], fg=THEME['text'],
                                        selectbackground=THEME['accent'], selectforeground=THEME['text'],
                                        yscrollcommand=scrollbar.set, font=("Arial", 10), bd=0)
        self.version_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.version_listbox.yview)

        # Settings tab content
        settings_content = tk.Frame(settings_tab, bg=THEME['bg'])
        settings_content.pack(fill="both", expand=True, padx=10, pady=10)

        settings_title = tk.Label(settings_content, text="CATCLIENTHDR SETTINGS", 
                                 font=("Arial", 12, "bold"), bg=THEME['bg'], fg=THEME['text'])
        settings_title.pack(anchor="w", pady=(0, 10))

        # Settings options
        settings_options = [
            ("Auto-update CatClientHDR", tk.BooleanVar(value=True)),
            ("Close launcher when game starts", tk.BooleanVar(value=False)),
            ("Keep launcher open (recommended)", tk.BooleanVar(value=True)),
            ("Check for Java updates", tk.BooleanVar(value=True)),
            ("Enable cat mode (extra meows)", tk.BooleanVar(value=True))
        ]

        for text, var in settings_options:
            cb = tk.Checkbutton(settings_content, text=text, variable=var,
                              bg=THEME['bg'], fg=THEME['text'], selectcolor=THEME['sidebar'],
                              activebackground=THEME['bg'], activeforeground=THEME['text'])
            cb.pack(anchor="w", pady=5)

        # Game directory setting
        dir_frame = tk.Frame(settings_content, bg=THEME['bg'])
        dir_frame.pack(fill="x", pady=10)

        tk.Label(dir_frame, text="Game Directory:", bg=THEME['bg'], fg=THEME['text']).pack(anchor="w")
        dir_entry = tk.Entry(dir_frame, bg=THEME['input_bg'], fg=THEME['text'], 
                           insertbackground=THEME['text'], bd=0)
        dir_entry.insert(0, CATCLIENT_DIR)
        dir_entry.pack(fill="x", pady=(5, 0))

        # Load versions after UI is initialized
        self.load_version_manifest()

    def update_version_list(self, event=None):
        """Update the version list based on the selected category."""
        category = self.category_combo.get()
        if self.version_categories[category]:
            self.version_combo['values'] = self.version_categories[category]
            self.version_combo.current(0)
        else:
            self.version_combo['values'] = []
            self.version_combo.set("")  # Clear selection if category is empty
            self.category_combo.set("Latest Release")  # Fallback to Latest Release
            if self.version_categories["Latest Release"]:
                self.version_combo['values'] = self.version_categories["Latest Release"]
                self.version_combo.current(0)
        
        # Update the listbox in versions tab
        self.version_listbox.delete(0, tk.END)
        for version in self.version_categories[category]:
            self.version_listbox.insert(tk.END, version)

    def load_version_manifest(self):
        """Load the list of available Minecraft versions from Mojang's servers."""
        try:
            # Create SSL context that handles certificate verification issues
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(
                VERSION_MANIFEST_URL,
                headers={
                    'User-Agent': 'CatClientHDR/1.0 (Minecraft Launcher)',
                    'Accept': 'application/json'
                }
            )
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as url:
                manifest = json.loads(url.read().decode())
                
                # Clear existing categories
                for category in self.version_categories:
                    self.version_categories[category] = []
                
                # Categorize versions
                latest_release = None
                latest_snapshot = None
                
                for v in manifest["versions"]:
                    self.versions[v["id"]] = v["url"]
                    
                    # Track latest versions
                    if v["id"] == manifest["latest"]["release"]:
                        latest_release = v["id"]
                        self.version_categories["Latest Release"].append(v["id"])
                    elif v["id"] == manifest["latest"]["snapshot"]:
                        latest_snapshot = v["id"]
                        self.version_categories["Latest Snapshot"].append(v["id"])
                    
                    # Categorize by type
                    if v["type"] == "release":
                        if v["id"] != latest_release:
                            self.version_categories["Release"].append(v["id"])
                    elif v["type"] == "snapshot":
                        if v["id"] != latest_snapshot:
                            self.version_categories["Snapshot"].append(v["id"])
                    elif v["type"] == "old_beta":
                        self.version_categories["Old Beta"].append(v["id"])
                    elif v["type"] == "old_alpha":
                        self.version_categories["Old Alpha"].append(v["id"])
                
                # Update the version combo box
                self.update_version_list()
                print("✅ CatClientHDR: Version manifest loaded successfully! 🐱")
                
        except urllib.error.URLError as e:
            print(f"❌ CatClientHDR: Network error loading version manifest: {e}")
            messagebox.showerror("CatClientHDR Error", 
                               f"Failed to load version manifest.\n\nNetwork Error: {str(e)}\n\nPlease check your internet connection and firewall settings.")
        except ssl.SSLError as e:
            print(f"❌ CatClientHDR: SSL error loading version manifest: {e}")
            messagebox.showerror("CatClientHDR Error", 
                               f"SSL verification failed.\n\nError: {str(e)}\n\nPlease check your internet connection.")
        except Exception as e:
            print(f"❌ CatClientHDR: Error loading version manifest: {e}")
            messagebox.showerror("CatClientHDR Error", 
                               f"Failed to load version manifest.\n\nError: {str(e)}\n\nPlease check your internet connection.")

    def get_latest_java_url(self):
        """Fetch the latest OpenJDK 21 release URL from Adoptium API."""
        try:
            response = requests.get("https://api.adoptium.net/v3/assets/latest/21/hotspot", timeout=10)
            response.raise_for_status()
            releases = response.json()
            system = platform.system()
            arch = "x64"
            os_map = {"Windows": "windows", "Linux": "linux", "Darwin": "mac"}
            os_name = os_map.get(system, None)
            if not os_name:
                return None, None
            for release in releases:
                if release["binary"]["os"] == os_name and release["binary"]["architecture"] == arch:
                    return release["binary"]["package"]["link"], release["version"]["openjdk_version"]
            return None, None
        except Exception as e:
            print(f"❌ CatClientHDR: Failed to fetch latest Java version: {e}")
            return None, None

    def is_java_installed(self, required_version="21"):
        """Check if a compatible Java version (21 or higher) is installed."""
        try:
            # First check system Java
            result = subprocess.run(["java", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = result.stderr
            match = re.search(r'version "(\d+)', output)
            if match:
                major_version = int(match.group(1))
                return major_version >= int(required_version)
        except Exception:
            pass
        
        # Check local Java installation
        try:
            java_bin = os.path.join(JAVA_DIR, self.get_local_java_dir(), "bin", "java.exe" if platform.system() == "Windows" else "java")
            if os.path.exists(java_bin):
                result = subprocess.run([java_bin, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                output = result.stderr
                match = re.search(r'version "(\d+)', output)
                if match:
                    major_version = int(match.group(1))
                    return major_version >= int(required_version)
            return False
        except Exception:
            return False

    def get_local_java_dir(self):
        """Find the extracted Java directory dynamically."""
        for dir_name in os.listdir(JAVA_DIR):
            if dir_name.startswith("jdk-") and os.path.isdir(os.path.join(JAVA_DIR, dir_name)):
                return dir_name
        return "jdk-21.0.5+11"  # Fallback to default if not found

    def install_java_if_needed(self):
        """Install the latest OpenJDK 21 if a compatible Java version is not found."""
        if self.is_java_installed():
            print("✅ CatClientHDR: Java is already installed!")
            return
        print("🐱 CatClientHDR: Installing OpenJDK 21... (meow)")
        java_url, java_version = self.get_latest_java_url()
        if not java_url:
            messagebox.showerror("CatClientHDR Error", "Unsupported OS or failed to fetch Java URL - this cat can't run here!")
            return

        archive_ext = "zip" if platform.system() == "Windows" else "tar.gz"
        archive_path = os.path.join(JAVA_DIR, f"openjdk.{archive_ext}")
        os.makedirs(JAVA_DIR, exist_ok=True)

        try:
            # Create SSL context that handles certificate verification issues
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(java_url, headers={'User-Agent': 'CatClientHDR/1.0'})
            with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
                with open(archive_path, 'wb') as out_file:
                    out_file.write(response.read())
        except ssl.SSLError as e:
            print(f"❌ CatClientHDR: SSL error downloading Java: {e}")
            messagebox.showerror("CatClientHDR Error", 
                               f"SSL verification failed while downloading Java.\n\nError: {str(e)}\n\nPlease check your internet connection or install Java manually.")
            return
        except Exception as e:
            print(f"❌ CatClientHDR: Failed to download Java: {e}")
            if os.path.exists(archive_path):
                os.remove(archive_path)  # Cleanup partial download
            messagebox.showerror("CatClientHDR Error", 
                               "Failed to download Java 21. Please check your internet connection or install Java manually.")
            return

        try:
            if platform.system() == "Windows":
                with zipfile.ZipFile(archive_path, "r") as zip_ref:
                    zip_ref.extractall(JAVA_DIR)
            else:
                import tarfile
                with tarfile.open(archive_path, "r:gz") as tar_ref:
                    tar_ref.extractall(JAVA_DIR)
                java_bin = os.path.join(JAVA_DIR, self.get_local_java_dir(), "bin", "java")
                if os.path.exists(java_bin):
                    os.chmod(java_bin, 0o755)  # Make Java executable
        except Exception as e:
            print(f"❌ CatClientHDR: Failed to extract Java: {e}")
            messagebox.showerror("CatClientHDR Error", 
                               f"Failed to extract Java 21: {str(e)}.\n\nPlease try again or install Java manually.")
            return
        finally:
            if os.path.exists(archive_path):
                os.remove(archive_path)  # Cleanup archive
        print("✅ CatClientHDR: Java 21 installed locally! Meow!")

    def select_skin(self):
        """Allow the user to select and apply a custom skin PNG file."""
        file_path = filedialog.askopenfilename(filetypes=[("PNG Files", "*.png")])
        if file_path:
            skin_dest = os.path.join(CATCLIENT_DIR, "skins")
            os.makedirs(skin_dest, exist_ok=True)
            try:
                shutil.copy(file_path, os.path.join(skin_dest, "custom_skin.png"))
                messagebox.showinfo("CatClientHDR", "🎨 Skin applied successfully! Note: This may require a mod to apply in-game. Meow! 🐱")
            except Exception as e:
                print(f"❌ CatClientHDR: Failed to apply skin: {e}")
                messagebox.showerror("CatClientHDR Error", f"Failed to apply skin: {str(e)}.\n\nPlease check file permissions or try another file.")

    @staticmethod
    def verify_file(file_path, expected_sha1):
        """Verify the SHA1 checksum of a file."""
        try:
            with open(file_path, "rb") as f:
                file_hash = hashlib.sha1(f.read()).hexdigest()
            return file_hash == expected_sha1
        except Exception as e:
            print(f"❌ CatClientHDR: Failed to verify file {file_path}: {e}")
            return False

    def download_version_files(self, version_id, version_url):
        """Download the version JSON, JAR, libraries, and natives with checksum verification."""
        print(f"⬇️ CatClientHDR: Downloading version files for {version_id}... 🐱")
        version_dir = os.path.join(VERSIONS_DIR, version_id)
        os.makedirs(version_dir, exist_ok=True)

        # Create SSL context that handles certificate verification issues
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        version_json_path = os.path.join(version_dir, f"{version_id}.json")
        try:
            req = urllib.request.Request(version_url, headers={'User-Agent': 'CatClientHDR/1.0'})
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as url:
                data = json.loads(url.read().decode())
                with open(version_json_path, "w") as f:
                    json.dump(data, f, indent=2)
        except ssl.SSLError as e:
            print(f"❌ CatClientHDR: SSL error downloading version JSON: {e}")
            messagebox.showerror("CatClientHDR Error", f"SSL verification failed for version {version_id} JSON.")
            return False
        except Exception as e:
            print(f"❌ CatClientHDR: Failed to download version JSON: {e}")
            if os.path.exists(version_json_path):
                os.remove(version_json_path)  # Cleanup partial file
            messagebox.showerror("CatClientHDR Error", f"Failed to download version {version_id} JSON.")
            return False

        try:
            jar_url = data["downloads"]["client"]["url"]
            jar_path = os.path.join(version_dir, f"{version_id}.jar")
            expected_sha1 = data["downloads"]["client"]["sha1"]
            if not os.path.exists(jar_path) or not CatClientHDRLauncher.verify_file(jar_path, expected_sha1):
                req = urllib.request.Request(jar_url, headers={'User-Agent': 'CatClientHDR/1.0'})
                with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
                    with open(jar_path, 'wb') as out_file:
                        out_file.write(response.read())
                if not CatClientHDRLauncher.verify_file(jar_path, expected_sha1):
                    print(f"❌ CatClientHDR: Checksum mismatch for {jar_path}")
                    if os.path.exists(jar_path):
                        os.remove(jar_path)  # Cleanup invalid file
                    messagebox.showerror("CatClientHDR Error", f"Checksum mismatch for version {version_id} JAR.")
                    return False
        except KeyError as e:
            print(f"❌ CatClientHDR: Missing client JAR info in JSON: {e}")
            messagebox.showerror("CatClientHDR Error", f"Version {version_id} is missing client JAR information.")
            return False
        except ssl.SSLError as e:
            print(f"❌ CatClientHDR: SSL error downloading JAR: {e}")
            messagebox.showerror("CatClientHDR Error", f"SSL verification failed for version {version_id} JAR.")
            return False
        except Exception as e:
            print(f"❌ CatClientHDR: Failed to download JAR: {e}")
            if os.path.exists(jar_path):
                os.remove(jar_path)  # Cleanup partial file
            messagebox.showerror("CatClientHDR Error", f"Failed to download version {version_id} JAR.")
            return False

        current_os = platform.system().lower()
        if current_os == "darwin":
            current_os = "osx"

        libraries_dir = os.path.join(CATCLIENT_DIR, "libraries")
        os.makedirs(libraries_dir, exist_ok=True)
        natives_dir = os.path.join(version_dir, "natives")
        os.makedirs(natives_dir, exist_ok=True)

        for lib in data.get("libraries", []):
            if self.is_library_allowed(lib, current_os):
                if "downloads" in lib and "artifact" in lib["downloads"]:
                    lib_url = lib["downloads"]["artifact"]["url"]
                    lib_path = os.path.join(libraries_dir, lib["downloads"]["artifact"]["path"])
                    os.makedirs(os.path.dirname(lib_path), exist_ok=True)
                    expected_sha1 = lib["downloads"]["artifact"]["sha1"]
                    if not os.path.exists(lib_path) or not CatClientHDRLauncher.verify_file(lib_path, expected_sha1):
                        try:
                            req = urllib.request.Request(lib_url, headers={'User-Agent': 'CatClientHDR/1.0'})
                            with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
                                with open(lib_path, 'wb') as out_file:
                                    out_file.write(response.read())
                            if not CatClientHDRLauncher.verify_file(lib_path, expected_sha1):
                                print(f"❌ CatClientHDR: Checksum mismatch for {lib_path}")
                                if os.path.exists(lib_path):
                                    os.remove(lib_path)
                                messagebox.showerror("CatClientHDR Error", f"Checksum mismatch for library {lib.get('name', 'unknown')}.")
                                return False
                        except ssl.SSLError as e:
                            print(f"❌ CatClientHDR: SSL error downloading library {lib.get('name', 'unknown')}: {e}")
                            messagebox.showerror("CatClientHDR Error", f"SSL verification failed for library {lib.get('name', 'unknown')}.")
                            return False
                        except Exception as e:
                            print(f"❌ CatClientHDR: Failed to download library {lib.get('name', 'unknown')}: {e}")
                            if os.path.exists(lib_path):
                                os.remove(lib_path)
                            return False

                if "natives" in lib and current_os in lib["natives"]:
                    classifier = lib["natives"][current_os]
                    if "downloads" in lib and "classifiers" in lib["downloads"] and classifier in lib["downloads"]["classifiers"]:
                        native_url = lib["downloads"]["classifiers"][classifier]["url"]
                        native_path = os.path.join(natives_dir, f"{classifier}.jar")
                        expected_sha1 = lib["downloads"]["classifiers"][classifier]["sha1"]
                        if not os.path.exists(native_path) or not CatClientHDRLauncher.verify_file(native_path, expected_sha1):
                            try:
                                req = urllib.request.Request(native_url, headers={'User-Agent': 'CatClientHDR/1.0'})
                                with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
                                    with open(native_path, 'wb') as out_file:
                                        out_file.write(response.read())
                                if not CatClientHDRLauncher.verify_file(native_path, expected_sha1):
                                    print(f"❌ CatClientHDR: Checksum mismatch for {native_path}")
                                    if os.path.exists(native_path):
                                        os.remove(native_path)
                                    messagebox.showerror("CatClientHDR Error", f"Checksum mismatch for native {lib.get('name', 'unknown')}.")
                                    return False
                            except ssl.SSLError as e:
                                print(f"❌ CatClientHDR: SSL error downloading native {lib.get('name', 'unknown')}: {e}")
                                messagebox.showerror("CatClientHDR Error", f"SSL verification failed for native {lib.get('name', 'unknown')}.")
                                return False
                            except Exception as e:
                                print(f"❌ CatClientHDR: Failed to download native {lib.get('name', 'unknown')}: {e}")
                                if os.path.exists(native_path):
                                    os.remove(native_path)
                                return False
                        try:
                            with zipfile.ZipFile(native_path, "r") as zip_ref:
                                zip_ref.extractall(natives_dir)
                            os.remove(native_path)
                        except Exception as e:
                            print(f"❌ CatClientHDR: Failed to extract native {lib.get('name', 'unknown')}: {e}")
                            messagebox.showerror("CatClientHDR Error", f"Failed to extract native {lib.get('name', 'unknown')}: {str(e)}.")
                            return False

        print("✅ CatClientHDR: Download complete! Ready to play! 🐱🔥")
        return True

    def modify_options_txt(self, target_fps=60):
        """Modify options.txt to set maxFps and disable vsync, preserving other settings."""
        options_path = os.path.join(CATCLIENT_DIR, "options.txt")
        options = {}
        if os.path.exists(options_path):
            try:
                with open(options_path, "r") as f:
                    for line in f:
                        parts = line.strip().split(":", 1)
                        if len(parts) == 2:
                            options[parts[0]] = parts[1]
            except Exception as e:
                print(f"⚠️ CatClientHDR: Could not read options.txt: {e}")
                messagebox.showwarning("CatClientHDR Warning", f"Could not read options.txt: {str(e)}. Creating new file.")

        options['maxFps'] = str(target_fps)
        options['enableVsync'] = 'false'

        try:
            os.makedirs(os.path.dirname(options_path), exist_ok=True)
            with open(options_path, "w") as f:
                for key, value in options.items():
                    f.write(f"{key}:{value}\n")
            print(f"⚙️ CatClientHDR: Set maxFps to {target_fps} and disabled vsync!")
        except Exception as e:
            print(f"❌ CatClientHDR: Failed to write options.txt: {e}")
            messagebox.showerror("CatClientHDR Error", f"Failed to write options.txt: {str(e)}.\n\nPlease check disk space or permissions.")

    def is_library_allowed(self, lib, current_os):
        """Check if a library is allowed on the current OS based on its rules."""
        if "rules" not in lib:
            return True
        allowed = False
        for rule in lib["rules"]:
            if rule["action"] == "allow":
                if "os" not in rule or (isinstance(rule.get("os"), dict) and rule["os"].get("name") == current_os):
                    allowed = True
            elif rule["action"] == "disallow":
                if "os" in rule and isinstance(rule.get("os"), dict) and rule["os"].get("name") == current_os:
                    allowed = False
        return allowed

    def evaluate_rules(self, rules, current_os):
        """Evaluate argument rules based on the current OS, ignoring feature-based rules."""
        if not rules:
            return True
        allowed = False
        for rule in rules:
            if "features" in rule:
                continue
            if rule["action"] == "allow":
                if "os" not in rule or (isinstance(rule.get("os"), dict) and rule["os"].get("name") == current_os):
                    allowed = True
            elif rule["action"] == "disallow":
                if "os" in rule and isinstance(rule.get("os"), dict) and rule["os"].get("name") == current_os:
                    allowed = False
        return allowed

    def generate_offline_uuid(self, username):
        """Generate a UUID for offline mode based on the username."""
        offline_prefix = "OfflinePlayer:"
        hash_value = hashlib.md5((offline_prefix + username).encode('utf-8')).hexdigest()
        uuid_str = f"{hash_value[:8]}-{hash_value[8:12]}-{hash_value[12:16]}-{hash_value[16:20]}-{hash_value[20:32]}"
        return uuid_str

    def build_launch_command(self, version, username, ram):
        """Construct the command to launch Minecraft."""
        version_dir = os.path.join(VERSIONS_DIR, version)
        json_path = os.path.join(version_dir, f"{version}.json")

        try:
            with open(json_path, "r") as f:
                version_data = json.load(f)
        except Exception as e:
            print(f"❌ CatClientHDR: Failed to read version JSON: {e}")
            messagebox.showerror("CatClientHDR Error", f"Cannot read version {version} JSON.")
            return []

        current_os = platform.system().lower()
        if current_os == "darwin":
            current_os = "osx"

        main_class = version_data.get("mainClass", "net.minecraft.client.main.Main")
        libraries_dir = os.path.join(CATCLIENT_DIR, "libraries")
        natives_dir = os.path.join(version_dir, "natives")
        jar_path = os.path.join(version_dir, f"{version}.jar")
        classpath = [jar_path]

        for lib in version_data.get("libraries", []):
            if "downloads" in lib and "artifact" in lib["downloads"]:
                lib_path = os.path.join(libraries_dir, lib["downloads"]["artifact"]["path"])
                if os.path.exists(lib_path):
                    classpath.append(lib_path)

        classpath_str = ";".join(classpath) if platform.system() == "Windows" else ":".join(classpath)
        java_bin = "java"
        if not self.is_java_installed():
            java_bin = os.path.join(JAVA_DIR, self.get_local_java_dir(), "bin", "java.exe" if platform.system() == "Windows" else "java")
            if not os.path.exists(java_bin):
                print(f"❌ CatClientHDR: Java binary not found at {java_bin}")
                messagebox.showerror("CatClientHDR Error", "Java binary not found. Please install Java manually.")
                return []

        command = [java_bin, f"-Xmx{ram}G"]

        jvm_args = []
        if "arguments" in version_data and "jvm" in version_data["arguments"]:
            for arg in version_data["arguments"]["jvm"]:
                if isinstance(arg, str):
                    jvm_args.append(arg)
                elif isinstance(arg, dict) and "rules" in arg and "value" in arg:
                    if self.evaluate_rules(arg["rules"], current_os):
                        if isinstance(arg["value"], list):
                            jvm_args.extend(arg["value"])
                        else:
                            jvm_args.append(arg["value"])
                            jvm_args.append(arg["value"])

        if platform.system() == "Darwin" and "-XstartOnFirstThread" not in jvm_args:
            jvm_args.append("-XstartOnFirstThread")

        if not any("-Djava.library.path" in arg for arg in jvm_args):
            jvm_args.append(f"-Djava.library.path={natives_dir}")

        command.extend(jvm_args)

        game_args = []
        if "arguments" in version_data and "game" in version_data["arguments"]:
            for arg in version_data["arguments"]["game"]:
                if isinstance(arg, str):
                    game_args.append(arg)
                elif isinstance(arg, dict) and "rules" in arg and "value" in arg:
                    if self.evaluate_rules(arg["rules"], current_os):
                        if isinstance(arg["value"], list):
                            game_args.extend(arg["value"])
                        else:
                            game_args.append(arg["value"])
        elif "minecraftArguments" in version_data:
            game_args = version_data["minecraftArguments"].split()

        uuid = self.generate_offline_uuid(username)

        replacements = {
            "${auth_player_name}": username,
            "${version_name}": version,
            "${game_directory}": CATCLIENT_DIR,
            "${assets_root}": os.path.join(CATCLIENT_DIR, "assets"),
            "${assets_index_name}": version_data.get("assetIndex", {}).get("id", "legacy"),
            "${auth_uuid}": uuid,
            "${auth_access_token}": "0",
            "${user_type}": "legacy",
            "${version_type}": version_data.get("type", "release"),
            "${user_properties}": "{}",
            "${quickPlayRealms}": "",
        }

        def replace_placeholders(arg):
            for key, value in replacements.items():
                arg = arg.replace(key, value)
            return arg

        game_args = [replace_placeholders(arg) for arg in game_args]
        jvm_args = [replace_placeholders(arg) for arg in jvm_args]

        command.extend(["-cp", classpath_str, main_class] + game_args)
        return command

    def validate_username(self, username):
        """Validate the username to ensure it's non-empty and alphanumeric."""
        if not username or not re.match(r'^[a-zA-Z0-9_]+$', username):
            return "CatGamer"
        return username

    def prepare_and_launch(self):
        """Wrapper function to handle setup before launching."""
        self.install_java_if_needed()
        self.modify_options_txt(target_fps=60)
        self.download_and_launch()

    def download_and_launch(self):
        """Handle the download and launch process."""
        version = self.version_combo.get()
        if not version:
            messagebox.showerror("CatClientHDR Error", "No version selected. Meow!")
            return

        username = self.validate_username(self.username_input.get())
        ram = int(self.ram_scale.get())
        version_url = self.versions.get(version)

        if not version_url:
            messagebox.showerror("CatClientHDR Error", f"Version {version} URL not found.")
            return

        if not self.download_version_files(version, version_url):
            return

        launch_cmd = self.build_launch_command(version, username, ram)
        if not launch_cmd:
            return

        print("🚀 CatClientHDR: Launching Minecraft with:", " ".join(launch_cmd))
        print("🐱 Meow! Have fun gaming! 🔥")
        try:
            subprocess.Popen(launch_cmd)
        except Exception as e:
            print(f"❌ CatClientHDR: Failed to launch Minecraft: {e}")
            messagebox.showerror("CatClientHDR Error", f"Failed to launch Minecraft: {str(e)}.\n\nPlease check your settings or Java installation.")

if __name__ == "__main__":
    print("🐱🔥 CatClientHDR v1.0 - Initializing... Meow! 🔥🐱")
    app = CatClientHDRLauncher()
    app.mainloop()
