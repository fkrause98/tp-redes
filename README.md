# TP Teoría de las comunicaciones.

## Setup
Prerequisitos: Tener instalado python 3 y make.
1. Crear virtualenv: 
```bash
make virtualenv
```
2. Entrar al virtualenv
```bash
source ./virtualenv/bin/activate
```
3. Instalar dependencias:
```bash
make deps
```
4. Intentar correr el script:
```bash
chmod +x traceroute.py
sudo $(which python3) ./traceroute.py 157.92.0.1
```
## Mediciones

Para tomar mediciones, se usa el script ```test.sh```, mediante:
```bash
make measurements
```
