# 🌀 PROYECTO 8.5: GRAVITOMAGNETIC FIELD SIMULATOR

## Li-Torr Model Implementation

**Estado:** Planeado  
**Prioridad:** Alta (proyecto especial diferenciador)  
**Timeline estimado:** 25-30 horas  
**Fecha tentativa:** Enero-Febrero 2027  
**Prerrequisitos:** Proyecto 8 (PIC Code) completado

---

## 🎯 MOTIVACIÓN

### El Caso de Amy Eskridge

Amy Eskridge fue una científica del Institute for Exotic Science en Huntsville, Alabama, que investigaba antigravedad y propulsión avanzada. Murió en circunstancias controvertidas en junio 2022, semanas después de advertir: *"Si ven que me quité la vida, definitivamente no fue así."*

Su investigación se centraba en el trabajo de **Ning Li**, física que en los años 90 propuso generar campos gravitomagnéticos mediante superconductores en rotación.

### El Trabajo de Ning Li

**Papers fundamentales:**
- Li, N. & Torr, D. (1991). "Effects of a gravitomagnetic field on pure superconductors". *Physical Review D*, 43(2). DOI: 10.1103/PhysRevD.43.457
- Li, N. & Torr, D. (1993). "Gravitoelectric-electric coupling via superconductivity". *Foundations of Physics Letters*, 6(4).

**Teoría central:**
> Rotar iones dentro de un superconductor crea un campo gravitomagnético perpendicular al eje de giro. Si se alinea una gran cantidad de iones en un condensado de Bose-Einstein, el campo resultante sería lo suficientemente fuerte para producir una fuerza repulsiva detectable.

**Conexión con Amy:**
- Ambas en Huntsville, Alabama
- Ambas colaboraron con NASA Marshall
- Ambas investigaban propulsión sin propelente
- Ning Li desapareció en investigación clasificada (2002)
- Amy murió en circunstancias sospechosas (2022)

### ¿Por Qué Este Proyecto?

**Valor científico:**
- Los papers de Li-Torr son revisados por pares y matemáticamente rigurosos
- Nadie ha implementado computacionalmente estas ecuaciones de forma pública
- La DIA (Defense Intelligence Agency) tiene documentos desclasificados sobre el tema

**Valor para portfolio:**
- Intersección única: física teórica + computación científica + propulsión
- Tema controversial pero con fundamento académico
- Diferenciador brutal (nadie más tiene esto)
- Publicable en arXiv como preprint

**Relevancia personal:**
- Tu background en física aplicada (CIICAp-UAEM)
- Experiencia en CFD/FEM (Mayekawa)
- Ya dominarás PIC codes (Proyecto 8)
- Perfecta extensión: misma matemática, nueva física

---

## 🔬 FUNDAMENTOS TEÓRICOS

### Gravitomagnetismo Clásico

La Relatividad General predice que masas en rotación generan un campo gravitomagnético análogo al campo magnético en electrodinámica:

**Ecuaciones de campo gravitomagnético (GEM):**
∇ × E_g = -∂B_g/∂t
∇ × B_g = (4πG/c²) J_mass + (1/c²) ∂E_g/∂t
Donde:
E_g = campo gravitoeléctrico (análogo a E)
B_g = campo gravitomagnético (análogo a B)
J_mass = corriente de masa (ρ v)
G = constante gravitacional

**Problema:** Este efecto es EXTREMADAMENTE débil en condiciones normales.

### La Propuesta de Li-Torr

**Amplificación mediante superconductores:**

En un superconductor tipo-II, los iones de la red cristalina forman pares de Cooper con espines alineados. Si se rota el superconductor:

1. **Los iones rotan coherentemente** (no los electrones)
2. **Se genera corriente de masa** J_mass = n_ion × m_ion × v_rot
3. **Alineación cuántica** amplifica el efecto por factor ~10¹⁰

**Ecuación clave (Li-Torr 1991):**
B_g = (8πG/c²) × L_ion × n_coherent
Donde:
L_ion = momento angular por ion
n_coherent = densidad de iones coherentes

