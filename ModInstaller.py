import os
import sys

# =====================================================================
# MOD FILES CONTENT
# =====================================================================

INFO_TXT = r"""{
    "Name": "HDD Auto-Saver",
    "ID": "hdd_saver",
    "Author": "Blupillcosby",
    "Description": "Automatically exports your save code to a text file on a specified hard drive every time the game saves. Configurable in the Options menu.",
    "ModVersion": 1.2,
    "GameVersion": 2.052,
    "Date": "03/05/2026",
    "Dependencies": [],
    "LanguagePacks": ["EN"],
    "AllowSteamAchievs": true
}"""

MAIN_JS = r"""Game.registerMod("hdd_saver", {
    init: function() {
        let MOD = this;
        this.backupIndex = 1;
        this.maxBackups = 3;
        this.driveLetter = 'D';
        this.availableDrives = ['C', 'D']; 

        if (typeof window.api !== 'undefined') {
            window.api.send('toMain', { id: 'hdd_get_drives' });

            this.saveConfig = function() {
                let maxEl = document.getElementById('hddMaxBackups');
                if (maxEl) {
                    let val = parseInt(maxEl.value);
                    if (!isNaN(val)) {
                        MOD.maxBackups = Math.max(1, Math.min(1000, val));
                    }
                }
            };

            let oldUpdateMenu = Game.UpdateMenu;
            Game.UpdateMenu = function() {
                oldUpdateMenu();
                if (Game.onMenu === 'prefs') {
                    let menuNode = document.getElementById('menu');
                    if (menuNode) {
                        let div = document.createElement('div');
                        div.innerHTML = `
                            <style>
                                /* Number Input Arrow Styling */
                                #hddMaxBackups::-webkit-inner-spin-button, 
                                #hddMaxBackups::-webkit-outer-spin-button {
                                    opacity: 0;
                                    cursor: pointer;
                                    filter: sepia(100%) hue-rotate(345deg) saturate(250%) brightness(0.8);
                                }
                                #hddMaxBackups:hover::-webkit-inner-spin-button, 
                                #hddMaxBackups:hover::-webkit-outer-spin-button {
                                    opacity: 1;
                                }

                                .hdd-custom-select {
                                    position: relative;
                                    display: inline-block;
                                    vertical-align: middle;
                                    min-width: 65px;
                                    user-select: none;
                                    cursor: pointer;
                                }

                                /* We use a real select tag for the 'default' look, but disable its menu */
                                .hdd-select-shell {
                                    font-weight: bold;
                                    font-size: 11px;
                                    margin: 2px 4px 2px 0px;
                                    padding: 2px 4px;
                                    border-radius: 2px;
                                    background: #000 url(img/darkNoise.jpg);
                                    color: #ccc;
                                    border: 1px solid #e2dd48;
                                    border-color: #ece2b6 #875526 #733726 #dfbc9a;
                                    box-shadow: 0px 0px 1px 2px rgba(0,0,0,0.5), 0px 2px 4px rgba(0,0,0,0.25), 0px 0px 2px 2px #000 inset, 0px 1px 0px 1px rgba(255,255,255,0.5) inset;
                                    text-shadow: 0px 1px 1px #000;
                                    pointer-events: none; /* Let the container handle the click */
                                    width: 100%;
                                }

                                .hdd-select-menu {
                                    display: none;
                                    position: absolute;
                                    top: 100%;
                                    left: 0;
                                    z-index: 10000;
                                    background: #111 url(img/darkNoise.jpg);
                                    border: 1px solid #e2dd48;
                                    border-color: #ece2b6 #875526 #733726 #dfbc9a;
                                    box-shadow: 0px 4px 12px rgba(0,0,0,0.9);
                                    min-width: 100%;
                                    margin-top: 2px;
                                }

                                .hdd-select-menu.open { display: block; }

                                .hdd-option {
                                    padding: 5px 10px;
                                    cursor: pointer;
                                    color: #ccc;
                                    font-weight: bold;
                                    font-size: 11px;
                                    white-space: nowrap;
                                    transition: all 0.1s;
                                }

                                .hdd-option:hover {
                                    color: #ffffff !important;
                                    background-color: rgba(255, 255, 255, 0.1);
                                    text-shadow: 0px 0px 4px #3cf, 0px 0px 6px #33f !important;
                                    box-shadow: 0px 0px 2px 0px #3cf inset, 0px 0px 6px 1px #33f inset !important;
                                }

                                .hdd-option.selected {
                                    color: #ffffff !important;
                                    text-shadow: 0px 0px 4px #3cf, 0px 0px 6px #33f !important;
                                    background-color: rgba(51, 204, 255, 0.15);
                                }
                            </style>
                            <div class="block" style="padding:0px;margin:8px 4px;">
                                <div class="subsection" style="padding:0px;">
                                    <div class="title">HDD Auto-Saver Settings</div>
                                    <div class="listing">
                                        <label style="display:inline-block; width:170px; text-align:right; padding-right:10px;">Save Drive:</label>
                                        <div class="hdd-custom-select" id="hddDriveContainer">
                                            <select class="hdd-select-shell">
                                                <option>${MOD.driveLetter}:\\</option>
                                            </select>
                                            <div class="hdd-select-menu" id="hddDriveMenu">
                                                ${MOD.availableDrives.map(c => `
                                                    <div class="hdd-option ${MOD.driveLetter === c ? 'selected' : ''}" data-value="${c}">${c}:\\</div>
                                                `).join('')}
                                            </div>
                                        </div>
                                    </div>
                                    <div class="listing">
                                        <label style="display:inline-block; width:170px; text-align:right; padding-right:10px;">Max Backups (1-1000):</label>
                                        <input type="number" id="hddMaxBackups" min="1" max="1000" value="${MOD.maxBackups}" style="font-weight:bold; font-size:11px; padding:2px; width:50px; text-align:center; vertical-align:middle; background:#000 url(img/darkNoise.jpg); color:#ccc; border:1px solid #e2dd48; border-color:#ece2b6 #875526 #733726 #dfbc9a; border-radius:2px; box-shadow:0px 0px 1px 2px rgba(0,0,0,0.5), 0px 2px 4px rgba(0,0,0,0.25), 0px 0px 2px 2px #000 inset, 0px 1px 0px 1px rgba(255,255,255,0.5) inset; text-shadow:0px 1px 1px #000;" oninput="Game.mods['hdd_saver'].saveConfig()">
                                    </div>
                                </div>
                            </div>
                        `;
                        let spacer = menuNode.querySelector('div[style*="height:128px"]');
                        if (spacer) menuNode.insertBefore(div, spacer); else menuNode.appendChild(div);

                        // Attach Custom Logic
                        const container = document.getElementById('hddDriveContainer');
                        const menu = document.getElementById('hddDriveMenu');
                        
                        container.onclick = (e) => {
                            e.stopPropagation();
                            menu.classList.toggle('open');
                        };

                        document.querySelectorAll('.hdd-option').forEach(opt => {
                            opt.onclick = (e) => {
                                e.stopPropagation();
                                MOD.driveLetter = opt.getAttribute('data-value');
                                menu.classList.remove('open');
                                Game.Notify('HDD Saver', 'Drive set to ' + MOD.driveLetter, [16, 5], 2);
                                Game.UpdateMenu(); // Re-render to update the visual shell and highlights
                            };
                        });

                        window.addEventListener('click', () => {
                            if (menu) menu.classList.remove('open');
                        }, { once: true });
                    }
                }
            };

            const performBackup = () => {
                let saveData = "";
                let isError = false;
                let bakeryName = "Unknown";
                try {
                    if (typeof Game !== 'undefined' && typeof Game.WriteSave === 'function') {
                        bakeryName = Game.bakeryName || "Unknown";
                        let formattedCookies = Math.floor(Game.cookies || 0).toLocaleString('en-US');
                        let formattedCPS = Math.floor(Game.cookiesPs || 0).toLocaleString('en-US');
                        saveData = `Name: ${bakeryName}'s bakery. Cookies: ${formattedCookies}. CPS: ${formattedCPS}.\n` + Game.WriteSave(1);
                    } else throw new Error("Game.WriteSave function is missing or not ready!");
                } catch (err) {
                    isError = true;
                    saveData = "ERROR: Failed to get export code. Timestamp: " + new Date().toISOString() + "\nError details: " + err.message;
                }
                const fileName = 'CookieClickerBackup_' + MOD.backupIndex;
                let fileToDelete = MOD.backupIndex > MOD.maxBackups ? 'CookieClickerBackup_' + (MOD.backupIndex - MOD.maxBackups) : null;
                try {
                    window.api.send('toMain', {
                        id: 'hdd_backup',
                        data: saveData,
                        fileName: fileName,
                        deleteFile: fileToDelete,
                        drive: MOD.driveLetter,
                        bakeryName: bakeryName
                    });
                    if (isError) Game.Notify('HDD Saver Error', 'Saved ERROR log to slot ' + MOD.backupIndex, [16, 5], 6);
                    else Game.Notify('Auto-Backup', 'Saved to backup slot ' + MOD.backupIndex, [16, 5], 2);
                    MOD.backupIndex++;
                } catch(e) {}
            };

            window.api.receive('fromMain', (args) => {
                if (args && args.id === 'trigger_hdd_save') performBackup();
                if (args && args.id === 'hdd_drives_list' && Array.isArray(args.data)) MOD.availableDrives = args.data;
            });
        }
    },
    save: function() { 
        return JSON.stringify({ backupIndex: this.backupIndex, maxBackups: this.maxBackups, driveLetter: this.driveLetter }); 
    },
    load: function(str) {
        if (str) {
            try {
                let data = JSON.parse(str);
                this.backupIndex = data.backupIndex || 1;
                this.maxBackups = data.maxBackups || 3;
                this.driveLetter = data.driveLetter || 'D';
            } catch(e) { this.backupIndex = parseInt(str) || 1; }
        }
    }
});"""

