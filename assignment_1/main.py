import functools
from dataclasses import dataclass
from enum import Enum, auto
from timeit import default_timer as _timer

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2

from vtkmodules.vtkFiltersCore import vtkPolyDataNormals
from vtkmodules.vtkIOGeometry import vtkSTLReader

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer, vtkLight
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


def timer(func):
    """Print the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = _timer()    # 1
        func(*args, **kwargs)
        end_time = _timer()      # 2
        run_time = (end_time - start_time)*1000    # 3
        print(f"Finished {args[2].name} operation in {run_time:.4f} milli seconds")
        return
    return wrapper_timer


def main():
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

    source = get_source()
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
    iren.Start()


def get_source():
    reader = vtkSTLReader()
    reader.SetFileName("/home/supreeths/work/winter/graphics/assignment_1/files/pug.stl")
    reader.Update()
    return reader


@timer
def test_rendering(_source, coordinates: ViewPortCoordinates, shade_type: ShadeType, rw):
    camera = None
    ren = vtkRenderer()

    light = vtkLight()
    light.SetLightTypeToSceneLight()
    light.SetAmbientColor(1, 1, 1)
    light.SetDiffuseColor(1, 1, 1)
    light.SetSpecularColor(1, 1, 1)
    light.SetPosition(-100, 100, 25)
    light.SetFocalPoint(0, 0, 0)
    light.SetIntensity(0.8)

    rw.AddRenderer(ren)
    ren.SetViewport(coordinates.x_min, coordinates.y_min, coordinates.x_max, coordinates.y_max)
    ren.SetActiveCamera(camera)
    mapper = vtkPolyDataMapper()

    normals = vtkPolyDataNormals()
    normals.SetInputConnection(_source.GetOutputPort())

    mapper.SetInputConnection(normals.GetOutputPort())
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
    # ren.AddLight(light)
    ren.AddActor(actor)
    ren.ResetCamera()


if __name__ == '__main__':
    main()
