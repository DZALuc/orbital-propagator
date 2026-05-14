# 🚀 VTK Simulators - Quick Start Guide

## Instalación

```bash
pip install vtk numpy-stl pillow --break-system-packages
```

## Lanzar Simuladores

### Opción 1: Desde Calculadora (Más Fácil)

```bash
python examples/mission_calculator.py
```

Selecciona:
- `[10]` Para lanzar transferencia Hohmann con misión predefinida
- `[11]` Para menú completo de simuladores

### Opción 2: Directo

```bash
# Simulador completo (RECOMENDADO)
python examples/vtk_demos/hohmann_advanced.py

# Con altitudes custom
python examples/vtk_demos/hohmann_advanced.py 400 20200
```

## Controles

### Teclado
- `[+]` / `[-]` - Aumentar/disminuir velocidad
- `[SPACE]` - Pausar/Reanudar
- `[R]` - Reset
- `[T]` - Toggle trail (estela)
- `[V]` - Toggle velocity vector
- `[Z]` - Toggle auto-zoom
- `[Q]` - Salir

### Mouse
- **Click izquierdo + arrastrar** - Rotar vista
- **Scroll** - Zoom in/out
- **Click derecho + arrastrar** - Pan

## Fases de la Simulación

1. **Fase Inicial** (Azul)
   - Satélite orbita en LEO
   - Completa 1 órbita
   - Panel: "ÓRBITA INICIAL (LEO)"

2. **Transferencia** (Naranja)
   - Aplica ΔV₁ en periapsis
   - Sigue trayectoria elíptica
   - Panel: "TRANSFERENCIA HOHMANN"

3. **Fase Final** (Verde)
   - Aplica ΔV₂ en apoapsis
   - Continúa en órbita GEO
   - Panel: "ÓRBITA FINAL (GEO)"

## Solución de Problemas

### El simulador no abre

Verifica instalación:
```bash
pip list | grep vtk
```

### No se ve la textura

La textura debe estar en:
models/textures/earth_day.jpg

Si no existe, el simulador usa color azul automáticamente.

### Errores de import

Asegúrate de estar en el directorio raíz:
```bash
cd ~/orbital-propagator
python examples/vtk_demos/hohmann_advanced.py
```

## Características por Simulador

| Simulador | Tierra | Animación | Estela | Auto-zoom | Complejidad |
|-----------|--------|-----------|--------|-----------|-------------|
| test_orbit_animation.py | ❌ | ✅ | ❌ | ❌ | Básico |
| test_textured_earth.py | ✅ | ✅ | ❌ | ❌ | Medio |
| hohmann_transfer_animated.py | ✅ | ✅ | ❌ | ❌ | Medio |
| hohmann_advanced.py | ✅ | ✅ | ✅ | ✅ | Completo |

## Tips

1. **Velocidad inicial:** Empieza con velocidad 50x, ajusta según necesites
2. **Vista recomendada:** Posición isométrica (default) es la mejor
3. **Estela:** Actívala `[T]` para ver trayectoria completa
4. **Pausa:** Usa `[SPACE]` para examinar detalles
5. **Screenshots:** Pausa y captura con tu herramienta de OS

## Misiones Predefinidas

Desde `[10]` en calculadora:

1. **LEO → GEO** (400 → 35,786 km)
   - Transferencia clásica
   - ~3,857 m/s ΔV total
   - ~5.3 horas

2. **LEO → MEO GPS** (400 → 20,200 km)
   - Órbita GPS
   - ~2,800 m/s ΔV total
   - ~2.8 horas

3. **Starlink → GEO** (550 → 35,786 km)
   - Desde órbita Starlink
   - ~3,780 m/s ΔV total
   - ~5.2 horas

4. **Custom**
   - Tú defines altitudes
   - Cualquier combinación válida

## Comandos Útiles

```bash
# Ver todos los simuladores
ls examples/vtk_demos/

# Ejecutar con Python específico
python3 examples/vtk_demos/hohmann_advanced.py

# Con argumentos
python examples/vtk_demos/hohmann_advanced.py 1000 42164
```

## Contacto

Para bugs o sugerencias:
- GitHub: https://github.com/DZALuc/orbital-propagator
- Issues: https://github.com/DZALuc/orbital-propagator/issues