import logging
import sys

from kanha_manager import app, log
import database  # ensures tables are created

from kanha_manager.modules import (
    admin,
    warns,
    welcome,
    notes,
    filters,
    blacklist,
    locks,
    flood,
    info,
    report,
    help,
)

def load_modules():
    modules = [admin, warns, welcome, notes, filters, blacklist, locks, flood, info, report, help]
    for module in modules:
        module.register(app)
        log.info(f"Loaded module: {module.__name__}")

def main():
    load_modules()
    log.info("🌸 Kanha Manager is starting...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