NEW_START_JS_BLOCK = r"""else if (req=='save' && args.data)
            {
                try {
                    if (!fs.existsSync(path.join(__dirname,'/save'))) fs.mkdirSync(path.join(__dirname,'/save'),{recursive:true});
                    fs.writeFileSync(path.join(__dirname,'/save/'+saveFile),String(args.data),'utf-8');
                    send('trigger_hdd_save', 0, callback);
                    send('saved',0,callback);
                }
                catch(e){send('saved',0,callback);}
            }
            else if (req=='hdd_backup' && args.fileName)
            {
                try {
                    let drive = args.drive || 'D';
                    let bakery = (args.bakeryName || 'Unknown').replace(/[^a-zA-Z0-9 \-_']/g, '').trim();
                    if (!bakery) bakery = 'Unknown';
                    let backupDir = drive + ':/CookieBackups/' + bakery;
                    if (!fs.existsSync(backupDir)) fs.mkdirSync(backupDir,{recursive:true});
                    if (args.deleteFile) {
                        let delPath = path.join(backupDir, args.deleteFile + '.txt');
                        if (fs.existsSync(delPath)) fs.unlinkSync(delPath);
                    }
                    if (args.data) fs.writeFileSync(path.join(backupDir, args.fileName + '.txt'), String(args.data), 'utf-8');
                }
                catch(e){console.log('HDD backup error:', e);}
            }
            else if (req=='hdd_get_drives')
            {
                try {
                    let drives = [];
                    for (let i = 65; i <= 90; i++) {
                        let letter = String.fromCharCode(i);
                        if (fs.existsSync(letter + ':/')) drives.push(letter);
                    }
                    send('hdd_drives_list', drives, callback);
                }
                catch(e){console.log('HDD drive fetch error:', e);}
            }"""

