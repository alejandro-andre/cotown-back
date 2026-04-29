clear

$env:COTOWN_ENV="production"

python test.py --id 9958 --type B2C --template "B2C Piso.md"
python test.py --id 9958 --type B2C --contract services --template "Servicios.md"
python test.py --id 9986 --type B2C --template "B2C Habitacion.md"
python test.py --id 9986 --type B2C --contract services --template "Servicios.md"

python test.py --id 281 --type B2B --template "B2B Piso.md"
python test.py --id 701 --type B2B --template "B2B Habitacion.md"
