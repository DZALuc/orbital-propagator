"""
Perturbations Visualization - Simplified

Versión simplificada con efectos exagerados para visualización clara.

Author: Damián Zúñiga Avelar
Date: Mayo 2026
"""

import vtk
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.propagator import circular_velocity


class SimplePerturbationsDemo:
    """Demo simplificado de perturbaciones con efectos exagerados."""
    
    def __init__(self):
        """Inicializa demo."""
        
        print(f"\n{'='*70}")
        print(f"  PERTURBATIONS DEMO - SIMPLIFIED")
        print(f"{'='*70}\n")
        
        self.R_earth = 6371.0
        self.altitude = 400.0
        self.r = self.R_earth + self.altitude
        
        # Parámetros orbitales
        self.period = 2 * np.pi * np.sqrt((self.r * 1000)**3 / 398600.4418e9)  # segundos
        self.omega = 2 * np.pi / self.period
        
        # Estado
        self.time = 0.0
        self.speed = 50.0
        self.paused = False
        
        # Exageración de efectos (para visualización)
        self.j2_strength = 0.05  # Factor de exageración J2
        self.drag_strength = 0.001  # Factor de exageración drag
        
# Ángulos de los 3 satélites (separados inicialmente)
        self.angle_ideal = 0.0           # 0° - Ideal
        self.angle_j2 = np.pi / 3        # 60° - J2
        self.angle_full = 2 * np.pi / 3  # 120° - Full

        # Decay por drag (radio decreciente)
        self.r_full = self.r
        
        # Precesión J2 (cambio en plano orbital)
        self.inclination_j2 = 0.0
        
        # VTK
        self.renderer = None
        self.render_window = None
        self.interactor = None
        
        self.sat_ideal = None
        self.sat_j2 = None
        self.sat_full = None
        
        self.vector_j2 = None
        self.vector_drag = None
        
        self.text_actor = None
        
        self.show_vectors = True
        
        print("Configuración:")
        print(f"  Altitud: {self.altitude} km")
        print(f"  Periodo: {self.period/60:.1f} min")
        print(f"  J2 exagerado: {self.j2_strength}x")
        print(f"  Drag exagerado: {self.drag_strength}x")
        print()
    
    
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
    
    
    def create_orbit_ring(self, radius, color=(0.5, 0.5, 0.5)):
        """Crea anillo de órbita."""
        
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
        actor.GetProperty().SetLineWidth(2)
        actor.GetProperty().SetOpacity(0.3)
        
        return actor
    
    
    def create_satellite(self, color=(1, 1, 1), size=1.0):
        """Crea satélite."""
        
        sphere = vtk.vtkSphereSource()
        sphere.SetRadius(400 * size)
        sphere.SetThetaResolution(20)
        sphere.SetPhiResolution(20)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetSpecular(0.8)
        actor.GetProperty().SetSpecularPower(50)
        
        return actor
    
    
    def create_arrow(self, color=(1, 0, 0)):
        """Crea flecha para vectores."""
        
        arrow = vtk.vtkArrowSource()
        arrow.SetTipLength(0.3)
        arrow.SetTipRadius(0.15)
        arrow.SetShaftRadius(0.05)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(arrow.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetOpacity(0.8)
        
        return actor
    
    

    def create_label(self, text, position, color=(1, 1, 1)):
            """Crea etiqueta de texto 3D."""
            
            label = vtk.vtkVectorText()
            label.SetText(text)
            
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(label.GetOutputPort())
            
            actor = vtk.vtkFollower()
            actor.SetMapper(mapper)
            actor.SetScale(200, 200, 200)
            actor.SetPosition(position[0], position[1], position[2] + 500)  # Arriba del satélite
            actor.GetProperty().SetColor(color)
            
            return actor


    def update_arrow(self, arrow_actor, position, direction, length):
        """
        Actualiza posición y orientación de flecha.
        
        Parameters
        ----------
        arrow_actor : vtkActor
            Actor de la flecha
        position : tuple
            Posición base (x, y, z)
        direction : ndarray
            Vector dirección (será normalizado)
        length : float
            Longitud de la flecha
        """
        
        # Normalizar dirección
        dir_norm = np.linalg.norm(direction)
        if dir_norm > 0:
            direction = direction / dir_norm
        else:
            direction = np.array([1, 0, 0])
        
        # Crear transformación
        transform = vtk.vtkTransform()
        transform.Translate(position)
        
        # Rotar (arrow apunta en X por defecto)
        default_dir = np.array([1, 0, 0])
        
        if np.abs(np.dot(default_dir, direction)) < 0.9999:
            rotation_axis = np.cross(default_dir, direction)
            rotation_axis_norm = np.linalg.norm(rotation_axis)
            
            if rotation_axis_norm > 1e-6:
                rotation_axis = rotation_axis / rotation_axis_norm
                cos_angle = np.dot(default_dir, direction)
                angle_deg = np.degrees(np.arccos(np.clip(cos_angle, -1, 1)))
                
                transform.RotateWXYZ(angle_deg, rotation_axis)
        
        # Escalar
        transform.Scale(length, length, length)
        
        arrow_actor.SetUserTransform(transform)
    
    
    def create_info_text(self):
        """Crea texto."""
        
        text = vtk.vtkTextActor()
        text.GetTextProperty().SetFontSize(14)
        text.GetTextProperty().SetColor(1, 1, 1)
        text.GetTextProperty().SetBold(True)
        text.SetPosition(10, 10)
        
        return text
    
    
    def update_info_text(self):
        """Actualiza texto."""
        
        status = "⏸️ PAUSADO" if self.paused else "▶️ ACTIVO"
        
        # Diferencias
        pos_ideal = self.get_position_ideal()
        pos_j2 = self.get_position_j2()
        pos_full = self.get_position_full()
        
        diff_j2 = np.linalg.norm(np.array(pos_j2) - np.array(pos_ideal))
        diff_full = np.linalg.norm(np.array(pos_full) - np.array(pos_ideal))
        
        # Altitud actual
        r_full_current = np.linalg.norm(pos_full)
        alt_loss = self.r - r_full_current
        
        info = f"""PERTURBATIONS DEMO (EFECTOS EXAGERADOS)

Estado: {status} | Velocidad: {self.speed:.0f}x
Tiempo: {self.time/3600:.1f} horas ({self.time/86400:.2f} días)

Satélites:
  ⚪ Ideal (gris)      - Sin perturbaciones
  🟡 J2 only (amarillo) - Precesión: {np.degrees(self.inclination_j2):.2f}° | Δr = {diff_j2:.1f} km
  🔴 Full (rojo)       - Decay: {alt_loss:.1f} km | Δr = {diff_full:.1f} km

Vectores: {'ON' if self.show_vectors else 'OFF'}
  🟡 Amarillo = Fuerza J2 (oblateness)
  🔵 Cyan = Drag atmosférico

[+/-] Velocidad  [SPACE] Pausa  [V] Vectores  [R] Reset  [Q] Salir

NOTA: Efectos exagerados {int(self.j2_strength*100)}x y {int(self.drag_strength*1000)}x para visualización
"""
        self.text_actor.SetInput(info)
    
    
    def get_position_ideal(self):
        """Posición satélite ideal."""
        x = self.r * np.cos(self.angle_ideal)
        y = self.r * np.sin(self.angle_ideal)
        z = 0.0
        return (x, y, z)
    
    
    def get_position_j2(self):
        """Posición satélite con J2."""
        # J2 causa precesión del plano orbital
        x = self.r * np.cos(self.angle_j2)
        y = self.r * np.sin(self.angle_j2) * np.cos(self.inclination_j2)
        z = self.r * np.sin(self.angle_j2) * np.sin(self.inclination_j2)
        return (x, y, z)
    
    
    def get_position_full(self):
        """Posición satélite con J2 + Drag."""
        # Drag causa decay del radio
        x = self.r_full * np.cos(self.angle_full)
        y = self.r_full * np.sin(self.angle_full)
        z = 0.0
        return (x, y, z)
    
    
    def setup_renderer(self):
        """Configura escena."""
        
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0, 0, 0.05)
        
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.SetSize(1800, 1000)
        self.render_window.AddRenderer(self.renderer)
        self.render_window.SetWindowName("Perturbations Demo - Simplified")
        
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)
        
        # Tierra
        earth = self.create_earth()
        self.renderer.AddActor(earth)
        
        # Anillo órbita referencia
        ring = self.create_orbit_ring(self.r, (0.5, 0.5, 0.5))
        self.renderer.AddActor(ring)
        
        # Satélites
        print("Creando satélites...")
        
        self.sat_ideal = self.create_satellite((1.0, 1.0, 1.0), size=.5)  # Blanco y más grande    
        self.renderer.AddActor(self.sat_ideal)
        print("  ✓ Satélite IDEAL (gris)")
        
        self.sat_j2 = self.create_satellite((1, 1, 0), size=.5)
        self.renderer.AddActor(self.sat_j2)
        print("  ✓ Satélite J2 (amarillo)")
        
        self.sat_full = self.create_satellite((1, 0.2, 0.2), size=.5)
        self.renderer.AddActor(self.sat_full)
        print("  ✓ Satélite FULL (rojo)")
        

        # Labels para satélites
        self.label_ideal = self.create_label("IDEAL", self.get_position_ideal(), (1, 1, 1))
        self.label_ideal.SetCamera(self.renderer.GetActiveCamera())
        self.renderer.AddActor(self.label_ideal)
        
        self.label_j2 = self.create_label("J2", self.get_position_j2(), (1, 1, 0))
        self.label_j2.SetCamera(self.renderer.GetActiveCamera())
        self.renderer.AddActor(self.label_j2)
        
        self.label_full = self.create_label("DRAG", self.get_position_full(), (1, 0.2, 0.2))
        self.label_full.SetCamera(self.renderer.GetActiveCamera())
        self.renderer.AddActor(self.label_full)


        # Flechas vectores
        self.vector_j2 = self.create_arrow((1, 1, 0))
        self.renderer.AddActor(self.vector_j2)
        
        self.vector_drag = self.create_arrow((0, 1, 1))
        self.renderer.AddActor(self.vector_drag)
        
        # Luces
        light = vtk.vtkLight()
        light.SetPosition(50000, 20000, 30000)
        light.SetIntensity(1.2)
        self.renderer.AddLight(light)


        # LUZ ADICIONAL (para ver mejor los satélites)
        light2 = vtk.vtkLight()
        light2.SetPosition(-50000, -20000, 30000)
        light2.SetIntensity(0.8)
        self.renderer.AddLight(light2)
        
        # Luz ambiental
        self.renderer.SetAmbient(0.3, 0.3, 0.3)
        
        # Texto
        self.text_actor = self.create_info_text()
        self.renderer.AddActor2D(self.text_actor)
        
        # Cámara
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(self.r * 2.5, self.r * 2.5, self.r * 1.5)
        camera.SetFocalPoint(0, 0, 0)
        self.renderer.ResetCamera()
        
        # Actualizar posiciones iniciales
        self.update_positions()
        self.update_info_text()
        
        print("✓ Escena configurada\n")
    
    
    def update_positions(self):
        """Actualiza posiciones."""
        
        # Posiciones
        pos_ideal = self.get_position_ideal()
        pos_j2 = self.get_position_j2()
        pos_full = self.get_position_full()
        
        # Actualizar satélites
        self.sat_ideal.SetPosition(pos_ideal)
        self.sat_j2.SetPosition(pos_j2)
        self.sat_full.SetPosition(pos_full)
    
        self.label_ideal.SetPosition(pos_ideal[0], pos_ideal[1], pos_ideal[2] + 500)
        self.label_j2.SetPosition(pos_j2[0], pos_j2[1], pos_j2[2] + 500)
        self.label_full.SetPosition(pos_full[0], pos_full[1], pos_full[2] + 500)

        
        # Vectores de perturbación
        if self.show_vectors:
            # Vector J2 (perpendicular al plano, causa precesión)
            # Simplificado: apunta fuera del plano
            j2_dir = np.array([0, -np.sin(self.angle_j2), 1])
            self.update_arrow(self.vector_j2, pos_j2, j2_dir, 2000)
            self.vector_j2.SetVisibility(True)
            
            # Vector Drag (opuesto a velocidad)
            # Tangencial hacia atrás
            drag_dir = np.array([
                np.sin(self.angle_full),
                -np.cos(self.angle_full),
                0
            ])
            self.update_arrow(self.vector_drag, pos_full, drag_dir, 2000)
            self.vector_drag.SetVisibility(True)
        else:
            self.vector_j2.SetVisibility(False)
            self.vector_drag.SetVisibility(False)
    
    
    def animation_callback(self, obj, event):
        """Callback animación."""
        
        if self.paused:
            return
        
        dt_real = 0.033
        dt_sim = dt_real * self.speed
        
        self.time += dt_sim
        
        # Órbita ideal (circular simple)
        self.angle_ideal += self.omega * dt_sim
        if self.angle_ideal >= 2 * np.pi:
            self.angle_ideal -= 2 * np.pi
        
        # Órbita con J2 (precesión)
        self.angle_j2 += self.omega * dt_sim
        # J2 causa precesión del plano
        self.inclination_j2 += self.j2_strength * dt_sim / 86400  # rad/día
        
        if self.angle_j2 >= 2 * np.pi:
            self.angle_j2 -= 2 * np.pi
        
        # Órbita con Drag (decay)
        self.angle_full += self.omega * dt_sim
        # Drag causa decay del radio
        self.r_full -= self.drag_strength * dt_sim / 86400  # km/día
        
        # Limitar decay
        if self.r_full < self.R_earth + 100:
            self.r_full = self.R_earth + 100
        
        if self.angle_full >= 2 * np.pi:
            self.angle_full -= 2 * np.pi
        
        self.update_positions()
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
        
        elif key == 'v':
            self.show_vectors = not self.show_vectors
            print(f"Vectores: {'ON' if self.show_vectors else 'OFF'}")
        
        elif key == 'r':
            self.time = 0
            self.angle_ideal = 0
            self.angle_j2 = 0
            self.angle_full = 0
            self.inclination_j2 = 0
            self.r_full = self.r
            self.update_positions()
            print("RESET")
    
    
    def run(self):
        """Ejecuta simulación."""
        
        self.setup_renderer()
        
        self.interactor.AddObserver('TimerEvent', self.animation_callback)
        self.interactor.CreateRepeatingTimer(33)
        self.interactor.AddObserver('KeyPressEvent', self.key_press_callback)
        
        print("─"*70)
        print("CONTROLES:")
        print("  [+/-]   Velocidad")
        print("  [SPACE] Pausa")
        print("  [V]     Toggle vectores")
        print("  [R]     Reset")
        print("  Mouse   Rotar/Zoom/Pan")
        print("  [Q]     Salir")
        print("\nNOTA: Los efectos están EXAGERADOS para visualización clara")
        print("─"*70 + "\n")
        
        self.render_window.Render()
        self.interactor.Start()
        
        print("\n✓ Simulación cerrada\n")


if __name__ == "__main__":
    sim = SimplePerturbationsDemo()
    sim.run()