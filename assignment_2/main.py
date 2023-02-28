import vtk
from vtkmodules.vtkCommonDataModel import vtkPlane
from vtkmodules.vtkFiltersCore import vtkClipPolyData
from vtkmodules.vtkFiltersSources import vtkConeSource
from vtkmodules.vtkInteractionWidgets import vtkImplicitPlaneWidget
from vtkmodules.vtkRenderingCore import vtkPolyDataMapper, vtkActor, vtkRenderer, vtkRenderWindow, \
    vtkRenderWindowInteractor
from vtkmodules.vtkRenderingLOD import vtkLODActor

cone = vtkConeSource()

coneMapper = vtkPolyDataMapper()
coneMapper.SetInputConnection( cone.GetOutputPort() )

coneActor = vtkActor()
coneActor.SetMapper( coneMapper )

ren1= vtkRenderer()
ren1.AddActor( coneActor )
ren1.SetBackground( 0, 0, 0 )

renWin = vtkRenderWindow()
renWin.AddRenderer( ren1 ) # selection part - green color part
plane = vtkPlane()
clipper = vtkClipPolyData()
clipper.SetInputConnection( cone.GetOutputPort() )
clipper.SetClipFunction( plane )
clipper.InsideOutOn()

selectMapper = vtkPolyDataMapper()
selectMapper.SetInputConnection( clipper.GetOutputPort() )

selectActor = vtkLODActor()
selectActor.SetMapper(selectMapper)
selectActor.GetProperty().SetColor(0, 1, 0)
selectActor.SetScale(1.01, 1.01, 1.01)

ren1.AddActor( selectActor )# selection part end

renWinInteractor = vtkRenderWindowInteractor()
renWinInteractor.SetRenderWindow( renWin )

def myCallback(obj, event):
    global plane, selectActor
    obj.GetPlane(plane)
    selectActor.VisibilityOn()

# ImplicitPlaneWidget - outlines and plane
planeWidget = vtkImplicitPlaneWidget()
planeWidget.SetInteractor( renWinInteractor )
planeWidget.SetPlaceFactor( 1 )
planeWidget.SetInputConnection(cone.GetOutputPort())
planeWidget.PlaceWidget()
planeWidget.AddObserver("InteractionEvent", myCallback)
planeWidget.On() # ImplicitPlaneWidget end

renWinInteractor.Start()