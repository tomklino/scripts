#!/usr/bin/env python3
"""
Hybrid Power Management Installer

Installs and configures laptop suspend logic with:
- Idle timeout suspend
- Immediate suspend on lid close (conditional)
- AC power inhibit to prevent idle suspend when plugged in

Usage:
    sudo python3 install-power-config.py [--config CONFIG_FILE]

Requires: Python 3.6+ (no external dependencies)
"""

import argparse
import logging
import subprocess
import sys
import os
from pathlib import Path
from string import Template

# Set up logging
log = logging.getLogger(__name__)

# Paths
SCRIPT_DIR = Path(__file__).parent
DEFAULT_CONFIG = SCRIPT_DIR / "power-config.toml"
TEMPLATES_DIR = SCRIPT_DIR / "templates"

TARGET_FILES = {
    "logind_dropin": Path("/etc/systemd/logind.conf.d/power-management.conf"),
    "power_logic": Path("/usr/local/bin/power-logic.sh"),
    "udev_rules": Path("/etc/udev/rules.d/99-power-rules.rules"),
    "ac_inhibit_script": Path("/usr/local/bin/ac-inhibit.sh"),
    "ac_inhibit_service": Path("/etc/systemd/system/ac-inhibit.service"),
}


def parse_toml(content: str) -> dict:
    """
    Minimal TOML parser for simple config files.
    Handles: strings, integers, booleans, and nested tables.
    """
    result = {}
    current_section = result

    for line in content.split("\n"):
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        # Section header [section] or [section.subsection]
        if line.startswith("[") and line.endswith("]"):
            section_path = line[1:-1].split(".")
            current_section = result
            for key in section_path:
                if key not in current_section:
                    current_section[key] = {}
                current_section = current_section[key]
            continue

        # Key-value pair
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            # Remove inline comment
            if " #" in value:
                value = value.split(" #")[0].strip()

            # Parse value
            if value.startswith('"') and value.endswith('"'):
                current_section[key] = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                current_section[key] = value[1:-1]
            elif value.lower() == "true":
                current_section[key] = True
            elif value.lower() == "false":
                current_section[key] = False
            elif value.isdigit():
                current_section[key] = int(value)
            else:
                current_section[key] = value

    return result


