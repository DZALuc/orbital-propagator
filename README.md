# 🛰️ Propagador Orbital

Simulador de mecánica orbital en Python para análisis de trayectorias satelitales y planificación de misiones.

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/estado-activo-success)
![Version](https://img.shields.io/badge/version-v2.0.0-blue)
![Projects](https://img.shields.io/badge/proyectos-2%2F7-orange)
## 📋 Descripción General

Propagador orbital numérico de alta precisión que implementa mecánica clásica de dos cuerpos con soporte para perturbaciones. Diseñado para aplicaciones de ingeniería aeroespacial, análisis de misiones y propósitos educativos.

**Características Principales:**
- ✅ Propagación orbital Kepleriana (problema de dos cuerpos)
- ✅ **Soporte para órbitas circulares y elípticas**
- ✅ **Perturbación J2 (achatamiento terrestre)**
- ✅ **Conversión Cartesiano ↔ Kepleriano (elementos orbitales)**
- ✅ Integración numérica de alta precisión (DOP853, rtol=1e-10)
- ✅ Visualización de trayectorias en 2D/3D
- ✅ Análisis y validación de elementos orbitales
- ✅ Verificación de conservación de energía (error relativo < 1e-12)
- 🚧 Extensión para propulsión eléctrica de bajo empuje (planeado)
- 🚧 Validación contra poliastro/GMAT (planeado)

## 🎯 Objetivos del Proyecto

Este proyecto forma parte de un portafolio técnico que demuestra capacidades en:
- Computación científica y métodos numéricos
- Mecánica orbital y astrodinámica
- Mejores prácticas de ingeniería de software
- Documentación técnica y visualización de datos

**Dominio de aplicación objetivo:** Sistemas de propulsión eléctrica para pequeños satélites (CubeSats).

## 🖼️ Visualizaciones

### Proyección Orbital 2D
![Órbita 2D](docs/orbit_2d.png)

### Vista de Trayectoria 3D
![Órbita 3D](docs/orbit_3d.png)

### Análisis de Elementos Orbitales
![Elementos Orbitales](docs/orbital_elements.png)

### Evolución de Componentes de Posición
![Componentes de Posición](docs/position_components.png)

### Efectos de J2 en Elementos Orbitales
![Efectos J2](docs/j2_orbital_elements_evolution.png)

Gráfica de 6 paneles mostrando cómo la perturbación J2 afecta los elementos Keplerianos. Notable:
- **Precesión nodal (RAAN):** -2.9°/día visible
- **Rotación de ápsides (ω):** regresiva para i=65°
- **Oscilaciones periódicas** en a, e, i (física real, no errores numéricos)

### Comparación 3D: Con J2 vs Sin J2
![Comparación J2 3D](docs/j2_comparison_3d.png)

Visualización 3D mostrando divergencia de trayectorias:
- **Azul:** Modelo ideal (sin J2)
- **Roja:** Modelo realista (con J2)
- **Divergencia:** ~3,000 km después de 20 órbitas (33.5 horas)

### Ground Track (Traza Terrestre)
![Ground Track](docs/ground_track.png)

Proyección lat/lon de la órbita sobre la superficie terrestre. Muestra:
- Patrón sinusoidal entre ±51.6° (inclinación orbital)
- Regresión nodal por rotación terrestre (~22°/órbita hacia oeste)
- 5 pasadas completas en 8 horas

## 🚀 Inicio Rápido

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/DZALuc/orbital-propagator.git
cd orbital-propagator

# Crear ambiente virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Uso Básico

```python
from src.propagator import OrbitalPropagator, circular_velocity, orbital_period
from src.visualization import plot_orbit_3d
import numpy as np

# Configurar órbita terrestre a 400 km de altitud (tipo ISS)
R_earth = 6371e3  # metros
altitude = 400e3
r_orbit = R_earth + altitude

# Calcular parámetros de órbita circular
v_circ = circular_velocity(r_orbit)
T = orbital_period(r_orbit)

# Condiciones iniciales
r0 = np.array([r_orbit, 0.0, 0.0])  # Posición [m]
v0 = np.array([0.0, v_circ, 0.0])   # Velocidad [m/s]

# Propagar órbita
prop = OrbitalPropagator()
solution = prop.propagate(r0, v0, t_span=(0, T), dt=60.0)

# Visualizar
plot_orbit_3d(solution)
```

### Ejecutar Ejemplos

```bash
# Probar propagación de órbita circular
python examples/test_circular.py

# Generar visualizaciones
python examples/visualize_orbit.py
```

## 📊 Resultados de Validación

**Órbita Circular LEO (400 km de altitud):**
- Periodo orbital: 92.68 minutos
- Error de cierre de órbita: 51 m (0.00012% de la circunferencia orbital)
- Conservación de energía: Error relativo 7.91×10⁻¹³ (precisión de máquina)

**Órbita Elíptica (400 km × 2000 km):**
- Excentricidad: 0.1058
- Error en perigeo: 2.3 m
- Error en apogeo: 2.4 m
- Conservación de elementos orbitales: < 5×10⁻⁵%

**Perturbación J2:**
- Desviación después de 5 órbitas polares (800 km): 1,225 km
- Ratio J2/Two-body: 0.013% (efecto pequeño pero acumulativo)
- Crítico para predicciones precisas a largo plazo

**Conversión de Elementos Orbitales:**
- 6 casos de prueba: circular, elíptica, polar, inclinada, GEO, Molniya
- Error de conversión (ida y vuelta): < 1×10⁻⁶ m (precisión de máquina)
- Todas las pruebas exitosas

**Método de integración:** DOP853 (Dormand-Prince orden 8) con tolerancias rtol=1e-10, atol=1e-12


### Validación Contra Biblioteca de Referencia

**Poliastro 0.17.0** (biblioteca estándar en astrodinámica Python):

| Test | Resultado |
|------|-----------|
| Conversión de elementos - Circular | ✅ PASS |
| Conversión de elementos - Elíptica | ✅ PASS |
| Conversión de elementos - Polar | ✅ PASS |
| Conservación orbital - Circular (1 periodo) | ✅ PASS |
| Conservación orbital - Elíptica (1 periodo) | ✅ PASS |
| Propagación corta - 10 minutos | ✅ PASS |

**Conclusión:** Implementación validada como físicamente correcta y compatible con estándar de industria.

**Nota técnica:** La validación requiere Python 3.10 (poliastro incompatible con 3.11). Se ejecuta en entorno separado `venv_validation`.


---

## 🚀 Proyecto 2: Low-Thrust Trajectory Optimizer

Optimizador de trayectorias para satélites con **propulsión eléctrica** (bajo empuje continuo). Demuestra cómo motores iónicos/Hall pueden lograr transferencias orbitales con **ahorro masivo de propelente** comparado con propulsión química.

### 🎯 Características

- ✅ **Propagador con empuje continuo** - Integración de ecuaciones con masa variable
- ✅ **Búsqueda automática de tiempo óptimo** - Algoritmo de bisección para transferencias precisas
- ✅ **Comparación química vs eléctrica** - Análisis cuantitativo de trade-offs
- ✅ **Múltiples casos de estudio** - LEO→GEO, LEO→Molniya, estrategias híbridas
- ✅ **Visualizaciones 3D avanzadas** - Trayectorias espiral, evolución temporal, perfiles de empuje

### 📊 Resultados Principales

#### Transferencia LEO → GEO (Órbita Geoestacionaria)

| Método | Propelente | % Masa | Tiempo | Ahorro |
|--------|-----------|--------|--------|--------|
| **Hohmann (químico)** | 51.13 kg | 73.0% | 5 horas | — |
| **Bajo empuje (eléctrico)** | 18.80 kg | 26.9% | 32 días | **63.2%** |

**Precisión alcanzada:** Error de 20 km (0.05%)  
**Factor de mejora:** 2.72x más eficiente

#### Transferencia LEO → Molniya (Órbita Elíptica Rusa)

| Método | Propelente | % Masa | Tiempo | Ahorro |
|--------|-----------|--------|--------|--------|
| **Hohmann (químico)** | 72.91 kg | 97.2% | 1 día | — |
| **Bajo empuje (eléctrico)** | 25.00 kg | 33.3% | 60 días | **65.7%** |

**Factor de mejora:** 2.92x más eficiente

> **Nota:** Con químico se necesitaría 97% de la masa como propelente (físicamente inviable). La propulsión eléctrica hace esta misión **posible**.

### 🔬 Fundamentos Teóricos

**Ecuaciones de movimiento con empuje:**

d²r/dt² = -μ/r³ · r + (T/m) · û
dm/dt = -T / (Isp × g₀)
Donde:
T = empuje (N)
m = masa actual (kg)
û = dirección unitaria de empuje
Isp = impulso específico (s)

**Trade-off fundamental:**

| Tipo | Empuje | Isp | Ventaja | Desventaja |
|------|--------|-----|---------|------------|
| **Químico** | Alto (kN) | Bajo (~300s) | Rápido | Ineficiente |
| **Eléctrico** | Bajo (mN) | Alto (~1500s) | Eficiente | Lento |

**Resultado:** Factor 2-3x menos propelente con eléctrico, pero transferencias de semanas/meses vs horas.

### 💻 Ejemplo de Uso

```python
from src.low_thrust import LowThrustPropagator, SpacecraftModel, tangential_thrust
import numpy as np

# Configurar nave con Hall thruster
spacecraft = SpacecraftModel(
    thrust=0.1,        # 100 mN (típico Hall thruster)
    isp=1500,          # s (impulso específico)
    m_dry=50.0,        # kg (masa seca)
    m_propellant=20.0  # kg (propelente inicial)
)

# Condiciones iniciales (LEO 400 km)
R_earth = 6371e3
r0 = np.array([R_earth + 400e3, 0.0, 0.0])
v0 = np.array([0.0, 7669.0, 0.0])

# Propagar 32 días con empuje tangencial
prop = LowThrustPropagator()
solution = prop.propagate_with_thrust(
    r0, v0, spacecraft.m_total,
    (0, 32*86400),  # 32 días en segundos
    spacecraft,
    tangential_thrust  # Ley de empuje
)

# Analizar resultado
m_final = solution['m'][-1]
propellant_used = spacecraft.m_total - m_final

print(f"Propelente consumido: {propellant_used:.2f} kg")
print(f"Radio final: {np.linalg.norm(solution['r'][-1])/1e3:.1f} km")
```

### 📁 Scripts de Ejemplo

```bash
# Transferencia óptima LEO → GEO
python examples/optimize_leo_to_geo.py

# Órbita Molniya (elíptica inclinada)
python examples/transfer_to_molniya.py

# Comparación de estrategias de empuje
python examples/simple_optimization_demo.py
```

### 🌍 Aplicaciones Reales

Sistemas que **ya usan** propulsión eléctrica:

- **Starlink (SpaceX)** - Hall thrusters para elevar órbitas (~60% ahorro vs químico)
- **Cubesats modernos** - Propulsión iónica para misiones extendidas
- **BepiColombo (ESA)** - Iónica para transfer Tierra→Mercurio
- **Dawn (NASA)** - Primera misión con propulsión iónica a asteroides (Vesta, Ceres)
- **Psyche (NASA)** - Hall thrusters para misión a asteroide metálico

### 📈 Visualizaciones

**Transferencia LEO → GEO (Trayectoria 3D):**

![Transfer LEO-GEO](docs/low_thrust_trajectory_3d.png)

**Evolución Temporal (Altitud, Masa, Velocidad):**

![Análisis Temporal](docs/low_thrust_analysis.png)

**Órbita Molniya (Before/After):**

![Molniya Orbit](docs/molniya_orbit.png)

**Evolución hacia Molniya:**

![Molniya Evolution](docs/molniya_evolution.png)

**Comparación de Estrategias:**

![Estrategias](docs/simple_optimization_comparison.png)

### 🎓 Implicaciones para Diseño de Misiones

**Cuándo usar propulsión eléctrica:**
- ✅ Misiones donde masa es crítica (CubeSats)
- ✅ Transferencias no urgentes (meses disponibles)
- ✅ Misiones de larga duración con múltiples maniobras
- ✅ Cuando hay energía solar abundante

**Cuándo usar químico:**
- ✅ Lanzamientos y maniobras de emergencia
- ✅ Transferencias urgentes (horas/días)
- ✅ Cuando empuje alto es necesario
- ✅ Misiones tripuladas (seguridad/tiempo)

### 📚 Referencias Adicionales

- **Kluever, C.** (2018). *Space Flight Dynamics* - Capítulo sobre Low-Thrust Optimization
- **Betts, J.** (1998). "Survey of Numerical Methods for Trajectory Optimization". *Journal of Guidance, Control, and Dynamics*
- **NASA Glenn Research Center** - Electric Propulsion Database

---



---

## 🧮 Proyecto 3: Mission ΔV Calculator

Calculadora completa de ΔV para planificación de misiones orbitales. Herramienta tipo "navaja suiza" para análisis preliminares.

### 🎯 Características

- ✅ **Hohmann transfers** - Circular, elíptico, cualquier par de órbitas
- ✅ **Bi-elliptic transfers** - Optimización automática, comparación vs Hohmann
- ✅ **Plane changes** - Simple, combinado, análisis de estrategias
- ✅ **Escape & Interplanetary** - Velocidades hiperbólicas, Tierra→Marte
- ✅ **Phasing & Rendezvous** - Encuentros orbitales, constraint de tiempo
- ✅ **Calculadora interactiva** - CLI fácil de usar
- ✅ **Base de datos** - Órbitas comunes, misiones históricas, propulsores
- ✅ **Visualizaciones** - 6 gráficas comparativas profesionales

### 📊 Resultados Destacados

#### Comparación Hohmann vs Bi-elliptic

| Ratio r₂/r₁ | Hohmann | Bi-elliptic | Mejor |
|-------------|---------|-------------|-------|
| 2.0 | 2,182 m/s | 2,411 m/s | Hohmann |
| 11.94 | 4,098 m/s | 4,102 m/s | **Empate** (crítico) |
| 15.0 | 4,114 m/s | 4,005 m/s | **Bi-elliptic** |
| 30.0 | 4,047 m/s | 3,767 m/s | **Bi-elliptic** (-7%) |

**Conclusión:** Bi-elliptic es mejor para ratio > 11.94, pero toma mucho más tiempo.

#### Cambios de Plano (muy costosos)

| Δi | ΔV (LEO) | ΔV (GEO) | Ratio |
|----|----------|----------|-------|
| 10° | 1,337 m/s | 536 m/s | **2.5x** |
| 28.5° | 3,777 m/s | 1,592 m/s | **2.4x** |
| 90° | 10,851 m/s | 4,349 m/s | **2.5x** |

**Implicación:** Siempre hacer cambios de plano en la órbita más alta (menor velocidad).

#### Estrategias para Maniobra Combinada (LEO→GEO + 28.5°)

| Estrategia | ΔV total | Nota |
|------------|----------|------|
| Plano en LEO + Hohmann | 7,634 m/s | ❌ Muy costoso |
| Hohmann + Plano en GEO | 5,370 m/s | ⚠️ Secuencial |
| **Combinado en GEO** | **4,224 m/s** | ✅ **Óptimo** |

**Ahorro:** 3,410 m/s (45%) vs estrategia naive.

#### Rendezvous: Optimización vs Realista

| Escenario | ΔV | Tiempo | Método |
|-----------|-----|--------|--------|
| Optimización pura (min ΔV) | 411 m/s | 8.5 h | max_orbits=5 |
| **Realista (24h disponibles)** | **176 m/s** | **23.9 h** | Usa tiempo inteligentemente |
| Dragon real (ISS) | ~100 m/s | 24-48 h | Lambert + J2 + multi-impulso |

**Factor vs real:** 1.76x (excelente para análisis preliminar).

### 💻 Calculadora Interactiva

```bash
$ python examples/delta_v_calculator.py

======================================================================
               

**Menú:**[1] Hohmann Transfer
[2] Bi-elliptic Transfer
[3] Plane Change
[4] Combined Transfer + Plane Change
[5] Escape Velocity
[6] Interplanetary (Earth → Mars)
[7] Rendezvous Planning
[8] Compare All Strategies
[9] Common Missions (Database)

**Ejemplo de uso:**Selecciona una opción: 1
Altitud inicial (km): 400
Altitud final (km): 35786RESULTADOS:
ΔV₁ (primer impulso):   2,399.4 m/s
ΔV₂ (segundo impulso):  1,457.2 m/s
ΔV total:               3,856.6 m/s
Tiempo de transferencia: 5.29 horasPROPELENTE NECESARIO (estimado):
Químico bajo    (Isp= 300s): 73.0% masa total
Químico alto    (Isp= 450s): 56.1% masa total
Eléctrico       (Isp=1500s): 23.2% masa total

### 🗄️ Base de Datos

**Órbitas disponibles:**
- LEO (200, 400 km), ISS (408 km), Starlink (550 km)
- SSO polar (800 km), GPS (20,200 km)
- GEO (35,786 km), Molniya, Tundra
- Lunar transfer

**Misiones históricas:**
- Apollo 11, Space Shuttle, Voyager, New Horizons
- Dawn, BepiColombo, Mars Science Laboratory

**Sistemas de propulsión:**
- Químico: RL-10, Merlin 1D, Hydrazine
- Eléctrico: SPT-100, NSTAR, Starlink Hall

### 📊 Visualizaciones

**6 gráficas profesionales generadas:**

1. **Hohmann vs Bi-elliptic** - Ratio crítico 11.94
2. **Plane change cost** - Absoluto y relativo
3. **Combined strategies** - LEO→GEO optimización
4. **Phasing trade-off** - ΔV vs tiempo
5. **Mission comparison** - 6 misiones comunes
6. **Propellant mass fraction** - Ecuación Tsiolkovsky

![Delta-V Hohmann vs Bielliptic](docs/delta_v_hohmann_vs_bielliptic.png)
![Plane Change Cost](docs/delta_v_plane_change.png)
![Mission Comparison](docs/delta_v_mission_comparison.png)

### 🎓 Fundamentos Teóricos

**Ecuación de Tsiolkovsky:**ΔV = Isp × g₀ × ln(m_initial / m_final)Para LEO→GEO (ΔV = 3,857 m/s):
Isp=300s  → 73% propelente
Isp=450s  → 56% propelente
Isp=1500s → 23% propelente

**Cambio de plano:**ΔV = 2 × v × sin(Δi/2)Para Δi = 90°:
ΔV = 2v × sin(45°) = 1.414v

**Ratio crítico bi-elliptic:**Teórico: r₂/r₁ > 11.94 (con r_intermediate → ∞)
Práctico: Ganancia marginal (2-7%), tiempo enorme

### 🔬 Validación

**Comparación con valores reales:**

| Misión | Calculado | Real | Factor |
|--------|-----------|------|--------|
| LEO→GEO (Hohmann) | 3,857 m/s | ~3,850 m/s | 1.00x ✓ |
| Shuttle→ISS | 191 m/s | ~150 m/s | 1.27x |
| Dragon→ISS | 176 m/s | ~100 m/s | 1.76x |
| Earth→Mars (C3) | 2,944 m/s | ~2,950 m/s | 0.99x ✓ |

**Precisión:**
- Hohmann: ±1% (excelente)
- Rendezvous: Factor 1.3-2x sobre real (conservador pero útil)
- Interplanetario: ±2% (muy bueno)

**Diferencias explicadas:**
- Modelo simplificado (no J2, Lambert, multi-impulso)
- Límite superior conservador
- Perfecto para análisis preliminar

### 🛠️ Código Desarrolladosrc/
├── delta_v.py              (~700 líneas)
│   ├── hohmann_transfer()
│   ├── bielliptic_transfer()
│   ├── plane_change()
│   ├── combined_plane_change()
│   ├── escape_velocity()
│   ├── interplanetary_hohmann()
│   ├── phasing_orbit()
│   ├── rendezvous_realistic()
│   └── 15+ funciones más
│
└── mission_database.py     (~400 líneas)
├── ORBITS_EARTH (10+ órbitas)
├── PLANETS (5 planetas)
├── MISSIONS (10+ misiones)
└── PROPULSION_SYSTEMS (6 sistemas)examples/
├── mission_calculator.py   (~500 líneas)
│   └── CLI interactiva con 9 opciones
│
└── visualize_delta_v.py    (~400 líneas)
└── 6 funciones de graficación

**Total:** ~2,000 líneas de código funcional

### 📚 Aplicaciones

**Para qué sirve:**
- ✅ Análisis preliminares de misiones
- ✅ Trade-off studies (químico vs eléctrico)
- ✅ Estimación de propelente
- ✅ Comparación de estrategias
- ✅ Educación en astrodinámica

**Para qué NO sirve:**
- ❌ Planning operacional de misiones reales
- ❌ Optimización final (requiere Lambert, J2, etc.)
- ❌ Compliance regulatorio

**Herramientas profesionales equivalentes:**
- GMAT (NASA) - Más completo
- STK (AGI) - Comercial
- Este proyecto - Open source, educativo, análisis rápidos

### 🎯 Valor para Portfolio

**Diferenciador único:**
- Calculadora completa y usable (no solo código)
- Base de datos integrada
- Visualizaciones profesionales
- Comparable a herramientas comerciales (nivel básico)

**Narrativa para entrevistas:**"Desarrollé una calculadora completa de ΔV que cubre todas las
maniobras orbitales estándar: Hohmann, bi-elliptic, cambios de
plano, escape, rendezvous. Incluye una CLI interactiva, base de
datos de misiones históricas, y genera 6 visualizaciones comparativas.
Los resultados están dentro de 1-2x de valores reales, perfecto para
análisis preliminares. Total: 2,000 líneas de código Python funcional."



## 🛠️ Stack Técnico

- **Python 3.11+** - Lenguaje principal
- **NumPy** - Cálculos numéricos y álgebra lineal
- **SciPy** - Integración de EDOs (`solve_ivp` con paso adaptativo)
- **Matplotlib** - Visualización 2D/3D
- **Astropy** - Constantes astronómicas y conversiones de unidades

## 📚 Fundamentos Teóricos

### Problema de Dos Cuerpos

El propagador resuelve la ecuación gravitacional de Newton:

d²r/dt² = -μ/r³ · r

Donde:
- `r` = vector de posición (m)
- `μ` = GM = parámetro gravitacional (3.986×10¹⁴ m³/s² para la Tierra)
- `t` = tiempo (s)

### Integración Numérica

Utiliza **scipy.integrate.solve_ivp** con:
- **Método:** DOP853 (Dormand-Prince de orden 8, Runge-Kutta)
- **Tolerancias:** rtol=1e-10, atol=1e-12
- **Paso adaptativo** para balance óptimo entre precisión y rendimiento

### Conservación de Energía

La energía orbital específica es una cantidad conservada:

ε = v²/2 - μ/r = constante

Cualquier desviación de energía constante indica error de integración numérica.

## 🗂️ Estructura del Proyecto

orbital-propagator/
├── src/
│   ├── propagator.py       # Motor de propagación principal
│   ├── visualization.py    # Utilidades de graficación
│   └── utils.py           # Funciones auxiliares
├── examples/
│   ├── test_circular.py   # Validación de órbita circular
│   └── visualize_orbit.py # Generar gráficas
├── docs/                   # Gráficas y documentación generadas
├── tests/                  # Pruebas unitarias (planeadas)
├── notebooks/             # Exploración en Jupyter (planeado)
├── README.md
├── requirements.txt
├── LICENSE
└── .gitignore

## 🛣️ Hoja de Ruta

### Fase 1: Fundamentos ✅ (Completada)
- [x] Propagador de dos cuerpos
- [x] Validación de órbita circular
- [x] Soporte para órbitas elípticas
- [x] Visualización 2D/3D
- [x] Verificación de conservación de energía

### Fase 2: Perturbaciones ✅ (Completada)
- [x] Perturbación J2 (achatamiento terrestre)
- [x] Conversión de elementos orbitales (Cartesianos ↔ Keplerianos)
- [x] Validación numérica con 6 tipos de órbitas
- [x] Validación contra poliastro/GMAT

### Fase 3: Propulsión Eléctrica ✅ (Completada)
- [x] Modelado de propulsión eléctrica de bajo empuje
- [x] Optimización de trayectorias LEO→GEO
- [x] Casos de estudio (Molniya, múltiples estrategias)
- [x] Búsqueda automática de tiempo óptimo
- [x] Comparación cuantitativa químico vs eléctrico

### Fase 4: Herramientas de Misión 🚧 (Jun-Jul 2026)
- [ ] **Proyecto 3:** Mission ΔV Calculator (Próximo - Jun 2026)
  - Calculadora de ΔV para maniobras comunes
  - Hohmann, bi-elliptic, cambios de plano
  - Comparación de estrategias
  - Base de datos de misiones típicas

- [ ] **Proyecto 4:** Rocket Equation & Propulsion Comparison Tool (Jul 2026)
  - Implementación completa ecuación Tsiolkovsky
  - Comparación Isp de diferentes propulsores
  - Trade-offs químico vs eléctrico vs nuclear
  - Calculadora de masa estructural

### Fase 5: Física de Plasmas & Propulsión (Ago-Sep 2026)
- [ ] **Proyecto 5:** Ion Thruster Simple Model (Ago 2026)
  - Modelo 0D/1D de thruster de xenón
  - Física básica de ionización
  - Cálculo de empuje e Isp
  - Comparación con datos reales

- [ ] **Proyecto 6:** Hall Thruster Basic Simulation (Sep 2026)
  - Campos E×B en canal anular
  - Simulación de deriva de electrones
  - Erosión preliminar de paredes
  - Validación contra thruster SPT-100

### Fase 6: CFD & Simulación Avanzada (Oct-Ene 2027)
- [ ] **Proyecto 7:** Plume Expansion CFD (Oct-Nov 2026)
  - OpenFOAM o código propio
  - Expansión de pluma en vacío
  - Efectos de contaminación
  - Visualización 3D de densidad/velocidad

- [ ] **Proyecto 8:** Particle-in-Cell (PIC) Code (Dic 2026-Ene 2027)
  - Simulador PIC desde cero
  - Partículas cargadas + campos autoconsistentes
  - Aplicación a thrusters de plasma
  - **Diferenciador clave del portfolio**

### Fase 7: Física Teórica Avanzada ⭐ (Ene-Feb 2027)
- [ ] **Proyecto 8.5:** Gravitomagnetic Field Simulator (Li-Torr Model) 🌟
  - **Motivación:** Investigación de Amy Eskridge y Ning Li
  - Implementación ecuaciones Li-Torr (Physical Review D, 1991)
  - Simulación campos gravitomagnéticos en superconductores
  - Modelado de alineación coherente de espines iónicos
  - Comparación con Efecto Podkletnov (experimental)
  - Análisis de sensibilidad de parámetros
  - **Único en su tipo:** Nadie ha hecho esto públicamente en Python
  - **Valor:** Intersección física teórica + propulsión avanzada
  - **Aplicación:** NASA Marshall, DARPA, startups de propulsión
  - **Publicable:** arXiv preprint

### Fase 8: Integración & Portfolio Final (Mar-Abr 2027)
- [ ] **Proyecto 9:** Electric Propulsion Performance Tool (Mar 2027)
  - Integrador de todos los proyectos anteriores
  - Interfaz unificada para diseño de misiones
  - Análisis completo: órbita + propulsión + plasma

- [ ] **Proyecto 10:** Digital Twin de Hall Thruster (Abr 2027)
  - Opcional avanzado
  - Sistema completo integrado
  - Matching con datos experimentales reales

### Proyectos Especiales (Timing Flexible)
- [ ] **Proyecto 7.5:** Alcubierre Drive Visualizer
  - Visualización de métrica de Alcubierre
  - Animación de burbuja warp
  - Cálculo de requerimientos energéticos
  - Educativo/divulgación

---

## 📊 Progreso del Roadmap

**Estado actual:** 2/10+ proyectos completados (20%)

**Timeline total:** 20 meses (Abr 2026 - Dic 2027)

**Objetivo:** Portfolio profesional + publicaciones + preparación para maestría

**Nivel actual alcanzado:** Comparable a herramientas profesionales básicas

**Próximo hito:** Proyecto 3 (Mission ΔV Calculator) - Jun 2026

## 📖 Referencias

1. **Bate, R., Mueller, D., White, J.** (1971). *Fundamentals of Astrodynamics*. Dover.
2. **Curtis, H.** (2013). *Orbital Mechanics for Engineering Students* (3ra ed.). Butterworth-Heinemann.
3. **Vallado, D.** (2013). *Fundamentals of Astrodynamics and Applications* (4ta ed.). Microcosm Press.
4. **Dormand, J. R., Prince, P. J.** (1980). "A family of embedded Runge-Kutta formulae". *Journal of Computational and Applied Mathematics*, 6(1), 19-26.

## 👤 Autor

**Damián Zúñiga Avelar**
- 🎓 Lic. en Física Aplicada (CIICAp-UAEM)
- 💼 Desarrollador II @ Garrido Licona y Asociados
- 🔬 Experiencia previa: Análisis CFD/FEM (Mayekawa)
- 🎯 Objetivo de transición profesional: Ingeniería de Propulsión Eléctrica / Sistemas Espaciales

**Contacto:**
- GitHub: [@DZALuc](https://github.com/DZALuc)
- LinkedIn: [Damián Zúñiga](https://linkedin.com/in/damianzuñiga)
- Email: damianzu94@gmail.com

## 📄 Licencia

Este proyecto está licenciado bajo la **Licencia MIT** - ver el archivo [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- **Proyecto Astropy** - Constantes astronómicas de alta precisión
- **Comunidad SciPy** - Herramientas robustas de integración de EDOs
- **Curtis, H.** - Excelente libro de texto sobre mecánica orbital
- **CIICAp-UAEM** - Formación fundamental en física

---

## 🌟 Estado del Proyecto

**Desarrollo Activo** - Esta es la Semana 1 de un ciclo de proyecto planeado de 6 semanas.

Actualizaciones futuras incluirán perturbaciones J2, modelado de bajo empuje, y validación contra herramientas establecidas (poliastro, GMAT).

⭐ **Dale una estrella a este repo** si te resulta útil para aprender mecánica orbital!

---

*Construido como parte de un portafolio técnico que demuestra habilidades de computación científica y experiencia en el dominio de ingeniería aeroespacial. Este proyecto sirve como fundamento para trabajo avanzado en sistemas de propulsión eléctrica y análisis de misiones.*


