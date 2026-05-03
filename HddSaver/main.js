Game.registerMod("hdd_saver", {
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
});
