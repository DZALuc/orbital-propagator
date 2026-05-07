"""
VTK Textured Earth Animation

Simulador con Tierra texturizada realista.

Author: Damián Zúñiga Avelar
Date: Abril 2026
"""

import vtk
import numpy as np
import sys
import os

# Añadir path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.propagator import circular_velocity, orbital_period as calc_orbital_period


class TexturedEarthSimulator:
    """Simulador con Tierra texturizada."""
    
    def __init__(self, altitude_km=400):
        """
        Parameters
        ----------
        altitude_km : float
            Altitud de la órbita (km)
        """
        
        print("DEBUG: Iniciando TexturedEarthSimulator...")
        
        self.R_earth = 6371.0  # km
        self.altitude = altitude_km
        self.orbital_radius = self.R_earth + altitude_km
        
        print("DEBUG: Calculando parámetros orbitales...")
        
        # Parámetros orbitales
        r_meters = self.orbital_radius * 1000
        self.orbital_velocity = circular_velocity(r_meters)
        self.orbital_period = calc_orbital_period(r_meters)
        
        print(f"DEBUG: Periodo orbital = {self.orbital_period/60:.2f} min")
        
        # Estado
        self.current_angle = 0.0
        self.time_elapsed = 0.0
        self.speed_multiplier = 100.0
        self.paused = False
        
        # VTK objects
        self.renderer = None
        self.render_window = None
        self.interactor = None
        self.satellite_actor = None
        self.orbit_actor = None
        self.text_actor = None
        
        print(f"\n{'='*70}")
        print(f"  TEXTURED EARTH SIMULATOR - LEO {altitude_km} km")
        print(f"{'='*70}")
        print(f"\nParámetros orbitales:")
        print(f"  Radio órbita:     {self.orbital_radius:.1f} km")
        print(f"  Velocidad:        {self.orbital_velocity:.1f} m/s")
        print(f"  Periodo:          {self.orbital_period/60:.2f} min\n")
    
    

    def create_textured_earth(self, texture_file='models/textures/earth_day.jpg'):
        """Crea Tierra con textura realista."""
        
        print(f"DEBUG: Creando Tierra texturizada...")
        print(f"DEBUG: Buscando textura: {texture_file}")
        
        # Crear esfera NORMAL (NO textured)
        sphere = vtk.vtkSphereSource()  # ← CAMBIAR vtkTexturedSphereSource por vtkSphereSource
        sphere.SetCenter(0, 0, 0)
        sphere.SetRadius(self.R_earth)
        sphere.SetThetaResolution(100)
        sphere.SetPhiResolution(100)
        
        print("DEBUG: Esfera creada")
        
        # Generar coordenadas de textura
        texture_coords = vtk.vtkTextureMapToSphere()
        texture_coords.SetInputConnection(sphere.GetOutputPort())
        texture_coords.PreventSeamOn()
        
        print("DEBUG: Coordenadas de textura generadas")
        
        # Intentar cargar textura
        texture = None
        if os.path.exists(texture_file):
            try:
                print(f"DEBUG: Textura encontrada, cargando...")
                reader = vtk.vtkJPEGReader()
                reader.SetFileName(texture_file)
                reader.Update()
                
                texture = vtk.vtkTexture()
                texture.SetInputConnection(reader.GetOutputPort())
                texture.InterpolateOn()
                
                print(f"✓ Textura cargada: {texture_file}")
                
            except Exception as e:
                print(f"⚠️  Error cargando textura: {e}")
                print("  Usando color azul sólido")
                texture = None
        else:
            print(f"⚠️  Textura no encontrada: {texture_file}")
            print("  Usando color azul sólido")
        
        # Mapper (con coordenadas de textura)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(texture_coords.GetOutputPort())
        
        # Actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        
        if texture:
            actor.SetTexture(texture)
        else:
            actor.GetProperty().SetColor(0.2, 0.5, 0.9)  # Azul fallback
        
        print("DEBUG: Tierra creada OK")
        return actor



    def create_orbit_line(self):
        """Crea línea de órbita."""
        
        n_points = 100
        points = vtk.vtkPoints()
        
        for i in range(n_points + 1):
            angle = 2 * np.pi * i / n_points
            x = self.orbital_radius * np.cos(angle)
            y = self.orbital_radius * np.sin(angle)
            z = 0.0
            points.InsertNextPoint(x, y, z)
        
        line = vtk.vtkPolyLine()
        line.GetPointIds().SetNumberOfIds(n_points + 1)
        for i in range(n_points + 1):
            line.GetPointIds().SetId(i, i)
        
        cells = vtk.vtkCellArray()
        cells.InsertNextCell(line)
        
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetLines(cells)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 1.0, 0.0)
        actor.GetProperty().SetLineWidth(3)
        
        return actor
    
    
    def create_satellite(self):
        """Crea satélite."""
        
        cube = vtk.vtkCubeSource()
        cube.SetXLength(500)
        cube.SetYLength(500)
        cube.SetZLength(750)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(cube.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.9, 0.9, 0.9)
        
        return actor
    
    
    def update_satellite_position(self):
        """Actualiza posición del satélite."""
        
        x = self.orbital_radius * np.cos(self.current_angle)
        y = self.orbital_radius * np.sin(self.current_angle)
        z = 0.0
        
        self.satellite_actor.SetPosition(x, y, z)
    
    
    def create_info_text(self):
        """Crea texto informativo."""
        
        text = vtk.vtkTextActor()
        text.GetTextProperty().SetFontSize(16)
        text.GetTextProperty().SetColor(1.0, 1.0, 1.0)
        text.SetPosition(10, 10)
        
        return text
    
    
    def update_info_text(self):
        """Actualiza texto."""
        
        orbits = self.time_elapsed / self.orbital_period
        status = "PAUSADO" if self.paused else "ACTIVO"
        
        info = f"""TEXTURED EARTH SIMULATOR - LEO {self.altitude} km

Status:           {status}
Tiempo:           {self.time_elapsed:.1f} s ({self.time_elapsed/60:.2f} min)
Ángulo:           {np.degrees(self.current_angle):.1f}°
Órbitas:          {orbits:.3f}
Velocidad sim:    {self.speed_multiplier:.0f}x

[+/-] Velocidad  [SPACE] Pausa  [R] Reset  [Q] Salir
"""
        self.text_actor.SetInput(info)
    
    
    def setup_renderer(self):
        """Configura renderer."""
        
        print("DEBUG: Setup renderer...")
        
        # Renderer
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.0, 0.0, 0.0)
        
        print("DEBUG: Renderer creado")
        
        # Ventana
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.SetSize(1400, 900)
        self.render_window.AddRenderer(self.renderer)
        self.render_window.SetWindowName(f"Textured Earth - LEO {self.altitude} km")
        
        print("DEBUG: Ventana creada")
        
        # Interactor
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)
        
        print("DEBUG: Interactor creado")
        
        # Añadir Tierra
        print("DEBUG: Añadiendo Tierra...")
        earth = self.create_textured_earth()
        self.renderer.AddActor(earth)
        
        # Añadir órbita
        print("DEBUG: Añadiendo órbita...")
        self.orbit_actor = self.create_orbit_line()
        self.renderer.AddActor(self.orbit_actor)
        
        # Añadir satélite
        print("DEBUG: Añadiendo satélite...")
        self.satellite_actor = self.create_satellite()
        self.renderer.AddActor(self.satellite_actor)
        
        # Luz
        print("DEBUG: Añadiendo luces...")
        light = vtk.vtkLight()
        light.SetPosition(50000, 0, 0)
        light.SetFocalPoint(0, 0, 0)
        self.renderer.AddLight(light)
        
        # Texto
        print("DEBUG: Añadiendo texto...")
        self.text_actor = self.create_info_text()
        self.renderer.AddActor2D(self.text_actor)
        
        # Cámara
        print("DEBUG: Configurando cámara...")
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(15000, 15000, 15000)
        camera.SetFocalPoint(0, 0, 0)
        self.renderer.ResetCamera()
        
        # Posición inicial
        self.update_satellite_position()
        self.update_info_text()
        
        print("DEBUG: Setup completo OK")
    
    
    def animation_callback(self, obj, event):
        """Callback para animación."""
        
        if self.paused:
            return
        
        dt_real = 0.033
        dt_sim = dt_real * self.speed_multiplier
        
        self.time_elapsed += dt_sim
        
        omega = 2 * np.pi / self.orbital_period
        self.current_angle += omega * dt_sim
        
        if self.current_angle >= 2 * np.pi:
            self.current_angle -= 2 * np.pi
        
        self.update_satellite_position()
        self.update_info_text()
        
        self.render_window.Render()
    
    
    def key_press_callback(self, obj, event):
        """Callback para teclas."""
        
        key = self.interactor.GetKeySym()
        
        if key in ['plus', 'equal']:
            self.speed_multiplier *= 1.5
            print(f"Velocidad: {self.speed_multiplier:.0f}x")
        
        elif key == 'minus':
            self.speed_multiplier /= 1.5
            if self.speed_multiplier < 1.0:
                self.speed_multiplier = 1.0
            print(f"Velocidad: {self.speed_multiplier:.0f}x")
        
        elif key == 'space':
            self.paused = not self.paused
            print("PAUSADO" if self.paused else "ACTIVO")
        
        elif key == 'r':
            self.current_angle = 0.0
            self.time_elapsed = 0.0
            self.update_satellite_position()
            self.update_info_text()
            print("RESET")
    
    
    def run(self):
        """Ejecuta simulación."""
        
        print("DEBUG: Ejecutando run()...")
        
        self.setup_renderer()
        
        print("DEBUG: Setup completo, iniciando callbacks...")
        
        # Timer
        self.interactor.AddObserver('TimerEvent', self.animation_callback)
        timer_id = self.interactor.CreateRepeatingTimer(33)
        
        # Keyboard
        self.interactor.AddObserver('KeyPressEvent', self.key_press_callback)
        
        print("\n" + "─"*70)
        print("Simulación iniciada...")
        print("\nControles:")
        print("  [+/-]     Velocidad")
        print("  [SPACE]   Pausa")
        print("  [R]       Reset")
        print("  Mouse     Rotar/Zoom")
        print("  [Q]       Salir")
        print("─"*70 + "\n")
        
        print("DEBUG: Iniciando render...")
        
        # Iniciar
        self.render_window.Render()
        
        print("DEBUG: Iniciando interactor...")
        
        self.interactor.Start()
        
        print("\n✓ Simulación cerrada\n")


if __name__ == "__main__":
    print("DEBUG: __main__ ejecutándose...")
    sim = TexturedEarthSimulator(altitude_km=400)
    print("DEBUG: Objeto creado, llamando run()...")
    sim.run()
    print("DEBUG: Programa terminado")