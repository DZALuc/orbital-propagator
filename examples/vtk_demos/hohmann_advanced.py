"""
Hohmann Transfer - Advanced Visualization

Versión mejorada con estela, vectores de velocidad, y zoom automático.

Author: Damián Zúñiga Avelar
Date: Mayo 2026
"""

import vtk
import numpy as np
import sys
import os
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.propagator import circular_velocity, orbital_period as calc_orbital_period
from src.delta_v import hohmann_transfer


class AdvancedHohmannSimulator:
    """Simulador avanzado de transferencia Hohmann."""
    
    def __init__(self, h1_km=400, h2_km=35786):
        """
        Parameters
        ----------
        h1_km : float
            Altitud órbita inicial (km)
        h2_km : float
            Altitud órbita final (km)
        """
        
        print(f"\n{'='*70}")
        print(f"  ADVANCED HOHMANN TRANSFER SIMULATOR")
        print(f"{'='*70}\n")
        
        self.R_earth = 6371.0
        self.h1 = h1_km
        self.h2 = h2_km
        self.r1 = self.R_earth + h1_km
        self.r2 = self.R_earth + h2_km
        
        # Calcular parámetros
        r1_m = self.r1 * 1000
        r2_m = self.r2 * 1000
        
        transfer_data = hohmann_transfer(r1_m, r2_m)
        
        self.v1 = circular_velocity(r1_m)
        self.v2 = circular_velocity(r2_m)
        self.period1 = calc_orbital_period(r1_m)
        self.period2 = calc_orbital_period(r2_m)
        
        self.a_transfer = transfer_data['semi_major']
        self.transfer_time = transfer_data['transfer_time']
        self.delta_v1 = transfer_data['delta_v_1']
        self.delta_v2 = transfer_data['delta_v_2']
        self.delta_v_total = transfer_data['delta_v_total']
        self.period_transfer = 2 * self.transfer_time
        
        # Estado
        self.phase = 'initial'
        self.time_in_phase = 0.0
        self.total_time = 0.0
        self.speed = 50.0
        self.paused = False
        self.current_angle = 0.0
        
        # Estela (trail)
        self.trail_points = deque(maxlen=200)  # Últimos 200 puntos
        self.show_trail = True
        self.show_velocity = True
        self.auto_zoom = True
        
        # VTK objects
        self.renderer = None
        self.render_window = None
        self.interactor = None
        self.satellite_actor = None
        self.trail_actor = None
        self.velocity_actor = None
        self.text_actor = None
        
        print(f"LEO: {h1_km} km → GEO: {h2_km} km")
        print(f"ΔV₁: {self.delta_v1:.1f} m/s | ΔV₂: {self.delta_v2:.1f} m/s")
        print(f"Total: {self.delta_v_total:.1f} m/s | Tiempo: {self.transfer_time/3600:.2f} h\n")
    
    
    def create_earth(self):
        """Crea Tierra."""
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(0, 0, 0)
        sphere.SetRadius(self.R_earth)
        sphere.SetThetaResolution(100)
        sphere.SetPhiResolution(100)
        
        texture_coords = vtk.vtkTextureMapToSphere()
        texture_coords.SetInputConnection(sphere.GetOutputPort())
        texture_coords.PreventSeamOn()
        
        texture = None
        texture_file = 'models/textures/earth_day.jpg'
        
        if os.path.exists(texture_file):
            try:
                reader = vtk.vtkJPEGReader()
                reader.SetFileName(texture_file)
                reader.Update()
                
                texture = vtk.vtkTexture()
                texture.SetInputConnection(reader.GetOutputPort())
                texture.InterpolateOn()
            except:
                pass
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(texture_coords.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        
        if texture:
            actor.SetTexture(texture)
        else:
            actor.GetProperty().SetColor(0.2, 0.5, 0.9)
        
        return actor
    
    
    def create_orbit_line(self, radius, color=(1, 1, 1), width=2):
        """Crea órbita circular."""
        n_points = 100
        points = vtk.vtkPoints()
        
        for i in range(n_points + 1):
            angle = 2 * np.pi * i / n_points
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
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
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetLineWidth(width)
        
        return actor
    
    
    def create_elliptical_orbit(self, r_peri, r_apo, color=(1, 0.5, 0), width=3):
        """Crea órbita elíptica."""
        a = (r_peri + r_apo) / 2
        e = (r_apo - r_peri) / (r_apo + r_peri)
        
        n_points = 200
        points = vtk.vtkPoints()
        
        for i in range(n_points + 1):
            nu = 2 * np.pi * i / n_points
            r = a * (1 - e**2) / (1 + e * np.cos(nu))
            
            x = r * np.cos(nu)
            y = r * np.sin(nu)
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
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetLineWidth(width)
        
        return actor
    
    
    def create_impulse_marker(self, position, color=(1, 0, 0)):
        """Crea marcador de impulso."""
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(position)
        sphere.SetRadius(300)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        
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
        actor.GetProperty().SetColor(1, 1, 1)
        actor.GetProperty().SetSpecular(0.6)
        actor.GetProperty().SetSpecularPower(30)
        
        return actor
    
    
    def create_trail(self):
        """Crea estela del satélite (se actualiza dinámicamente)."""
        self.trail_polydata = vtk.vtkPolyData()
        self.trail_points_vtk = vtk.vtkPoints()
        self.trail_polydata.SetPoints(self.trail_points_vtk)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.trail_polydata)
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1, 1, 0)  # Amarillo
        actor.GetProperty().SetLineWidth(2)
        actor.GetProperty().SetOpacity(0.7)
        
        return actor
    
    
    def update_trail(self, position):
        """Actualiza estela con nueva posición."""
        self.trail_points.append(position)
        
        # Actualizar VTK points
        self.trail_points_vtk.Reset()
        for p in self.trail_points:
            self.trail_points_vtk.InsertNextPoint(p)
        
        # Crear línea
        if len(self.trail_points) > 1:
            line = vtk.vtkPolyLine()
            line.GetPointIds().SetNumberOfIds(len(self.trail_points))
            for i in range(len(self.trail_points)):
                line.GetPointIds().SetId(i, i)
            
            cells = vtk.vtkCellArray()
            cells.InsertNextCell(line)
            
            self.trail_polydata.SetLines(cells)
        
        self.trail_polydata.Modified()
    
    
    def create_velocity_vector(self):
        """Crea flecha de vector velocidad."""
        self.arrow_source = vtk.vtkArrowSource()
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self.arrow_source.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0, 1, 1)  # Cyan
        
        return actor
    
    
    def update_velocity_vector(self, position, velocity_magnitude):
        """
        Actualiza vector de velocidad.
        
        Parameters
        ----------
        position : tuple
            Posición actual (x, y, z)
        velocity_magnitude : float
            Magnitud velocidad (km/s)
        """
        # Dirección tangencial
        x, y, z = position
        r = np.sqrt(x**2 + y**2)
        
        # Vector tangencial (perpendicular al radio)
        vx = -y / r if r > 0 else 0
        vy = x / r if r > 0 else 1
        
        # Escalar por velocidad (escala visual)
        scale = velocity_magnitude * 500  # Factor visual
        
        # Transform
        transform = vtk.vtkTransform()
        transform.Translate(position)
        transform.Scale(scale, scale, scale)
        
        # Rotar para apuntar en dirección correcta
        angle = np.degrees(np.arctan2(vy, vx))
        transform.RotateZ(angle - 90)  # Arrow apunta en Y por defecto
        
        transform_filter = vtk.vtkTransformPolyDataFilter()
        transform_filter.SetInputConnection(self.arrow_source.GetOutputPort())
        transform_filter.SetTransform(transform)
        transform_filter.Update()
        
        self.velocity_actor.GetMapper().SetInputConnection(transform_filter.GetOutputPort())
    
    
    def get_satellite_position(self):
        """Calcula posición actual del satélite."""
        if self.phase == 'initial':
            x = self.r1 * np.cos(self.current_angle)
            y = self.r1 * np.sin(self.current_angle)
            z = 0.0
            v_mag = self.v1 / 1000  # km/s
            
        elif self.phase == 'transfer':
            a = self.a_transfer / 1000
            e = (self.r2 - self.r1) / (self.r2 + self.r1)
            
            progress = self.time_in_phase / self.transfer_time
            nu = np.pi * progress
            
            r = a * (1 - e**2) / (1 + e * np.cos(nu))
            
            x = r * np.cos(nu)
            y = r * np.sin(nu)
            z = 0.0
            
            # Velocidad en órbita elíptica (aproximada)
            v_mag = np.sqrt(398600 * (2/r - 1/a)) / 1000
            
        elif self.phase == 'final':
            x = self.r2 * np.cos(self.current_angle)
            y = self.r2 * np.sin(self.current_angle)
            z = 0.0
            v_mag = self.v2 / 1000  # km/s
        
        return (x, y, z), v_mag
    
    
    def update_simulation(self, dt):
        """Actualiza simulación."""
        self.total_time += dt
        self.time_in_phase += dt
        
        if self.phase == 'initial':
            omega1 = 2 * np.pi / self.period1
            self.current_angle += omega1 * dt
            
            if self.current_angle >= 2 * np.pi:
                print(f"\n⚡ IMPULSO 1: ΔV = +{self.delta_v1:.1f} m/s")
                self.phase = 'transfer'
                self.time_in_phase = 0.0
                self.current_angle = 0.0
                self.trail_points.clear()  # Limpiar estela
        
        elif self.phase == 'transfer':
            if self.time_in_phase >= self.transfer_time:
                print(f"⚡ IMPULSO 2: ΔV = +{self.delta_v2:.1f} m/s")
                print(f"✓ Transferencia completada")
                self.phase = 'final'
                self.time_in_phase = 0.0
                self.current_angle = np.pi
        
        elif self.phase == 'final':
            omega2 = 2 * np.pi / self.period2
            self.current_angle += omega2 * dt
    
    
    def update_camera_zoom(self):
        """Zoom automático según fase."""
        if not self.auto_zoom:
            return
        
        camera = self.renderer.GetActiveCamera()
        
        if self.phase == 'initial':
            # Zoom a LEO
            camera.SetPosition(15000, 15000, 10000)
        elif self.phase == 'transfer':
            # Vista completa de transferencia
            camera.SetPosition(50000, 50000, 30000)
        elif self.phase == 'final':
            # Zoom a GEO
            camera.SetPosition(60000, 60000, 40000)
        
        camera.SetFocalPoint(0, 0, 0)
    
    
    def create_info_text(self):
        """Crea texto."""
        text = vtk.vtkTextActor()
        text.GetTextProperty().SetFontSize(16)
        text.GetTextProperty().SetColor(1, 1, 1)
        text.GetTextProperty().SetBold(True)
        text.SetPosition(10, 10)
        return text
    
    
    def update_info_text(self):
        """Actualiza texto."""
        phase_names = {
            'initial': 'ÓRBITA INICIAL (LEO)',
            'transfer': 'TRANSFERENCIA HOHMANN',
            'final': 'ÓRBITA FINAL (GEO)'
        }
        
        phase_emoji = {
            'initial': '🔵',
            'transfer': '🟠',
            'final': '🟢'
        }
        
        status = "⏸️ PAUSADO" if self.paused else "▶️ ACTIVO"
        
        trail_status = "ON" if self.show_trail else "OFF"
        velocity_status = "ON" if self.show_velocity else "OFF"
        zoom_status = "ON" if self.auto_zoom else "OFF"
        
        info = f"""ADVANCED HOHMANN TRANSFER SIMULATOR

Estado: {status}
Fase:   {phase_emoji[self.phase]} {phase_names[self.phase]}
Tiempo: {self.total_time:.1f} s ({self.total_time/60:.2f} min)
En fase: {self.time_in_phase:.1f} s
Velocidad: {self.speed:.0f}x

ΔV₁: {self.delta_v1:.1f} m/s | ΔV₂: {self.delta_v2:.1f} m/s | Total: {self.delta_v_total:.1f} m/s

Visualización:
  [T] Estela: {trail_status}  [V] Velocidad: {velocity_status}  [Z] Auto-zoom: {zoom_status}

[+/-] Velocidad  [SPACE] Pausa  [R] Reset  [Q] Salir
"""
        self.text_actor.SetInput(info)
    
    
    def setup_renderer(self):
        """Setup escena."""
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0, 0, 0)
        
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.SetSize(1600, 1000)
        self.render_window.AddRenderer(self.renderer)
        self.render_window.SetWindowName("Advanced Hohmann Transfer")
        
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)
        
        # Tierra
        earth = self.create_earth()
        self.renderer.AddActor(earth)
        
        # Órbitas
        orbit1 = self.create_orbit_line(self.r1, (0.3, 0.5, 1.0), 3)
        self.renderer.AddActor(orbit1)
        
        orbit2 = self.create_orbit_line(self.r2, (0.3, 1.0, 0.3), 3)
        self.renderer.AddActor(orbit2)
        
        transfer_orbit = self.create_elliptical_orbit(self.r1, self.r2, (1.0, 0.6, 0.0), 4)
        self.renderer.AddActor(transfer_orbit)
        
        # Marcadores
        impulse1 = self.create_impulse_marker((self.r1, 0, 0), (1, 0, 0))
        self.renderer.AddActor(impulse1)
        
        impulse2 = self.create_impulse_marker((self.r2, 0, 0), (0, 1, 0))
        self.renderer.AddActor(impulse2)
        
        # Satélite
        self.satellite_actor = self.create_satellite()
        self.renderer.AddActor(self.satellite_actor)
        
        # Estela
        self.trail_actor = self.create_trail()
        self.renderer.AddActor(self.trail_actor)
        
        # Vector velocidad
        self.velocity_actor = self.create_velocity_vector()
        self.renderer.AddActor(self.velocity_actor)
        
        # Luz
        light = vtk.vtkLight()
        light.SetPosition(50000, 0, 0)
        light.SetFocalPoint(0, 0, 0)
        self.renderer.AddLight(light)
        
        # Texto
        self.text_actor = self.create_info_text()
        self.renderer.AddActor2D(self.text_actor)
        
        # Cámara
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(15000, 15000, 10000)
        camera.SetFocalPoint(0, 0, 0)
        self.renderer.ResetCamera()
        
        # Posición inicial
        pos, v_mag = self.get_satellite_position()
        self.satellite_actor.SetPosition(pos)
        self.update_velocity_vector(pos, v_mag)
        self.update_info_text()
    
    
    def animation_callback(self, obj, event):
        """Callback animación."""
        if self.paused:
            return
        
        dt_real = 0.033
        dt_sim = dt_real * self.speed
        
        # Actualizar fase actual
        old_phase = self.phase
        self.update_simulation(dt_sim)
        
        # Si cambió de fase, hacer zoom
        if old_phase != self.phase:
            self.update_camera_zoom()
        
        # Actualizar posición
        pos, v_mag = self.get_satellite_position()
        self.satellite_actor.SetPosition(pos)
        
        # Actualizar estela
        if self.show_trail:
            self.update_trail(pos)
        
        # Actualizar vector velocidad
        if self.show_velocity:
            self.update_velocity_vector(pos, v_mag)
        
        self.update_info_text()
        self.render_window.Render()
    
    
    def key_press_callback(self, obj, event):
        """Callback teclado."""
        key = self.interactor.GetKeySym()
        
        if key in ['plus', 'equal']:
            self.speed *= 1.5
            print(f"Velocidad: {self.speed:.0f}x")
        
        elif key == 'minus':
            self.speed /= 1.5
            if self.speed < 1:
                self.speed = 1
            print(f"Velocidad: {self.speed:.0f}x")
        
        elif key == 'space':
            self.paused = not self.paused
            print("PAUSADO" if self.paused else "ACTIVO")
        
        elif key == 'r':
            self.phase = 'initial'
            self.time_in_phase = 0
            self.total_time = 0
            self.current_angle = 0
            self.trail_points.clear()
            print("RESET")
        
        elif key == 't':
            self.show_trail = not self.show_trail
            self.trail_actor.SetVisibility(self.show_trail)
            print(f"Estela: {'ON' if self.show_trail else 'OFF'}")
        
        elif key == 'v':
            self.show_velocity = not self.show_velocity
            self.velocity_actor.SetVisibility(self.show_velocity)
            print(f"Vector velocidad: {'ON' if self.show_velocity else 'OFF'}")
        
        elif key == 'z':
            self.auto_zoom = not self.auto_zoom
            print(f"Auto-zoom: {'ON' if self.auto_zoom else 'OFF'}")
    
    
    def run(self):
        """Ejecuta simulación."""
        self.setup_renderer()
        
        self.interactor.AddObserver('TimerEvent', self.animation_callback)
        self.interactor.CreateRepeatingTimer(33)
        self.interactor.AddObserver('KeyPressEvent', self.key_press_callback)
        
        print("\n" + "─"*70)
        print("CONTROLES:")
        print("  [+/-]   Velocidad")
        print("  [SPACE] Pausa")
        print("  [R]     Reset")
        print("  [T]     Toggle estela")
        print("  [V]     Toggle vector velocidad")
        print("  [Z]     Toggle auto-zoom")
        print("  Mouse   Rotar/Zoom/Pan")
        print("  [Q]     Salir")
        print("─"*70 + "\n")
        
        self.render_window.Render()
        self.interactor.Start()
        
        print("\n✓ Simulación cerrada\n")


if __name__ == "__main__":
    import sys
    
    # Revisar si se pasaron argumentos desde línea de comando
    if len(sys.argv) >= 3:
        try:
            h1 = float(sys.argv[1])
            h2 = float(sys.argv[2])
            print(f"Argumentos recibidos: h1={h1} km, h2={h2} km")
        except:
            print("Error parseando argumentos, usando valores por defecto")
            h1, h2 = 400, 35786
    else:
        # Valores por defecto
        h1, h2 = 400, 35786
    
    sim = AdvancedHohmannSimulator(h1_km=h1, h2_km=h2)
    sim.run()