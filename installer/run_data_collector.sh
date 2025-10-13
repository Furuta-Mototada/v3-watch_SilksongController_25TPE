#!/bin/bash
# Silksong Motion Controller - Data Collection Tool
# This script runs the guided data collection procedure for IMU gestures

echo "========================================"
echo " IMU Gesture Data Collection - Phase II"
echo "========================================"
echo ""
echo "This tool will guide you through collecting high-quality"
echo "IMU gesture data from your Pixel Watch."
echo ""
echo "Before starting, make sure:"
echo "1. Your Pixel Watch app is installed and ready"
echo "2. Watch and computer are on the same WiFi network"
echo "3. You have cleared space for natural movements"
echo "4. You're ready to perform gestures for 15-30 minutes"
echo ""
echo "Press Ctrl+C to stop data collection at any time"
echo ""

python3 ../src/data_collector.py
