"""
VTK Basic Test

Primer test de VTK: renderizar Tierra + satélite.

Author: Damián Zúñiga Avelar
Date: Abril 2026
"""

import vtk
import numpy as np


def create_earth_sphere(radius=6371.0):
    """Crea esfera para Tierra."""
    
    sphere = vtk.vtkSphereSource()
    sphere.SetCenter(0, 0, 0)
    sphere.SetRadius(radius)
    sphere.SetThetaResolution(50)
    sphere.SetPhiResolution(50)
    
    # Mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(sphere.GetOutputPort())
    
    # Actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.2, 0.4, 0.8)  # Azul
    
    return actor


def create_marker_sphere(position, radius=200.0, color=(1.0, 0.0, 0.0)):
    """Crea esfera marcador para debugging."""
    
    sphere = vtk.vtkSphereSource()
    sphere.SetCenter(position)
    sphere.SetRadius(radius)
    sphere.SetThetaResolution(20)
    sphere.SetPhiResolution(20)
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(sphere.GetOutputPort())
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    
    return actor


def create_simple_satellite_geometry(position, size=300.0):
    """
    Crea geometría simple de satélite (cubo + paneles).
    
    Parameters
    ----------
    position : tuple
        (x, y, z) posición
    size : float
        Tamaño del satélite
    
    Returns
    -------
    actor : vtkActor
    """
    
    # Crear cubo (cuerpo)
    cube = vtk.vtkCubeSource()
    cube.SetXLength(size)
    cube.SetYLength(size)
    cube.SetZLength(size * 1.5)
    
    # Transform
    transform = vtk.vtkTransform()
    transform.Translate(position)
    
    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetInputConnection(cube.GetOutputPort())
    transform_filter.SetTransform(transform)
    
    # Mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(transform_filter.GetOutputPort())
    
    # Actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.8, 0.8, 0.8)  # Gris plata
    
    return actor


def load_stl_model(filename, scale=1.0, position=(0, 0, 0), color=(0.8, 0.8, 0.8)):
    """
    Carga modelo STL.
    
    Parameters
    ----------
    filename : str
        Ruta al archivo .stl
    scale : float
        Factor de escala
    position : tuple
        (x, y, z) posición
    color : tuple
        (r, g, b) color
    
    Returns
    -------
    actor : vtkActor
    """
    
    # Leer STL
    reader = vtk.vtkSTLReader()
    reader.SetFileName(filename)
    
    # Transform (escala + posición)
    transform = vtk.vtkTransform()
    transform.Translate(position)
    transform.Scale(scale, scale, scale)
    
    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetInputConnection(reader.GetOutputPort())
    transform_filter.SetTransform(transform)
    
    # Mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(transform_filter.GetOutputPort())
    
    # Actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    
    return actor


def main():
    """Test básico VTK."""
    
    print("\n" + "="*70)
    print(" "*25 + "VTK BASIC TEST")
    print("="*70 + "\n")
    
    # Crear renderer
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.05, 0.05, 0.05)  # Fondo casi negro
    
    # Crear ventana
    render_window = vtk.vtkRenderWindow()
    render_window.SetSize(1200, 800)
    render_window.AddRenderer(renderer)
    render_window.SetWindowName("VTK Test - Tierra + Satélite")
    
    # Interactor
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)
    
    # Añadir Tierra
    print("Añadiendo Tierra...")
    earth = create_earth_sphere(radius=6371.0)
    renderer.AddActor(earth)
    
    # Añadir satélite en LEO (400 km)
    print("Añadiendo satélite...")
    sat_position = (6771.0, 0, 0)  # Radio LEO
    
    # OPCIÓN 1: Geometría simple (siempre funciona)
    satellite = create_simple_satellite_geometry(sat_position, size=300.0)
    renderer.AddActor(satellite)
    
    # OPCIÓN 2: Marcador adicional (esfera roja brillante)
    marker = create_marker_sphere(sat_position, radius=200.0, color=(1.0, 0.2, 0.2))
    renderer.AddActor(marker)
    
    # OPCIÓN 3: Intentar cargar STL si existe
    try:
        satellite_stl = load_stl_model(
            'models/satellites/satellite.stl',
            scale=100.0,
            position=sat_position,
            color=(1.0, 0.8, 0.0)
        )
        renderer.AddActor(satellite_stl)
        print("  ✓ Modelo STL cargado")
    except:
        print("  ⚠️  Modelo STL no cargado (usando geometría simple)")
    
    # Añadir ejes de referencia
    axes = vtk.vtkAxesActor()
    axes.SetTotalLength(10000, 10000, 10000)
    renderer.AddActor(axes)
    
    # Añadir luz
    light = vtk.vtkLight()
    light.SetPosition(15000, 15000, 15000)
    light.SetFocalPoint(0, 0, 0)
    renderer.AddLight(light)
    
    # Configurar cámara
    camera = renderer.GetActiveCamera()
    camera.SetPosition(15000, 15000, 15000)
    camera.SetFocalPoint(0, 0, 0)
    renderer.ResetCamera()
    
    # Añadir texto informativo
    text = vtk.vtkTextActor()
    text.SetInput("VTK Test - Tierra + Satelite en LEO (400 km)\nBusca el cubo gris + esfera roja")
    text.GetTextProperty().SetFontSize(18)
    text.GetTextProperty().SetColor(1.0, 1.0, 1.0)
    text.SetPosition(10, 10)
    renderer.AddActor2D(text)
    
    # Info de posición
    info_text = vtk.vtkTextActor()
    info_text.SetInput(f"Satelite en: ({sat_position[0]:.0f}, {sat_position[1]:.0f}, {sat_position[2]:.0f}) km")
    info_text.GetTextProperty().SetFontSize(14)
    info_text.GetTextProperty().SetColor(0.8, 0.8, 1.0)
    info_text.SetPosition(10, 750)
    renderer.AddActor2D(info_text)
    
    print("\n" + "─"*70)
    print("Controles:")
    print("  - Click izquierdo + arrastrar: Rotar")
    print("  - Scroll: Zoom")
    print("  - Click derecho + arrastrar: Pan")
    print("  - 'q' o cerrar ventana: Salir")
    print("\nBUSCA:")
    print("  - Esfera AZUL grande = Tierra")
    print("  - Cubo GRIS pequeño = Satélite")
    print("  - Esfera ROJA pequeña = Marcador de posición")
    print("─"*70 + "\n")
    
    # Renderizar
    render_window.Render()
    interactor.Start()
    
    print("\n✓ Simulación cerrada\n")


if __name__ == "__main__":
    main()