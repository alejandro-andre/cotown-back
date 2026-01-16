sed -e 's/ISA/XSA/g' -e 's/ISC/XSC/g' -e 's/Stabilised/Business Plan/g' csv/income_stabilised.csv > csv/income_business_plan.csv
sed -e 's/OSA/XSA/g' -e 's/OSC/XSC/g' -e 's/Stabilised/Business Plan/g' csv/occupancy_stabilised.csv > csv/occupancy_business_plan.csv
sed -e 's/BDR/XDR/g' -e 's/Real/Business Plan/g' csv/beds_real.csv > csv/beds_business_plan.csv

