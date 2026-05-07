"""
Create Simple Satellite Models

Genera modelos STL simples de satélites proceduralmente.

Author: Damián Zúñiga Avelar
Date: Abril 2026
"""

import numpy as np
from stl import mesh


def create_cubesat(size=0.1, output_file='models/satellites/cubesat.stl'):
    """
    Crea modelo STL de CubeSat (cubo simple).
    
    Parameters
    ----------
    size : float
        Tamaño del cubo (metros)
    output_file : str
        Ruta de salida
    """
    
    # Definir vértices del cubo
    vertices = np.array([
        [-size, -size, -size],
        [+size, -size, -size],
        [+size, +size, -size],
        [-size, +size, -size],
        [-size, -size, +size],
        [+size, -size, +size],
        [+size, +size, +size],
        [-size, +size, +size]
    ])
    
    # Definir caras (triángulos)
    faces = np.array([
        [0,3,1], [1,3,2],  # Bottom
        [0,4,7], [0,7,3],  # Left
        [4,5,6], [4,6,7],  # Top
        [5,1,2], [5,2,6],  # Right
        [2,3,6], [3,7,6],  # Back
        [0,1,5], [0,5,4]   # Front
    ])
    
    # Crear mesh
    cube = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            cube.vectors[i][j] = vertices[face[j]]
    
    # Guardar
    cube.save(output_file)
    print(f"✓ CubeSat creado: {output_file}")


def create_simple_satellite(length=2.0, radius=0.5, 
                           output_file='models/satellites/satellite.stl'):
    """
    Crea modelo STL de satélite simple (cilindro + paneles).
    
    Parameters
    ----------
    length : float
        Longitud del cuerpo (metros)
    radius : float
        Radio del cilindro (metros)
    output_file : str
        Ruta de salida
    """
    
    # Crear cilindro (cuerpo del satélite)
    n_segments = 16
    n_length = 10
    
    vertices = []
    
    # Generar vértices del cilindro
    for i in range(n_length):
        z = (i / (n_length - 1) - 0.5) * length
        for j in range(n_segments):
            angle = 2 * np.pi * j / n_segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            vertices.append([x, y, z])
    
    vertices = np.array(vertices)
    
    # Crear caras
    faces = []
    for i in range(n_length - 1):
        for j in range(n_segments):
            j_next = (j + 1) % n_segments
            
            # Dos triángulos por quad
            v0 = i * n_segments + j
            v1 = i * n_segments + j_next
            v2 = (i + 1) * n_segments + j_next
            v3 = (i + 1) * n_segments + j
            
            faces.append([v0, v1, v2])
            faces.append([v0, v2, v3])
    
    # Tapas
    # Tapa inferior
    center_bottom = len(vertices)
    vertices = np.vstack([vertices, [[0, 0, -length/2]]])
    for j in range(n_segments):
        j_next = (j + 1) % n_segments
        faces.append([center_bottom, j, j_next])
    
    # Tapa superior
    center_top = len(vertices)
    vertices = np.vstack([vertices, [[0, 0, length/2]]])
    offset = (n_length - 1) * n_segments
    for j in range(n_segments):
        j_next = (j + 1) % n_segments
        faces.append([center_top, offset + j_next, offset + j])
    
    faces = np.array(faces)
    
    # Crear mesh
    satellite = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            satellite.vectors[i][j] = vertices[face[j]]
    
    # Guardar
    satellite.save(output_file)
    print(f"✓ Satélite creado: {output_file}")


def create_sphere(radius=1.0, output_file='models/earth_sphere.stl'):
    """
    Crea esfera simple (para Tierra).
    
    Parameters
    ----------
    radius : float
        Radio (escala Tierra)
    output_file : str
        Ruta de salida
    """
    
    n_lat = 20
    n_lon = 40
    
    vertices = []
    
    # Generar vértices
    for i in range(n_lat + 1):
        lat = np.pi * (i / n_lat - 0.5)
        for j in range(n_lon):
            lon = 2 * np.pi * j / n_lon
            
            x = radius * np.cos(lat) * np.cos(lon)
            y = radius * np.cos(lat) * np.sin(lon)
            z = radius * np.sin(lat)
            
            vertices.append([x, y, z])
    
    vertices = np.array(vertices)
    
    # Crear caras
    faces = []
    for i in range(n_lat):
        for j in range(n_lon):
            j_next = (j + 1) % n_lon
            
            v0 = i * n_lon + j
            v1 = i * n_lon + j_next
            v2 = (i + 1) * n_lon + j_next
            v3 = (i + 1) * n_lon + j
            
            faces.append([v0, v1, v2])
            faces.append([v0, v2, v3])
    
    faces = np.array(faces)
    
    # Crear mesh
    sphere = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            sphere.vectors[i][j] = vertices[face[j]]
    
    # Guardar
    sphere.save(output_file)
    print(f"✓ Esfera (Tierra) creada: {output_file}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print(" "*20 + "GENERANDO MODELOS STL")
    print("="*70 + "\n")
    
    # Crear modelos
    create_cubesat(size=0.1)
    create_simple_satellite(length=2.0, radius=0.5)
    create_sphere(radius=6371.0)  # Radio Tierra en km
    
    print("\n" + "="*70)
    print("✓ Modelos STL generados")
    print("  Ver en: models/satellites/")
    print("="*70 + "\n")