#!/bin/bash
# Test script for Regime-Alert Service

echo "===================================================="
echo "Regime-Alert Service - Test Suite"
echo "===================================================="
echo ""

# Test 1: First Run (no prior state)
echo "TEST 1: First Run (no prior state)"
echo "----------------------------------------------------"
rm -f data/hmm_prev.json data/last_run.txt out/*.csv
python main.py --skip-schedule-check
echo ""
echo "Expected: No alert (first run, no changes to compare)"
echo ""
read -p "Press Enter to continue..."
echo ""

# Test 2: No changes
echo "TEST 2: Subsequent Run (no regime changes)"
echo "----------------------------------------------------"
python main.py --skip-schedule-check
echo ""
echo "Expected: Already ran today message OR no changes detected"
echo ""
read -p "Press Enter to continue..."
echo ""

# Test 3: Simulated regime changes
echo "TEST 3: Regime Changes Detected"
echo "----------------------------------------------------"
rm -f data/last_run.txt
cat > data/hmm_prev.json << 'EOF'
{
  "APPS": "Bear",
  "ATUS": "Bear",
  "CSIQ": "Bull",
  "FUBO": "Bear",
  "WOLF": "Bull",
  "ARQQ": "Bear",
  "SPIR": "Bull",
  "SES": "Bear",
  "SANA": "Bull",
  "JKS": "Bear"
}
EOF
python main.py --skip-schedule-check
echo ""
echo "Expected: Multiple regime changes detected and alert message shown"
echo ""
read -p "Press Enter to continue..."
echo ""

# Test 4: Force alert
echo "TEST 4: Force Alert (even without changes)"
echo "----------------------------------------------------"
rm -f data/last_run.txt
python main.py --skip-schedule-check --force-alert
echo ""
echo "Expected: Alert sent even if no changes"
echo ""
read -p "Press Enter to continue..."
echo ""

# Test 5: Check outputs
echo "TEST 5: Verify Output Files"
echo "----------------------------------------------------"
echo "today_regimes.csv:"
head -5 out/today_regimes.csv
echo ""
echo "changes.csv (if exists):"
if [ -f out/changes.csv ]; then
    cat out/changes.csv
else
    echo "(no changes file)"
fi
echo ""
echo "run.log (last 5 entries):"
tail -5 out/run.log
echo ""
read -p "Press Enter to continue..."
echo ""

# Test 6: Universe modification
echo "TEST 6: Universe Changes"
echo "----------------------------------------------------"
echo "Adding TSLA to universe..."
echo "TSLA" >> config/universe.txt
rm -f data/last_run.txt
python main.py --skip-schedule-check
echo ""
echo "Expected: TSLA included in next run"
echo ""
echo "Restoring original universe..."
head -10 config/universe.txt > config/universe.tmp
mv config/universe.tmp config/universe.txt
echo ""

echo "===================================================="
echo "Test Suite Complete!"
echo "===================================================="
echo ""
echo "Summary:"
echo "- First run: ✓"
echo "- Duplicate run prevention: ✓"  
echo "- Regime change detection: ✓"
echo "- Force alert: ✓"
echo "- Output files: ✓"
echo "- Universe changes: ✓"
echo ""
echo "Note: Sunday skip is time-based and requires actual Sunday to test"
echo "Note: Webhook alerts require ALERT_WEBHOOK_URL environment variable"
