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
import re
from pathlib import Path
from string import Template

# Set up logging
log = logging.getLogger(__name__)

# Paths
SCRIPT_DIR = Path(__file__).parent
DEFAULT_CONFIG = SCRIPT_DIR / "power-config.toml"
TEMPLATES_DIR = SCRIPT_DIR / "templates"

TARGET_FILES = {
    "logind": Path("/etc/systemd/logind.conf"),
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


def run_cmd(cmd: list, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command."""
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


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

    def ensure_sudo(self) -> None:
        """Ensure script is running as root."""
        if self.dry_run:
            log.debug("Skipping sudo check (dry-run)")
            return
        if os.geteuid() != 0:
            log.error("This script must be run as root (use sudo)")
            sys.exit(1)

    def print_dry_run(self, target: Path, content: str) -> None:
        """Print rendered content for dry-run mode."""
        print(f"\n{'=' * 60}")
        print(f"# Target: {target}")
        print(f"{'=' * 60}")
        print(content.rstrip())
        print()

    def configure_logind(self) -> None:
        """Configure idle timer in logind.conf using template."""
        idle_config = self.config.get("idle", {})

        action = idle_config.get("action", "suspend")
        timeout = idle_config.get("timeout_minutes", 20)

        log.debug(f"Configuring logind.conf: IdleAction={action}, IdleActionSec={timeout}min")

        # Render template
        rendered = render_template("logind.conf.tpl", {
            "idle_action": action,
            "idle_timeout": timeout
        })

        if self.dry_run:
            self.print_dry_run(TARGET_FILES["logind"], rendered)
            return

        # Read current logind.conf content
        target = TARGET_FILES["logind"]
        current_content = target.read_text() if target.exists() else ""

        # Update or append settings in logind.conf
        for line in rendered.strip().split("\n"):
            if line.startswith("#") or not line.strip():
                continue

            key = line.split("=")[0]
            if key in current_content:
                # Replace existing line (commented or not)
                pattern = rf"^#?{key}=.*$"
                current_content = re.sub(pattern, line, current_content, flags=re.MULTILINE)
            else:
                # Append new setting
                current_content += f"\n{line}\n"

        target.write_text(current_content)
        log.debug("logind.conf updated")

    def create_power_logic_script(self) -> None:
        """Create the power-logic.sh script using template."""
        lid_config = self.config.get("lid_close_suspend", {})

        if not lid_config.get("enabled", True):
            log.debug("Skipping power-logic.sh (lid_close_suspend disabled)")
            if not self.dry_run:
                target = TARGET_FILES["power_logic"]
                if target.exists():
                    target.unlink()
                    log.debug("Removed existing power-logic.sh")
            return

        on_battery = lid_config.get("on_battery", True)
        require_no_ext = lid_config.get("require_no_external_monitor", True)

        log.debug(f"Creating power-logic.sh (on_battery={on_battery}, require_no_external_monitor={require_no_ext})")

        # Build condition string
        conditions = []
        if on_battery:
            conditions.append('[ "$ON_AC" -eq 0 ]')
        if require_no_ext:
            conditions.append('[ "$EXT_SCREEN" -eq 0 ]')

        condition_str = " && ".join(conditions) if conditions else "true"

        rendered = render_template("power-logic.sh.tpl", {"condition_str": condition_str})

        if self.dry_run:
            self.print_dry_run(TARGET_FILES["power_logic"], rendered)
            return

        target = TARGET_FILES["power_logic"]
        target.write_text(rendered)
        target.chmod(0o755)
        log.debug("power-logic.sh created")

    def create_udev_rules(self) -> None:
        """Create udev rules using template."""
        lid_config = self.config.get("lid_close_suspend", {})

        if not lid_config.get("enabled", True):
            log.debug("Skipping udev rules (lid_close_suspend disabled)")
            if not self.dry_run:
                target = TARGET_FILES["udev_rules"]
                if target.exists():
                    target.unlink()
                    log.debug("Removed existing udev rules")
            return

        log.debug("Creating udev rules")

        rendered = render_template("udev-rules.rules.tpl", {})

        if self.dry_run:
            self.print_dry_run(TARGET_FILES["udev_rules"], rendered)
            return

        target = TARGET_FILES["udev_rules"]
        target.write_text(rendered)
        log.debug("udev rules created")

    def create_ac_inhibit_script(self) -> None:
        """Create the ac-inhibit.sh script using template."""
        inhibit_config = self.config.get("ac_inhibit", {})

        if not inhibit_config.get("enabled", True):
            log.debug("Skipping ac-inhibit.sh (ac_inhibit disabled)")
            if not self.dry_run:
                target = TARGET_FILES["ac_inhibit_script"]
                if target.exists():
                    target.unlink()
                    log.debug("Removed existing ac-inhibit.sh")
            return

        interval = inhibit_config.get("check_interval_seconds", 60)

        log.debug(f"Creating ac-inhibit.sh (check_interval={interval}s)")

        rendered = render_template("ac-inhibit.sh.tpl", {"check_interval": interval})

        if self.dry_run:
            self.print_dry_run(TARGET_FILES["ac_inhibit_script"], rendered)
            return

        target = TARGET_FILES["ac_inhibit_script"]
        target.write_text(rendered)
        target.chmod(0o755)
        log.debug("ac-inhibit.sh created")

    def create_ac_inhibit_service(self) -> None:
        """Create the systemd service for ac-inhibit using template."""
        inhibit_config = self.config.get("ac_inhibit", {})

        if not inhibit_config.get("enabled", True):
            log.debug("Skipping ac-inhibit.service (ac_inhibit disabled)")
            if not self.dry_run:
                target = TARGET_FILES["ac_inhibit_service"]
                if target.exists():
                    target.unlink()
                    log.debug("Removed existing ac-inhibit.service")
            return

        log.debug("Creating ac-inhibit.service")

        rendered = render_template("ac-inhibit.service.tpl", {})

        if self.dry_run:
            self.print_dry_run(TARGET_FILES["ac_inhibit_service"], rendered)
            return

        target = TARGET_FILES["ac_inhibit_service"]
        target.write_text(rendered)
        log.debug("ac-inhibit.service created")

    def reload_and_enable_services(self) -> None:
        """Reload systemd, udev and enable services."""
        if self.dry_run:
            log.debug("Skipping service reload (dry-run)")
            return

        services_config = self.config.get("services", {})
        auto_enable = services_config.get("auto_enable", True)
        auto_start = services_config.get("auto_start", True)

        log.debug("Reloading system configurations...")

        run_cmd(["systemctl", "daemon-reload"])
        log.debug("systemd daemon reloaded")

        run_cmd(["udevadm", "control", "--reload-rules"])
        run_cmd(["udevadm", "trigger"])
        log.debug("udev rules reloaded")

        run_cmd(["systemctl", "restart", "systemd-logind"])
        log.debug("systemd-logind restarted")

        inhibit_config = self.config.get("ac_inhibit", {})
        if inhibit_config.get("enabled", True):
            if auto_enable:
                run_cmd(["systemctl", "enable", "ac-inhibit.service"])
                log.debug("ac-inhibit.service enabled")

            if auto_start:
                run_cmd(["systemctl", "restart", "ac-inhibit.service"])
                log.debug("ac-inhibit.service started")
        else:
            run_cmd(["systemctl", "stop", "ac-inhibit.service"], check=False)
            run_cmd(["systemctl", "disable", "ac-inhibit.service"], check=False)
            log.debug("ac-inhibit.service stopped and disabled")

    def verify_installation(self) -> None:
        """Verify the installation."""
        if self.dry_run:
            log.debug("Skipping verification (dry-run)")
            return

        log.debug("Verifying installation...")

        result = run_cmd(["grep", "-E", "^(IdleAction|IdleActionSec)", str(TARGET_FILES["logind"])])
        if result.returncode == 0:
            log.debug("logind.conf configured:")
            for line in result.stdout.strip().split("\n"):
                log.debug(f"  {line}")
        else:
            log.debug("logind.conf not configured")

        lid_config = self.config.get("lid_close_suspend", {})
        if lid_config.get("enabled", True):
            if TARGET_FILES["power_logic"].exists():
                log.debug("power-logic.sh exists")
            else:
                log.debug("power-logic.sh missing")

            if TARGET_FILES["udev_rules"].exists():
                log.debug("udev rules exist")
            else:
                log.debug("udev rules missing")
        else:
            log.debug("lid_close_suspend disabled - skipping power-logic.sh verification")

        inhibit_config = self.config.get("ac_inhibit", {})
        if inhibit_config.get("enabled", True):
            if TARGET_FILES["ac_inhibit_script"].exists():
                log.debug("ac-inhibit.sh exists")
            else:
                log.debug("ac-inhibit.sh missing")

            result = run_cmd(["systemctl", "is-active", "ac-inhibit.service"], check=False)
            if result.stdout.strip() == "active":
                log.debug("ac-inhibit.service running")
            else:
                log.debug("ac-inhibit.service not running")

            result = run_cmd(["systemd-inhibit", "--list", "--no-pager"], check=False)
            if "idle" in result.stdout:
                for line in result.stdout.split("\n"):
                    if "idle" in line.lower():
                        log.debug(f"Idle inhibit active: {line.split()[0]}")
                        break
            else:
                log.debug("No idle inhibit currently active (may be on battery)")
        else:
            log.debug("ac_inhibit disabled - skipping ac-inhibit verification")

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
