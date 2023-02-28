import vtk
# Step 1: Read the 3D model using vtkSTLReader
reader = vtk.vtkSTLReader()
reader.SetFileName('/home/supreeths/work/winter/graphics/Graphics-Assignment/assignment_1/files/teapot.stl')
reader.Update()
total_vertices = reader.GetOutput().GetNumberOfPoints()
model = reader.GetOutput()

# Step 2: Create a plane at the center of the model
center = model.GetCenter()
print(f"Center of model {center}")
plane = vtk.vtkPlane()
plane.SetOrigin(center)
plane.SetNormal(1, 0, 1)

# Step 3: Clip the model using the plane
clipper = vtk.vtkClipPolyData()
clipper.SetInputData(model)
clipper.SetClipFunction(plane)
clipper.SetValue(0)
clipper.Update()
num_vertices_clip = clipper.GetOutput().GetNumberOfPoints()
print(f"Number of vertices = {reader.GetOutput().GetNumberOfPoints()}")
print(f"Number of vertices in clipped out part: {num_vertices_clip}")
print(f"Number of vertices in remaining part: {total_vertices - num_vertices_clip}")

# Step 4: Cut the clipped model using the plane
cutter = vtk.vtkCutter()
cutter.SetInputData(clipper.GetOutput())
cutter.SetCutFunction(plane)
cutter.Update()

# Step 5: Extract the triangles from the cutter output
triangleFilter = vtk.vtkTriangleFilter()
triangleFilter.SetInputData(cutter.GetOutput())
triangleFilter.Update()

# Step 6: Create a stripper to merge the triangles into polylines
stripper = vtk.vtkStripper()
stripper.SetInputData(triangleFilter.GetOutput())
stripper.Update()

# Display the original model in wireframe representation
mapper_orig = vtk.vtkPolyDataMapper()
mapper_orig.SetInputData(model)
actor_orig = vtk.vtkActor()
actor_orig.SetMapper(mapper_orig)
actor_orig.GetProperty().SetRepresentationToWireframe()

# Display the clipped part of the model in surface representation
mapper_clipped = vtk.vtkPolyDataMapper()
mapper_clipped.SetInputData(clipper.GetOutput())
actor_clipped = vtk.vtkActor()
actor_clipped.SetMapper(mapper_clipped)

# Display the intersection area in red color
mapper_intersection = vtk.vtkPolyDataMapper()
mapper_intersection.SetInputData(stripper.GetOutput())
actor_intersection = vtk.vtkActor()
actor_intersection.SetMapper(mapper_intersection)
actor_intersection.GetProperty().SetColor(1, 0, 0)

sample = vtk.vtkSampleFunction()
sample.SetImplicitFunction(plane)
sample.SetModelBounds(model.GetBounds())

# Create a contour filter from the sample function
contour = vtk.vtkContourFilter()
contour.SetInputConnection(sample.GetOutputPort())
contour.SetValue(0, 0)

# Create a mapper and actor for the plane and set their properties
mapper_plane = vtk.vtkPolyDataMapper()
mapper_plane.SetInputConnection(contour.GetOutputPort())
actor_plane = vtk.vtkActor()
actor_plane.SetMapper(mapper_plane)
actor_plane.GetProperty().SetColor(0, 1, 0)
actor_plane.GetProperty().SetOpacity(0.5)

# Set up the render window and add actors to the renderer
renderer = vtk.vtkRenderer()
renderer.AddActor(actor_orig)
renderer.AddActor(actor_clipped)
renderer.AddActor(actor_intersection)
renderer.AddActor(actor_plane)

# Set up the render window and interactor
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetSize(800, 800)
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Start the interaction and rendering loop
interactor.Initialize()
render_window.Render()
interactor.Start()