def load_config(config_path: Path) -> dict:
    """Load configuration from TOML file."""
    if not config_path.exists():
        log.error(f"Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        return parse_toml(f.read())


def render_template(template_name: str, context: dict) -> str:
    """Render a template file using string.Template substitution."""
    template_path = TEMPLATES_DIR / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    with open(template_path) as f:
        template_content = f.read()

    return Template(template_content).substitute(**context)


class PowerConfigInstaller:
    """Installer for hybrid power management configuration."""

    def __init__(self, config: dict, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run

        # Set action functions based on dry_run
        if dry_run:
            self.write_file = self._write_file_dry
            self.remove_file = self._remove_file_dry
            self.mkdir = self._mkdir_dry
            self.run_cmd = self._run_cmd_dry
            self.log_action = self._log_action_dry
        else:
            self.write_file = self._write_file_wet
            self.remove_file = self._remove_file_wet
            self.mkdir = self._mkdir_wet
            self.run_cmd = self._run_cmd_wet
            self.log_action = self._log_action_wet

    # === DRY RUN ACTIONS ===

    def _write_file_dry(self, target: Path, content: str, mode: int = 0o644) -> None:
        log.info("")
        log.info("=" * 60)
        log.info(f"# Target: {target}")
        log.info("=" * 60)
        log.info(content.rstrip())
        log.info("")

    def _remove_file_dry(self, target: Path) -> None:
        log.info(f"Would remove: {target}")

    def _mkdir_dry(self, target: Path, parents: bool = True) -> None:
        log.info(f"Would create directory: {target}")

    def _run_cmd_dry(self, cmd: list, check: bool = True) -> subprocess.CompletedProcess:
        log.info(f"Would run: {' '.join(cmd)}")
        # Return a fake CompletedProcess for compatibility
        return subprocess.CompletedProcess(cmd, returncode=0, stdout="", stderr="")

    def _log_action_dry(self, message: str) -> None:
        log.info(f"[DRY] {message}")

    # === WET (REAL) ACTIONS ===

    def _write_file_wet(self, target: Path, content: str, mode: int = 0o644) -> None:
        target.write_text(content)
        if mode != 0o644:
            target.chmod(mode)

    def _remove_file_wet(self, target: Path) -> None:
        if target.exists():
            target.unlink()

    def _mkdir_wet(self, target: Path, parents: bool = True) -> None:
        target.mkdir(parents=parents, exist_ok=True)

    def _run_cmd_wet(self, cmd: list, check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(cmd, check=check, capture_output=True, text=True)

    def _log_action_wet(self, message: str) -> None:
        log.debug(message)

    # === INSTALLER METHODS ===

    def ensure_sudo(self) -> None:
        if self.dry_run:
            self.log_action("Skipping sudo check (dry-run)")
            return
        if os.geteuid() != 0:
            log.error("This script must be run as root (use sudo)")
            sys.exit(1)

    def configure_logind(self) -> None:
        """Configure idle timer via logind drop-in."""
        idle_config = self.config.get("idle", {})

        action = idle_config.get("action", "suspend")
        timeout = idle_config.get("timeout_minutes", 20)

        self.log_action(f"Configuring logind: IdleAction={action}, IdleActionSec={timeout}min")

        rendered = render_template("logind.conf.tpl", {
            "idle_action": action,
            "idle_timeout": timeout
        })

        self.mkdir(TARGET_FILES["logind_dropin"].parent)
        self.write_file(TARGET_FILES["logind_dropin"], rendered)

    def create_power_logic_script(self) -> None:
        """Create the power-logic.sh script to immediately suspend when unlugged and lid is closed."""
        lid_config = self.config.get("lid_close_suspend", {})

        if not lid_config.get("enabled", True):
            self.log_action("Skipping power-logic.sh (lid_close_suspend disabled)")
            self.remove_file(TARGET_FILES["power_logic"])
            return

        on_battery = lid_config.get("on_battery", True)
        require_no_ext = lid_config.get("require_no_external_monitor", True)

        self.log_action(f"Creating power-logic.sh (on_battery={on_battery}, require_no_external_monitor={require_no_ext})")

        rendered = render_template("power-logic.sh.tpl", {
            "on_battery": "true" if on_battery else "false",
            "require_no_external_monitor": "true" if require_no_ext else "false"
        })

        self.write_file(TARGET_FILES["power_logic"], rendered, mode=0o755)

    def create_udev_rules(self) -> None:
        """Create udev rules to run power logic when relevant changes are detected."""
        lid_config = self.config.get("lid_close_suspend", {})

        if not lid_config.get("enabled", True):
            self.log_action("Skipping udev rules (lid_close_suspend disabled)")
            self.remove_file(TARGET_FILES["udev_rules"])
            return

        self.log_action("Creating udev rules")

        rendered = render_template("udev-rules.rules.tpl", {})

        self.write_file(TARGET_FILES["udev_rules"], rendered)

    def create_ac_inhibit_script(self) -> None:
        """Create the ac-inhibit.sh script to prevent suspension when plugged in."""
        inhibit_config = self.config.get("ac_inhibit", {})

        if not inhibit_config.get("enabled", True):
            self.log_action("Skipping ac-inhibit.sh (ac_inhibit disabled)")
            self.remove_file(TARGET_FILES["ac_inhibit_script"])
            return

        interval = inhibit_config.get("check_interval_seconds", 60)

        self.log_action(f"Creating ac-inhibit.sh (check_interval={interval}s)")

        rendered = render_template("ac-inhibit.sh.tpl", {"check_interval": interval})

        self.write_file(TARGET_FILES["ac_inhibit_script"], rendered, mode=0o755)

    def create_ac_inhibit_service(self) -> None:
        """Create the systemd service for ac-inhibit."""
        inhibit_config = self.config.get("ac_inhibit", {})

        if not inhibit_config.get("enabled", True):
            self.log_action("Skipping ac-inhibit.service (ac_inhibit disabled)")
            self.remove_file(TARGET_FILES["ac_inhibit_service"])
            return

        self.log_action("Creating ac-inhibit.service")

        rendered = render_template("ac-inhibit.service.tpl", {})

        self.write_file(TARGET_FILES["ac_inhibit_service"], rendered)

    def reload_and_enable_services(self) -> None:
        """Reload systemd, udev and enable services."""
        services_config = self.config.get("services", {})
        auto_enable = services_config.get("auto_enable", True)
        auto_start = services_config.get("auto_start", True)

        self.log_action("Reloading system configurations...")

        self.run_cmd(["systemctl", "daemon-reload"])
        self.log_action("systemd daemon reloaded")

        self.run_cmd(["udevadm", "control", "--reload-rules"])
        self.run_cmd(["udevadm", "trigger"])
        self.log_action("udev rules reloaded")

        self.run_cmd(["systemctl", "reload", "systemd-logind"])
        self.log_action("systemd-logind reloaded")

        inhibit_config = self.config.get("ac_inhibit", {})
        if inhibit_config.get("enabled", True):
            if auto_enable:
                self.run_cmd(["systemctl", "enable", "ac-inhibit.service"])
                self.log_action("ac-inhibit.service enabled")

            if auto_start:
                self.run_cmd(["systemctl", "restart", "ac-inhibit.service"])
                self.log_action("ac-inhibit.service started")
        else:
            self.run_cmd(["systemctl", "stop", "ac-inhibit.service"], check=False)
            self.run_cmd(["systemctl", "disable", "ac-inhibit.service"], check=False)
            self.log_action("ac-inhibit.service stopped and disabled")

    def verify_installation(self) -> None:
        """Verify the installation."""
        self.log_action("Verifying installation...")

        result = self.run_cmd(["grep", "-E", "^(IdleAction|IdleActionSec)", str(TARGET_FILES["logind_dropin"])])
        if result.returncode == 0:
            self.log_action("logind drop-in configured:")
            for line in result.stdout.strip().split("\n"):
                self.log_action(f"  {line}")
        else:
            self.log_action("logind drop-in not found")

        lid_config = self.config.get("lid_close_suspend", {})
        if lid_config.get("enabled", True):
            if TARGET_FILES["power_logic"].exists():
                self.log_action("power-logic.sh exists")
            else:
                self.log_action("power-logic.sh missing")

            if TARGET_FILES["udev_rules"].exists():
                self.log_action("udev rules exist")
            else:
                self.log_action("udev rules missing")
        else:
            self.log_action("lid_close_suspend disabled - skipping power-logic.sh verification")

        inhibit_config = self.config.get("ac_inhibit", {})
        if inhibit_config.get("enabled", True):
            if TARGET_FILES["ac_inhibit_script"].exists():
                self.log_action("ac-inhibit.sh exists")
            else:
                self.log_action("ac-inhibit.sh missing")

            result = self.run_cmd(["systemctl", "is-active", "ac-inhibit.service"], check=False)
            if result.stdout.strip() == "active":
                self.log_action("ac-inhibit.service running")
            else:
                self.log_action("ac-inhibit.service not running")

            result = self.run_cmd(["systemd-inhibit", "--list", "--no-pager"], check=False)
            if "idle" in result.stdout:
                for line in result.stdout.split("\n"):
                    if "idle" in line.lower():
                        self.log_action(f"Idle inhibit active: {line.split()[0]}")
                        break
            else:
                self.log_action("No idle inhibit currently active (may be on battery)")
        else:
            self.log_action("ac_inhibit disabled - skipping ac-inhibit verification")

    def run(self) -> None:
        """Run the full installation."""
        self.ensure_sudo()

        self.configure_logind()
        self.create_power_logic_script()
        self.create_udev_rules()
        self.create_ac_inhibit_script()
        self.create_ac_inhibit_service()
        self.reload_and_enable_services()
        self.verify_installation()


def main():
    parser = argparse.ArgumentParser(
        description="Install hybrid power management configuration"
    )
    parser.add_argument(
        "--config", "-c",
        type=Path,
        default=DEFAULT_CONFIG,
        help=f"Path to TOML config file (default: {DEFAULT_CONFIG})"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Render templates and print to stdout without writing files"
    )
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(message)s")

    config = load_config(args.config)

    log.info("=" * 60)
    log.info("Hybrid Power Management Installer")
    log.info("=" * 60)
    log.info(f"Config: {args.config}")
    log.info(f"Templates: {TEMPLATES_DIR}")
    if args.dry_run:
        log.info("Mode: DRY-RUN (no files will be written)")
    log.info("")

    installer = PowerConfigInstaller(config, dry_run=args.dry_run)
    installer.run()

    log.info("")
    if args.dry_run:
        log.info("✓ Dry-run complete!")
    else:
        log.info("✓ Installation complete!")


if __name__ == "__main__":
    main()
