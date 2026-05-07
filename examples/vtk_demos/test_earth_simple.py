"""
VTK Earth Simple - Versión que siempre funciona

Sin texturas, solo colores y geometría.

Author: Damián Zúñiga Avelar
Date: Abril 2026
"""

import vtk
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.propagator import circular_velocity, orbital_period


def create_earth(radius=6371.0):
    """Crea Tierra azul simple."""
    sphere = vtk.vtkSphereSource()
    sphere.SetCenter(0, 0, 0)
    sphere.SetRadius(radius)
    sphere.SetThetaResolution(100)
    sphere.SetPhiResolution(100)
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(sphere.GetOutputPort())
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.2, 0.5, 0.9)  # Azul océano
    
    return actor


def create_orbit_line(radius):
    """Crea línea de órbita."""
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
    actor.GetProperty().SetColor(1.0, 1.0, 0.0)
    actor.GetProperty().SetLineWidth(3)
    
    return actor


def create_satellite():
    """Crea satélite con paneles."""
    # Cuerpo
    cube = vtk.vtkCubeSource()
    cube.SetXLength(400)
    cube.SetYLength(400)
    cube.SetZLength(600)
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(cube.GetOutputPort())
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.9, 0.9, 0.9)
    
    return actor


def main():
    print("\n" + "="*70)
    print(" "*20 + "EARTH SIMULATOR SIMPLE")
    print("="*70 + "\n")
    
    # Parámetros
    R_earth = 6371.0
    altitude = 400.0
    orbital_radius = R_earth + altitude
    
    r_meters = orbital_radius * 1000
    orbital_velocity = circular_velocity(r_meters)
    period = orbital_period(r_meters) 
    
    print(f"LEO {altitude} km:")
    print(f"  Radio:    {orbital_radius:.1f} km")
    print(f"  Velocidad: {orbital_velocity:.1f} m/s")
    print(f"  Periodo:   {period/60:.2f} min\n")
    
    # Estado
    current_angle = [0.0]  # Lista para poder modificar en callback
    time_elapsed = [0.0]
    speed = [100.0]
    paused = [False]
    
    # Renderer
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.0, 0.0, 0.0)
    
    # Ventana
    window = vtk.vtkRenderWindow()
    window.SetSize(1400, 900)
    window.AddRenderer(renderer)
    window.SetWindowName("Earth Simulator Simple")
    
    # Interactor
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)
    
    # Añadir Tierra
    earth = create_earth(R_earth)
    renderer.AddActor(earth)
    
    # Añadir órbita
    orbit = create_orbit_line(orbital_radius)
    renderer.AddActor(orbit)
    
    # Añadir satélite
    satellite = create_satellite()
    renderer.AddActor(satellite)
    
    # Luces
    light = vtk.vtkLight()
    light.SetPosition(50000, 0, 0)
    light.SetFocalPoint(0, 0, 0)
    renderer.AddLight(light)
    
    # Texto
    text = vtk.vtkTextActor()
    text.GetTextProperty().SetFontSize(16)
    text.GetTextProperty().SetColor(1, 1, 1)
    text.SetPosition(10, 10)
    renderer.AddActor2D(text)
    
    # Cámara
    camera = renderer.GetActiveCamera()
    camera.SetPosition(15000, 15000, 15000)
    camera.SetFocalPoint(0, 0, 0)
    renderer.ResetCamera()
    
    # Callback animación
    def animate(obj, event):
        if paused[0]:
            return
        
        dt = 0.033 * speed[0]
        time_elapsed[0] += dt
        
        omega = 2 * np.pi / period
        current_angle[0] += omega * dt
        
        if current_angle[0] >= 2 * np.pi:
            current_angle[0] -= 2 * np.pi
        
        x = orbital_radius * np.cos(current_angle[0])
        y = orbital_radius * np.sin(current_angle[0])
        z = 0.0
        
        satellite.SetPosition(x, y, z)
        
        orbits = time_elapsed[0] / period
        status = "PAUSADO" if paused[0] else "ACTIVO"
        
        info = f"""LEO {altitude} km - {status}

Tiempo:    {time_elapsed[0]:.1f} s ({time_elapsed[0]/60:.2f} min)
Ángulo:    {np.degrees(current_angle[0]):.1f}°
Órbitas:   {orbits:.3f}
Velocidad: {speed[0]:.0f}x

[+/-] Velocidad  [SPACE] Pausa  [R] Reset  [Q] Salir
"""
        text.SetInput(info)
        window.Render()
    
    # Callback teclado
    def on_key(obj, event):
        key = interactor.GetKeySym()
        
        if key in ['plus', 'equal']:
            speed[0] *= 1.5
            print(f"Velocidad: {speed[0]:.0f}x")
        
        elif key == 'minus':
            speed[0] /= 1.5
            if speed[0] < 1.0:
                speed[0] = 1.0
            print(f"Velocidad: {speed[0]:.0f}x")
        
        elif key == 'space':
            paused[0] = not paused[0]
            print("PAUSADO" if paused[0] else "ACTIVO")
        
        elif key == 'r':
            current_angle[0] = 0.0
            time_elapsed[0] = 0.0
            print("RESET")
    
    # Conectar callbacks
    interactor.AddObserver('TimerEvent', animate)
    interactor.CreateRepeatingTimer(33)
    interactor.AddObserver('KeyPressEvent', on_key)
    
    print("Controles:")
    print("  [+/-]   Velocidad")
    print("  [SPACE] Pausa")
    print("  [R]     Reset")
    print("  Mouse   Rotar/Zoom")
    print("  [Q]     Salir\n")
    
    window.Render()
    interactor.Start()
    
    print("\n✓ Cerrado\n")


if __name__ == "__main__":
    main()