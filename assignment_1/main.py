import os
from dataclasses import dataclass
from enum import Enum, auto

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2

from vtkmodules.vtkFiltersCore import vtkPolyDataNormals
from vtkmodules.vtkIOGeometry import vtkSTLReader
from vtkmodules.vtkIOImage import vtkJPEGWriter

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer, vtkWindowToImageFilter
)


@dataclass
class ViewPortCoordinates:
    x_min: float
    x_max: float
    y_min: float
    y_max: float


class ShadeType(Enum):
    wireframe = auto()
    flat = auto()
    gouraud = auto()
    phong = auto()


def main():
    input_stl_file = "./files/Easter_Basket.stl"
    output_result = "./outputs/Easter_Basket.jpg"
    rw = vtkRenderWindow()
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(rw)

    # Define viewport ranges.
    xmins = iter([0, .5, 0, .5])
    xmaxs = iter([0.5, 1, 0.5, 1])
    ymins = iter([0, 0, .5, .5])
    ymaxs = iter([0.5, 0.5, 1, 1])

    def _make_coordinates():
        return ViewPortCoordinates(x_min=next(xmins), y_min=next(ymins), x_max=next(xmaxs), y_max=next(ymaxs))

    source = load_source(input_stl_file)
    coordinates = _make_coordinates()
    test_rendering(source, coordinates, ShadeType.gouraud, rw)

    coordinates = _make_coordinates()
    test_rendering(source, coordinates, ShadeType.phong, rw)

    coordinates = _make_coordinates()
    test_rendering(source, coordinates, ShadeType.wireframe, rw)

    coordinates = _make_coordinates()
    test_rendering(source, coordinates, ShadeType.flat, rw)

    rw.Render()
    rw.SetWindowName('MultipleViewPorts')
    rw.SetSize(800, 800)
    writer = vtkJPEGWriter()
    window_to_image_filter = vtkWindowToImageFilter()
    window_to_image_filter.SetInput(rw)
    window_to_image_filter.SetInputBufferTypeToRGB()
    window_to_image_filter.ReadFrontBufferOff()
    window_to_image_filter.Update()
    writer.SetFileName(output_result)
    writer.SetInputConnection(window_to_image_filter.GetOutputPort())
    writer.Write()
    iren.Start()


def load_source(file: str):
    """
    Load the STL file and return the reader object
    :param file: STL file path
    :return: VTk STL reader
    """
    reader = vtkSTLReader()
    reader.SetFileName(file)
    reader.Update()
    os.chdir(os.path.dirname(__file__))
    print(f"File name: {file.split('/')[-1]}")
    print(f"Number of vertices = {reader.GetOutput().GetNumberOfPoints()}")
    return reader


def test_rendering(_source, coordinates: ViewPortCoordinates, shade_type: ShadeType, rw):
    """
    Render the STL object in the view port of the render window using the `coordinates` object and the `shading` type
    :param _source: Object to render
    :param coordinates: ViewPortCoordinates to specify the viewport in the render window
    :param shade_type: Shade type to use for the interpolation
    :param rw: VTK render window object
    :return:
    """
    camera = None
    ren = vtkRenderer()

    #  Set the view port for the object in the multi-viewport window
    ren.SetViewport(coordinates.x_min, coordinates.y_min, coordinates.x_max, coordinates.y_max)
    ren.SetActiveCamera(camera)

    # vtkPolyDataMapper is a class that maps polygonal data and that actually does
    # the mapping to the rendering/graphics hardware/software.
    # vtkPolyDataNormals is a filter that computes point and/or cell normals for a polygonal mesh.
    # It can reorder polygons to ensure consistent orientation across polygon neighbors.
    # Sharp edges can be split and points duplicated with separate normals to give crisp (rendered) surface definition.
    mapper = vtkPolyDataMapper()
    normals = vtkPolyDataNormals()
    normals.SetInputConnection(_source.GetOutputPort())
    mapper.SetInputConnection(normals.GetOutputPort())

    #  actor represents an object in the rendered scene
    actor = vtkActor()

    if shade_type is ShadeType.gouraud:
        actor.GetProperty().SetInterpolationToGouraud()
    elif shade_type is ShadeType.phong:
        actor.GetProperty().SetInterpolationToPhong()
    elif shade_type is ShadeType.flat:
        actor.GetProperty().SetInterpolationToFlat()
    elif shade_type is ShadeType.wireframe:
        actor.GetProperty().SetRepresentationToWireframe()
    actor.GetProperty().SetEdgeColor(1, 1, 1)
    actor.SetMapper(mapper)
    ren.AddActor(actor)
    ren.ResetCamera()
    rw.AddRenderer(ren)


if __name__ == '__main__':
    main()
