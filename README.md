# 🛰️ Propagador Orbital

Simulador de mecánica orbital en Python para análisis de trayectorias satelitales y planificación de misiones.

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/estado-activo-success)

## 📋 Descripción General

Propagador orbital numérico de alta precisión que implementa mecánica clásica de dos cuerpos con soporte para perturbaciones. Diseñado para aplicaciones de ingeniería aeroespacial, análisis de misiones y propósitos educativos.

**Características Principales:**
- ✅ Propagación orbital Kepleriana (problema de dos cuerpos)
- ✅ Integración numérica de alta precisión (DOP853, rtol=1e-10)
- ✅ Visualización de trayectorias en 2D/3D
- ✅ Análisis y validación de elementos orbitales
- ✅ Verificación de conservación de energía (error relativo < 1e-12)
- 🚧 Modelado de perturbación J2 (planeado)
- 🚧 Extensión para propulsión eléctrica de bajo empuje (planeado)

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
- Método de integración: DOP853 (Dormand-Prince orden 8)

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

### Fase 1: Fundamentos ✅ (Actual)
- [x] Propagador de dos cuerpos
- [x] Validación de órbita circular
- [x] Visualización 2D/3D
- [x] Verificación de conservación de energía

### Fase 2: Perturbaciones 🚧 (En Progreso)
- [ ] Perturbación J2 (achatamiento terrestre)
- [ ] Soporte para órbitas elípticas
- [ ] Conversión de elementos orbitales (Cartesianos ↔ Keplerianos)
- [ ] Validación contra poliastro/GMAT

### Fase 3: Características Avanzadas (Planeado)
- [ ] Modelado de propulsión eléctrica de bajo empuje
- [ ] Arrastre atmosférico (modelo exponencial)
- [ ] Perturbaciones de tercer cuerpo (Luna, Sol)
- [ ] Visualización de trazas terrestres
- [ ] Calculadora de ΔV para misiones

### Fase 4: Optimización (Futuro)
- [ ] Perfilado y optimización de rendimiento
- [ ] Integradores simplécticos para estabilidad a largo plazo
- [ ] Propagación paralela para análisis Monte Carlo
- [ ] Aceleración con C/Cython para bucles críticos

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