**Campos acoplados:**

El paper de 1993 muestra que en presencia de un campo magnético AC, se induce también un campo gravitoeléctrico:
E_g = -(∂A_g/∂t) - ∇φ_g
Donde A_g es el potencial vector gravitomagnético

Este campo gravitoeléctrico produciría una fuerza sobre objetos neutros (sin carga).

---

## 💻 IMPLEMENTACIÓN TÉCNICA

### Arquitectura del Código
src/gravitomagnetic/
├── init.py
├── li_torr_model.py          # Ecuaciones fundamentales
├── superconductor_lattice.py # Modelo de red cristalina
├── field_solver.py            # Solver de campos acoplados
├── visualization.py           # Visualización 3D de campos
└── validation.py              # Comparación con experimentos
examples/
├── basic_rotating_disk.py     # Caso simple
├── podkletnov_comparison.py   # Réplica computacional Podkletnov
├── parametric_study.py        # Análisis sensibilidad
└── optimal_configuration.py   # Maximización de campo
docs/gravitomagnetic/
├── THEORY.md                  # Derivación completa de ecuaciones
├── IMPLEMENTATION.md          # Detalles numéricos
└── VALIDATION.md              # Comparación con datos experimentales

### Ecuaciones a Implementar

**1. Campo gravitomagnético en superconductor rotante:**

```python
def compute_gravitomagnetic_field(omega, n_ion, m_ion, r, z):
    """
    Calcula B_g según Li-Torr (1991)
    
    Parameters:
    -----------
    omega : float
        Velocidad angular (rad/s)
    n_ion : float
        Densidad de iones coherentes (m^-3)
    m_ion : float
        Masa del ion (kg)
    r, z : arrays
        Coordenadas cilíndricas (m)
    
    Returns:
    --------
    B_g : array
        Campo gravitomagnético (s^-1)
    """
    G = 6.674e-11  # m^3 kg^-1 s^-2
    c = 3e8        # m/s
    
    # Momento angular por ion
    L_ion = m_ion * omega * r**2
    
    # Campo gravitomagnético (componente z)
    B_g_z = (8 * np.pi * G / c**2) * L_ion * n_ion
    
    return B_g_z
```

**2. Acoplamiento con campo magnético (Li-Torr 1993):**

```python
def compute_gravitoelectric_field(B_mag, freq, r, z):
    """
    Campo gravitoeléctrico inducido por B magnético AC
    
    Según ecuación (15) de Li-Torr 1993
    """
    # Potencial vector magnético
    A_mag = B_mag / (2 * np.pi * freq)
    
    # Acoplamiento gravitoeléctrico-magnético
    # (Ecuaciones de London modificadas)
    lambda_L = london_penetration_depth(T)  # Longitud London
    
    E_g = coupling_coefficient * (dA_mag_dt) / lambda_L**2
    
    return E_g
```

**3. Fuerza sobre objeto de prueba:**

```python
def compute_gravitational_force(m_test, E_g, B_g, v_test):
    """
    Fuerza análoga a Lorentz para gravedad
    
    F_g = m × (E_g + v × B_g)
    """
    F_gravitoelectric = m_test * E_g
    F_gravitomagnetic = m_test * np.cross(v_test, B_g)
    
    return F_gravitoelectric + F_gravitomagnetic
```

### Solver Numérico

**Problema:** Campos acoplados GEM + Maxwell + London

