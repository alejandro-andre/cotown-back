#!/bin/bash
DATE_DIR=$(date +%Y-%m-%d)
BACKUP_DIR="csv/$DATE_DIR"

mkdir -p "$BACKUP_DIR"

sed -e '/^MP/d' -e 's/^ISA/XSA/' -e 's/^ISC/XSC/' -e 's/Stabilised/Business Plan/g' csv/income_stabilised.csv > csv/income_business_plan.csv
sed -e 's/^OSA/XSA/' -e 's/^OSC/XSC/' -e 's/Stabilised/Business Plan/g' csv/occupancy_stabilised.csv > csv/occupancy_business_plan.csv
sed -e 's/^BDR/XDR/' -e 's/Real/Business Plan/g' csv/beds_real.csv > csv/beds_business_plan.csv

cp csv/income_business_plan.csv csv/occupancy_business_plan.csv csv/beds_business_plan.csv "$BACKUP_DIR/"