# =====================================================================
# INSTALLER LOGIC
# =====================================================================

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def clean_old_blocks(content):
    blocks_to_remove = ["else if (req=='hdd_get_drives'", "else if (req=='hdd_backup'"]
    for block in blocks_to_remove:
        idx = content.find(block)
        if idx != -1:
            print(f"[*] Found old injected block '{block}'. Cleaning it up...")
            brace_start = content.find("{", idx)
            if brace_start != -1:
                brace_count = 0
                brace_end = -1
                for i in range(brace_start, len(content)):
                    if content[i] == '{': brace_count += 1
                    elif content[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            brace_end = i
                            break
                if brace_end != -1: content = content[:idx] + content[brace_end+1:]
    return content

def patch_start_js(filepath):
    print(f"[*] Reading target: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f: content = f.read()
    if "hdd_get_drives" in content and "args.bakeryName" in content:
        print("[~] start.js is already patched and up to date! Skipping injection.")
        return True
    content = clean_old_blocks(content)
    idx = content.find("else if (req=='save' && args.data)")
    if idx == -1: return False
    brace_start = content.find("{", idx)
    if brace_start == -1: return False
    brace_count = 0
    brace_end = -1
    for i in range(brace_start, len(content)):
        if content[i] == '{': brace_count += 1
        elif content[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                brace_end = i
                break
    if brace_end == -1: return False
    print("[*] Target block located. Injecting surgical patch...")
    new_content = content[:idx] + NEW_START_JS_BLOCK + content[brace_end+1:]
    with open(filepath, 'w', encoding='utf-8') as f: f.write(new_content)
    print("[✓] Successfully patched start.js!")
    return True

def write_if_changed(filepath, content, filename):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            if f.read() == content:
                print(f"[~] {filename} is already up to date! Skipping.")
                return
    with open(filepath, 'w', encoding='utf-8') as f: f.write(content)
    print(f"[✓] Created/Updated {filename}")

def install_mod(mod_dir):
    print(f"\n[*] Setting up Mod directory: {mod_dir}")
    os.makedirs(mod_dir, exist_ok=True)
    write_if_changed(os.path.join(mod_dir, "info.txt"), INFO_TXT, "info.txt")
    write_if_changed(os.path.join(mod_dir, "main.js"), MAIN_JS, "main.js")

def main():
    print("==================================================")
    print("    COOKIE CLICKER HDD AUTO-SAVER INSTALLER       ")
    print("==================================================\n")
    base_dir = get_base_dir()
    print(f"[*] Detected executable path: {base_dir}\n")
    start_js_path = os.path.join(base_dir, "resources", "app", "start.js")
    mod_dir = os.path.join(base_dir, "resources", "app", "mods", "local", "HddSaver")
    if not os.path.exists(start_js_path):
        print("[X] CRITICAL ERROR: Could not find resources\\app\\start.js")
        input("\nPress Enter to exit...")
        sys.exit(1)
    if patch_start_js(start_js_path): install_mod(mod_dir)
    print("\n==================================================")
    print("   INSTALLATION COMPLETE! YOU ARE GOOD TO GO!     ")
    print("==================================================")
    input("\nPress Enter to exit...")

if __name__ == "__main__": main()