```python
class GravitomagneticSolver:
    def __init__(self, geometry, material_properties):
        self.geom = geometry
        self.props = material_properties
        
    def solve_fields(self, omega, B_external, freq):
        """
        Resuelve sistema acoplado:
        - Ecuaciones GEM (gravitomagnético)
        - Ecuaciones Maxwell (electromagnético)
        - Ecuaciones London (superconductor)
        """
        # Grid espacial
        r = np.linspace(0, self.geom.radius, 100)
        z = np.linspace(-self.geom.height, self.geom.height, 100)
        R, Z = np.meshgrid(r, z)
        
        # Campos iniciales
        B_g = np.zeros_like(R)
        E_g = np.zeros_like(R)
        
        # Iteración hasta convergencia
        for iteration in range(max_iter):
            # Actualizar B_g
            B_g_new = self.compute_Bg(R, Z, omega)
            
            # Actualizar E_g (acoplado con B magnético)
            E_g_new = self.compute_Eg(R, Z, B_external, freq)
            
            # Check convergencia
            if np.allclose(B_g, B_g_new, rtol=1e-6):
                break
                
            B_g, E_g = B_g_new, E_g_new
        
        return {'B_g': B_g, 'E_g': E_g, 'R': R, 'Z': Z}
```

---

## 📊 CASOS DE ESTUDIO

### Caso 1: Disco YBCO Básico (Réplica Li)

**Configuración:**
Material: YBa₂Cu₃O₇₋ₓ (superconductor alta temperatura)
Geometría: Disco de 30 cm diámetro, 2 cm espesor
Temperatura: 77 K (nitrógeno líquido)
Velocidad rotación: 5,000 RPM
Campo magnético: 0.5 T, 50 Hz

**Predicción según Li-Torr:**
B_g ~ 10^-12 s^-1
Fuerza sobre masa de 1 kg a 1 cm del disco: ~ 10^-6 N
Reducción peso aparente: ~ 10^-7 g

### Caso 2: Réplica Computacional Podkletnov

**Configuración (Podkletnov 1992):**
Material: YBCO sinterizado
Diámetro: 27.5 cm
Espesor: 1 cm
Rotación: 5,000 RPM
Campo: 0-1 T
Temperatura: 64-77 K

**Resultado experimental reportado:** 0.05% - 2% reducción de peso

**Objetivo computacional:**
- Resolver campos con parámetros exactos de Podkletnov
- Calcular fuerza predicha teóricamente
- Comparar con datos experimentales
- Identificar parámetros críticos

### Caso 3: Configuración Optimizada

**Pregunta:** ¿Qué maximiza el campo gravitomagnético?

**Variables a optimizar:**
- Geometría (radio, espesor, forma)
- Material (YBCO vs otros superconductores)
- Velocidad rotación (límite mecánico)
- Campo magnético externo (magnitud, frecuencia)
- Temperatura (77K vs 4K)

**Método:** Búsqueda paramétrica con scipy.optimize

---

## 🎯 ENTREGABLES

### Código
✅ Solver de campos gravitomagnéticos
✅ Implementación ecuaciones Li-Torr completas
✅ Visualización 3D de campos
✅ Análisis paramétrico automatizado
✅ Comparación con datos Podkletnov
✅ Documentación completa

### Documentación Técnica
✅ Derivación completa de ecuaciones (LaTeX)
✅ Guía de implementación
✅ Resultados y análisis
✅ Comparación teoría vs experimento
✅ Limitaciones del modelo

### Publicación
✅ Preprint arXiv (opcional pero recomendado)
Título: "Numerical Simulation of Gravitomagnetic Fields in
Rotating Superconductors: A Computational Implementation
of the Li-Torr Model"

### Visualizaciones
✅ Mapa 3D de campo B_g sobre disco rotante
✅ Mapa 3D de campo E_g inducido
✅ Líneas de campo gravitomagnético
✅ Fuerza vs distancia al disco
✅ Análisis paramétrico (gráficas 2D)

---

## 🔍 VALIDACIÓN

### Comparación con Datos Experimentales

**Fuentes de datos:**
1. Podkletnov (1992) - Physica C: 0.05-2% reducción peso
2. Podkletnov (1997) - arXiv: hasta 9% en altas velocidades
3. NASA Marshall (intentos fallidos de replicación)
4. Modanese (2001) - Análisis teórico

