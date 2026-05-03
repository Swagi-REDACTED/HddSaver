Game.registerMod("hdd_saver", {
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
});