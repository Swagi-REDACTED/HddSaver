import os
import sys

# =====================================================================
# MOD FILES CONTENT
# =====================================================================

INFO_TXT = r"""{
    "Name": "HDD Auto-Saver",
    "ID": "hdd_saver",
    "Author": "Blupillcosby",
    "Description": "Automatically exports your save code to a text file on a specified hard drive every 60 seconds.",
    "ModVersion": 1.0,
    "GameVersion": 2.052,
    "Date": "03/05/2026",
    "Dependencies": [],
    "LanguagePacks": ["EN"],
    "AllowSteamAchievs": true
}"""

MAIN_JS = r"""Game.registerMod("hdd_saver", {
    init: function() {
        if (typeof window.api !== 'undefined') {
            console.log("HDD Saver Mod Initialized via native window.api.");
            
            this.backupIndex = 1;

            const performBackup = () => {
                let saveData = "";
                let isError = false;

                try {
                    if (typeof Game !== 'undefined' && typeof Game.WriteSave === 'function') {
                        let bakeryName = Game.bakeryName || "Unknown";
                        let formattedCookies = Math.floor(Game.cookies || 0).toLocaleString('en-US');
                        let formattedCPS = Math.floor(Game.cookiesPs || 0).toLocaleString('en-US');
                        
                        let header = `Name: ${bakeryName}'s bakery. Cookies: ${formattedCookies}. CPS: ${formattedCPS}.\n`;
                        saveData = header + Game.WriteSave(1);
                    } else {
                        throw new Error("Game.WriteSave function is missing or not ready!");
                    }
                } catch (err) {
                    isError = true;
                    console.error("!!! HDD SAVER MOD: CRITICAL FAILURE !!!\n", err);
                    saveData = "ERROR: Failed to get export code. Timestamp: " + new Date().toISOString() + "\nError details: " + err.message;
                }

                const fileName = 'CookieClickerBackup_' + this.backupIndex;
                let fileToDelete = null;

                if (this.backupIndex > 3) {
                    fileToDelete = 'CookieClickerBackup_' + (this.backupIndex - 3);
                }
                
                try {
                    window.api.send('toMain', {
                        id: 'hdd_backup',
                        data: saveData,
                        fileName: fileName,
                        deleteFile: fileToDelete
                    });
                    
                    if (isError) {
                        Game.Notify('HDD Saver Error', 'Saved ERROR log to slot ' + this.backupIndex, [16, 5], 6);
                    } else {
                        Game.Notify('Auto-Backup', 'Saved to backup slot ' + this.backupIndex, [16, 5], 2);
                    }
                    
                    this.backupIndex++;
                } catch(e) {
                    console.error('HDD Saver Error:', e);
                }
            };

            // Listen ONLY for the native save trigger from start.js
            window.api.receive('fromMain', (args) => {
                if (args && args.id === 'trigger_hdd_save') {
                    console.log("HDD Saver Mod: Native save triggered!");
                    performBackup();
                }
            });

        } else {
            console.error('HDD Saver Mod: window.api missing!');
        }
    },
    save: function() { 
        return String(this.backupIndex); 
    },
    load: function(str) {
        if (str) {
            this.backupIndex = parseInt(str) || 1;
        }
    }
});"""

NEW_START_JS_BLOCK = r"""else if (req=='save' && args.data)
			{
				try {
					if (!fs.existsSync(path.join(__dirname,'/save'))) fs.mkdirSync(path.join(__dirname,'/save'),{recursive:true});
					fs.writeFileSync(path.join(__dirname,'/save/'+saveFile),String(args.data),'utf-8');
					
					// --- TINY SURGICAL PATCH: Tell the mod to run its backup! ---
					send('trigger_hdd_save', 0, callback);
					// ------------------------------------------------------------
					
					send('saved',0,callback);
				}
				catch(e){send('saved',0,callback);}
			}
			else if (req=='hdd_backup' && args.fileName)
			{
				try {
					let backupDir = 'D:\\CookieBackups';
					if (!fs.existsSync(backupDir)) fs.mkdirSync(backupDir,{recursive:true});
					
					// Delete the old file if requested
					if (args.deleteFile) {
						let delPath = path.join(backupDir, args.deleteFile + '.txt');
						if (fs.existsSync(delPath)) fs.unlinkSync(delPath);
					}
					
					// Save the new file
					if (args.data) {
						fs.writeFileSync(path.join(backupDir, args.fileName + '.txt'), String(args.data), 'utf-8');
					}
				}
				catch(e){console.log('HDD backup error:', e);}
			}"""

# =====================================================================
# INSTALLER LOGIC
# =====================================================================

def get_base_dir():
    """Gets the correct directory whether running as a .py script or compiled .exe"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def patch_start_js(filepath):
    print(f"[*] Reading target: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Check if already patched
    if "trigger_hdd_save" in content or "hdd_backup" in content:
        print("[~] start.js is already patched! Skipping injection.")
        return True

    # 2. Find the exact start of the target block
    idx = content.find("else if (req=='save' && args.data)")
    if idx == -1:
        print("[X] ERROR: Could not find the target 'save' function in start.js!")
        return False

    # 3. Find the opening brace '{'
    brace_start = content.find("{", idx)
    if brace_start == -1:
        print("[X] ERROR: Parse error, could not find opening brace.")
        return False

    # 4. Bracket counting algorithm to find the exact closing brace '}'
    brace_count = 0
    brace_end = -1
    for i in range(brace_start, len(content)):
        if content[i] == '{':
            brace_count += 1
        elif content[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                brace_end = i
                break

    if brace_end == -1:
        print("[X] ERROR: Parse error, could not find closing brace.")
        return False

    # 5. Swap the block
    print("[*] Target block located. Injecting surgical patch...")
    new_content = content[:idx] + NEW_START_JS_BLOCK + content[brace_end+1:]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("[✓] Successfully patched start.js!")
    return True

def write_if_changed(filepath, content, filename):
    """Checks if the file already exists and matches the content. Skips writing if it matches."""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            if f.read() == content:
                print(f"[~] {filename} is already up to date! Skipping.")
                return
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[✓] Created/Updated {filename}")

def install_mod(mod_dir):
    print(f"\n[*] Setting up Mod directory: {mod_dir}")
    os.makedirs(mod_dir, exist_ok=True)

    info_path = os.path.join(mod_dir, "info.txt")
    main_path = os.path.join(mod_dir, "main.js")

    write_if_changed(info_path, INFO_TXT, "info.txt")
    write_if_changed(main_path, MAIN_JS, "main.js")

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
        print("Please make sure you place this .exe file inside your main Cookie Clicker folder!")
        input("\nPress Enter to exit...")
        sys.exit(1)

    patch_success = patch_start_js(start_js_path)
    
    if patch_success:
        install_mod(mod_dir)
        print("\n==================================================")
        print("   INSTALLATION COMPLETE! YOU ARE GOOD TO GO!     ")
        print("==================================================")
    else:
        print("\n[!] Installation aborted due to an error.")

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()