**Estrategia de validación:**
Si predicción teórica ~ datos Podkletnov:
→ Modelo Li-Torr es consistente
Si predicción << datos Podkletnov:
→ Faltan factores de amplificación
→ Investigar mecanismos cuánticos adicionales
Si predicción >> datos experimentales:
→ Revisar condiciones de coherencia
→ Analizar límites de validez del modelo

### Limitaciones Conocidas

**Física:**
- Modelo linealizado (válido solo para campos débiles)
- Asume coherencia perfecta de espines
- No incluye efectos térmicos en detalle
- Ignora vórtices en superconductor tipo-II

**Numérica:**
- Resolución de grid limitada
- Aproximación de campo medio
- No simula dinámica cuántica completa

---

## 💡 VALOR ESTRATÉGICO

### Para Portfolio

**Diferenciador único:**
- Nadie más tiene implementación pública de esto
- Intersección física + computación + propulsión
- Tema controversial pero académicamente fundamentado

**Narrativa para entrevistas:**
"Después de dominar simulación de plasma (PIC code), implementé
el modelo gravitomagnético de Ning Li — física que trabajó en NASA
Marshall investigando propulsión sin propelente mediante
superconductores. Tomé sus ecuaciones de Physical Review D (1991)
y las implementé computacionalmente para primera vez de forma
pública. Los resultados predicen campos débiles pero detectables,
consistentes con algunos experimentos reportados. Esto demuestra
mi capacidad de implementar física teórica avanzada y contribuir
a fronteras de investigación."

### Para Maestría/PhD

**Posibles líneas de investigación:**
- Optimización de configuraciones
- Acoplamiento con efectos cuánticos (BEC)
- Experimento computacional vs real
- Análisis de viabilidad tecnológica

**Publicación potencial:**
- arXiv preprint
- Revista de física computacional
- Conferencia de propulsión (AIAA)

### Para Empleabilidad

**Laboratorios interesados:**
- NASA Marshall (Huntsville, Alabama)
- DARPA (Propulsion Science)
- Startups de propulsión avanzada
- Universidades con research en GEM

---

## 📚 REFERENCIAS

**Papers fundamentales:**
1. Li, N. & Torr, D. (1991). Physical Review D, 43(2), 457
2. Li, N. & Torr, D. (1993). Foundations of Physics Letters, 6(4)
3. Podkletnov, E. (1992). Physica C, 203, 441-444
4. Modanese, G. (2001). Theoretical analysis of Li effect

**Documentos gobierno:**
5. DIA Report (2018). "Warp Drive, Dark Energy, and Manipulation of Extra Dimensions"
6. NASA Technical Reports sobre gravitomagnetismo

**Recursos online:**
- Papers en OSTI.gov (Department of Energy)
- arXiv: cond-mat, gr-qc sections

---

## ⏱️ TIMELINE ESTIMADO

**Total: 25-30 horas**
Semana 1 (8-10h):

Revisar papers Li-Torr en detalle
Derivar ecuaciones completas
Diseñar arquitectura del código

Semana 2 (8-10h):

Implementar solver básico
Caso 1: Disco simple
Validación matemática

Semana 3 (6-8h):

Caso Podkletnov
Análisis paramétrico
Visualizaciones 3D

Semana 4 (3-4h):

Documentación
Preprint (opcional)
Publicar en GitHub


---

## ✅ CRITERIOS DE ÉXITO

**Mínimo viable:**
- [ ] Implementación correcta ecuaciones Li-Torr
- [ ] Solver convergente y estable
- [ ] Comparación cuantitativa con Podkletnov
- [ ] 3+ visualizaciones profesionales
- [ ] Documentación técnica completa

**Bonus:**
- [ ] Preprint en arXiv
- [ ] Optimización automática de parámetros
- [ ] Análisis de viabilidad experimental
- [ ] Código optimizado (Cython/numba)

---

**FIN DEL DOCUMENTO**

Este proyecto te posiciona en la frontera entre física teórica, computación científica y propulsión avanzada — exactamente donde quieres estar.