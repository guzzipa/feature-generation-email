#!/usr/bin/env python3
"""
Local Scheduler for Auto-Improvement
Runs auto-improvement tasks on a schedule (alternative to GitHub Actions)

Usage:
    python scheduler.py start    # Start scheduler daemon
    python scheduler.py stop     # Stop scheduler
    python scheduler.py status   # Check status
    python scheduler.py run-now  # Run all tasks immediately

Cron Alternative:
    # Add to crontab for manual scheduling
    0 9 * * 1 cd /path/to/project && python auto_improve.py discover
    0 10 * * 1 cd /path/to/project && python auto_improve.py health
    0 11 * * 1 cd /path/to/project && python auto_improve.py optimize

Version: 5.0.0
"""

import schedule
import time
import logging
import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutoImproveScheduler:
    """
    Local scheduler for running auto-improvement tasks.
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).absolute()
        self.pid_file = self.project_root / "scheduler.pid"
        self.log_dir = self.project_root / "logs" / "auto_improve"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def run_task(self, task_name: str, command: list) -> bool:
        """
        Run a single auto-improvement task.
        """
        logger.info(f"🚀 Running task: {task_name}")

        log_file = self.log_dir / f"{task_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        try:
            with open(log_file, 'w') as f:
                result = subprocess.run(
                    command,
                    cwd=self.project_root,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    timeout=300  # 5 minutes max
                )

            if result.returncode == 0:
                logger.info(f"   ✅ {task_name} completed successfully")
                return True
            else:
                logger.error(f"   ❌ {task_name} failed with code {result.returncode}")
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"   ⏱️ {task_name} timed out after 5 minutes")
            return False
        except Exception as e:
            logger.error(f"   ❌ {task_name} error: {str(e)}")
            return False

    def discover_sources(self):
        """Weekly task: Discover new data sources."""
        logger.info("=" * 60)
        logger.info("🔍 WEEKLY SOURCE DISCOVERY")
        logger.info("=" * 60)

        success = self.run_task(
            "source_discovery",
            ["python", "auto_improve.py", "discover"]
        )

        if success:
            self._notify("Source Discovery Complete", "Check discoveries/ folder for new APIs")

    def health_check(self):
        """Daily task: Check system health."""
        logger.info("=" * 60)
        logger.info("🏥 DAILY HEALTH CHECK")
        logger.info("=" * 60)

        success = self.run_task(
            "health_check",
            ["python", "auto_improve.py", "health"]
        )

        if not success:
            self._notify("Health Check Failed", "One or more APIs are unhealthy", priority="high")

    def optimize_analysis(self):
        """Weekly task: Run optimization analysis."""
        logger.info("=" * 60)
        logger.info("⚡ WEEKLY OPTIMIZATION ANALYSIS")
        logger.info("=" * 60)

        success = self.run_task(
            "optimization",
            ["python", "auto_improve.py", "optimize"]
        )

        if success:
            self._notify("Optimization Analysis Complete", "Review optimization suggestions")

    def analyze_features(self):
        """Monthly task: Analyze data patterns."""
        logger.info("=" * 60)
        logger.info("📊 MONTHLY FEATURE ANALYSIS")
        logger.info("=" * 60)

        success = self.run_task(
            "feature_analysis",
            ["python", "auto_improve.py", "analyze"]
        )

        if success:
            self._notify("Feature Analysis Complete", "New feature opportunities identified")

    def cleanup_old_logs(self):
        """Weekly task: Clean up old logs."""
        logger.info("🗑️ Cleaning up old logs...")

        try:
            # Keep last 30 days of logs
            cutoff = datetime.now().timestamp() - (30 * 24 * 60 * 60)

            for log_file in self.log_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff:
                    log_file.unlink()
                    logger.info(f"   Deleted old log: {log_file.name}")

        except Exception as e:
            logger.error(f"Error cleaning logs: {e}")

    def backup_discoveries(self):
        """Weekly task: Backup discovery reports."""
        logger.info("💾 Backing up discovery reports...")

        try:
            discoveries_dir = self.project_root / "discoveries"
            backup_dir = self.project_root / "backups" / datetime.now().strftime('%Y%m%d')
            backup_dir.mkdir(parents=True, exist_ok=True)

            if discoveries_dir.exists():
                import shutil
                for file in discoveries_dir.glob("*.json"):
                    shutil.copy2(file, backup_dir / file.name)
                    logger.info(f"   Backed up: {file.name}")

        except Exception as e:
            logger.error(f"Error backing up: {e}")

    def _notify(self, title: str, message: str, priority: str = "normal"):
        """
        Send notification (extend this for Slack, email, etc).
        """
        logger.info(f"📬 Notification: {title} - {message}")

        # TODO: Integrate with Slack, Discord, email, etc
        # Example for macOS notification:
        try:
            if sys.platform == "darwin":
                subprocess.run([
                    "osascript", "-e",
                    f'display notification "{message}" with title "{title}"'
                ])
        except:
            pass

    def setup_schedule(self):
        """
        Configure the task schedule.
        """
        logger.info("📅 Setting up schedule...")

        # Daily tasks
        schedule.every().day.at("09:00").do(self.health_check)

        # Weekly tasks (Monday)
        schedule.every().monday.at("09:00").do(self.discover_sources)
        schedule.every().monday.at("10:00").do(self.optimize_analysis)
        schedule.every().monday.at("11:00").do(self.cleanup_old_logs)
        schedule.every().monday.at("12:00").do(self.backup_discoveries)

        # Monthly tasks (First day of month)
        schedule.every().month.at("09:00").do(self.analyze_features)

        logger.info("✅ Schedule configured:")
        logger.info("   • Daily 09:00 - Health Check")
        logger.info("   • Monday 09:00 - Source Discovery")
        logger.info("   • Monday 10:00 - Optimization Analysis")
        logger.info("   • Monday 11:00 - Log Cleanup")
        logger.info("   • Monthly 09:00 - Feature Analysis")

    def run_all_now(self):
        """
        Run all tasks immediately (for testing).
        """
        logger.info("🏃 Running all tasks immediately...")

        self.health_check()
        time.sleep(2)

        self.discover_sources()
        time.sleep(2)

        self.optimize_analysis()
        time.sleep(2)

        self.analyze_features()
        time.sleep(2)

        logger.info("✅ All tasks completed")

    def start(self):
        """
        Start the scheduler daemon.
        """
        # Check if already running
        if self.pid_file.exists():
            logger.error("❌ Scheduler already running (or stale PID file)")
            return

        # Write PID file
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))

        logger.info("🚀 Starting Auto-Improve Scheduler...")
        logger.info(f"   PID: {os.getpid()}")
        logger.info(f"   Project Root: {self.project_root}")
        logger.info(f"   Log Directory: {self.log_dir}")

        self.setup_schedule()

        try:
            logger.info("⏰ Scheduler running. Press Ctrl+C to stop.")

            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            logger.info("\n🛑 Stopping scheduler...")
            self.stop()

        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")
            self.stop()

    def stop(self):
        """
        Stop the scheduler.
        """
        if self.pid_file.exists():
            self.pid_file.unlink()
            logger.info("✅ Scheduler stopped")
        else:
            logger.warning("⚠️ Scheduler was not running")

    def status(self):
        """
        Check scheduler status.
        """
        if self.pid_file.exists():
            with open(self.pid_file) as f:
                pid = f.read().strip()

            logger.info(f"✅ Scheduler is running (PID: {pid})")

            # Show next scheduled runs
            logger.info("\n📅 Next scheduled runs:")
            for job in schedule.get_jobs():
                logger.info(f"   • {job.next_run} - {job.job_func.__name__}")

        else:
            logger.info("❌ Scheduler is not running")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Local Scheduler for Auto-Improvement"
    )

    parser.add_argument(
        'command',
        choices=['start', 'stop', 'status', 'run-now'],
        help='Command to execute'
    )

    parser.add_argument(
        '--project-root',
        default='.',
        help='Project root directory'
    )

    args = parser.parse_args()

    scheduler = AutoImproveScheduler(project_root=args.project_root)

    if args.command == 'start':
        scheduler.start()
    elif args.command == 'stop':
        scheduler.stop()
    elif args.command == 'status':
        scheduler.status()
    elif args.command == 'run-now':
        scheduler.run_all_now()


if __name__ == "__main__":
    main()
