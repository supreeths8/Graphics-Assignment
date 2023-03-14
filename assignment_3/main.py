import os
import vtk
from dataclasses import dataclass


@dataclass
class ViewPortCoordinates:
    x_min: float
    x_max: float
    y_min: float
    y_max: float


xmins = iter([0, 0.33, 0.66])
xmaxs = iter([0.33, 0.66, 1])
ymins = iter([0, 0, 0])
ymaxs = iter([1, 1, 1])


def _make_coordinates():
    return ViewPortCoordinates(x_min=next(xmins), y_min=next(ymins), x_max=next(xmaxs), y_max=next(ymaxs))


os.chdir(os.path.dirname(__file__))

# Read data
reader = vtk.vtkDICOMImageReader()
reader.SetDirectoryName('./DICOM_dir')
reader.Update()

dimensions = reader.GetOutput().GetDimensions()
print("Image dimensions:", dimensions)
spacing = reader.GetOutput().GetSpacing()
resolution = (1/spacing[0], 1/spacing[1], 1/spacing[2])
print("Voxel resolution:", resolution)
imageData = reader.GetOutput()
scalarRange = imageData.GetScalarRange()
print("Minimum intensity:", scalarRange[0])
print("Maximum intensity:", scalarRange[1])

rw = vtk.vtkRenderWindow()
ren_vol = vtk.vtkRenderer()

coordinates = _make_coordinates()
ren_vol.SetViewport(coordinates.x_min, coordinates.y_min, coordinates.x_max,
    coordinates.y_max)
ren_vol.SetActiveCamera(None)
# Create colour transfer function
colorFunc = vtk.vtkColorTransferFunction()
colorFunc.AddRGBPoint(-3024, 0.0, 0.0, 0.0)
colorFunc.AddRGBPoint(-77, 0.54902, 0.25098, 0.14902)
colorFunc.AddRGBPoint(94, 0.882353, 0.603922, 0.290196)
colorFunc.AddRGBPoint(179, 1, 0.937033, 0.954531)
colorFunc.AddRGBPoint(260, 0.615686, 0, 0)
colorFunc.AddRGBPoint(3071, 0.827451, 0.658824, 1)

# Create opacity transfer function
alphaChannelFunc = vtk.vtkPiecewiseFunction()
alphaChannelFunc.AddPoint(-3024, 0.0)
alphaChannelFunc.AddPoint(-77, 0.0)
alphaChannelFunc.AddPoint(94, 0.29)
alphaChannelFunc.AddPoint(179, 0.55)
alphaChannelFunc.AddPoint(260, 0.84)
alphaChannelFunc.AddPoint(3071, 0.875)

# Instantiate necessary classes and create VTK pipeline
volume = vtk.vtkVolume()
ren_vol.ResetCamera()

# Define volume mapper
volumeMapper = vtk.vtkSmartVolumeMapper()
volumeMapper.SetInputConnection(reader.GetOutputPort())

# Define volume properties
volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.SetScalarOpacity(alphaChannelFunc)
volumeProperty.SetColor(colorFunc)
volumeProperty.ShadeOn()

# Set the mapper and volume properties
volume.SetMapper(volumeMapper)
volume.SetProperty(volumeProperty)

# Add the volume to the renderer
ren_vol.AddVolume(volume)


ren_iso = vtk.vtkRenderer()
coordinates = _make_coordinates()
ren_iso.SetViewport(coordinates.x_min, coordinates.y_min, coordinates.x_max,
    coordinates.y_max)
ren_iso.SetActiveCamera(ren_vol.GetActiveCamera())

marching_cubes = vtk.vtkMarchingCubes()
marching_cubes.SetInputConnection(reader.GetOutputPort())

# Set iso-surface value
iso_value = 350   # Set a suitable iso-surface value
marching_cubes.SetValue(0, iso_value)

# Create mapper and actor for iso-surface
iso_mapper = vtk.vtkPolyDataMapper()
iso_mapper.SetInputConnection(marching_cubes.GetOutputPort())

iso_actor = vtk.vtkActor()
iso_actor.SetMapper(iso_mapper)

# Create renderer and add volume actor and iso-surface actor
ren_iso.AddActor(iso_actor)

ren_both = vtk.vtkRenderer()
coordinates = _make_coordinates()
ren_both.SetViewport(coordinates.x_min, coordinates.y_min, coordinates.x_max,
    coordinates.y_max)
ren_both.SetActiveCamera(ren_vol.GetActiveCamera())
ren_both.AddVolume(volume)
ren_both.AddActor(iso_actor)
# Render the scene
rw.AddRenderer(ren_vol)
rw.AddRenderer(ren_iso)
rw.AddRenderer(ren_both)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(rw)
rw.SetSize(800, 800)
rw.Render()
iren.Start()
