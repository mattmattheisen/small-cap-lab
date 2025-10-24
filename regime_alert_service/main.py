#!/usr/bin/env python3
"""
Regime-Alert Service - Main Entry Point
Monitors ticker universe for HMM regime changes and sends alerts
"""

import os
import argparse
import time
from datetime import datetime
from regime_service import RegimeService
from scheduler import Scheduler
from logger import RunLogger


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description='Regime-Alert Service: Monitor ticker regimes and send alerts'
    )
    parser.add_argument(
        '--force-alert',
        action='store_true',
        help='Send alert even if no regime changes'
    )
    parser.add_argument(
        '--universe',
        type=str,
        default='config/universe.txt',
        help='Path to universe file (default: config/universe.txt)'
    )
    parser.add_argument(
        '--skip-schedule-check',
        action='store_true',
        help='Run immediately without checking scheduled times or day-of-week'
    )
    
    args = parser.parse_args()
    
    # Initialize components
    logger = RunLogger()
    scheduler = Scheduler(timezone=os.getenv('TIMEZONE', 'America/Chicago'))
    service = RegimeService(universe_path=args.universe)
    
    # Check if should run (unless override)
    if not args.skip_schedule_check:
        should_run, reason = scheduler.should_run()
        if not should_run:
            print(reason)
            logger.log_run(0, 0, 0.0, error=reason)
            return
    
    # Start timing
    start_time = time.time()
    
    try:
        print(f"Starting regime detection at {datetime.now().isoformat()}")
        
        # Main detection logic
        today_df, changes_df = service.detect_regimes()
        
        # Write outputs
        service.write_outputs(today_df, changes_df)
        
        # Send alert
        service.send_alert(changes_df, force=args.force_alert)
        
        # Print summary
        service.print_summary(today_df, changes_df)
        
        # Calculate runtime
        runtime = time.time() - start_time
        
        # Log successful run
        logger.log_run(len(today_df), len(changes_df), runtime)
        
        # Mark run complete (for duplicate prevention)
        if not args.skip_schedule_check:
            scheduler.mark_run_complete()
        
        print(f"\nCompleted in {runtime:.2f} seconds")
        
    except Exception as e:
        runtime = time.time() - start_time
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"ERROR: {error_msg}")
        logger.log_run(0, 0, runtime, error=error_msg)
        raise


if __name__ == '__main__':
    main()
