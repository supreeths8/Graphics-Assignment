import vtk


# Helper functions
def clip_model():
    """
    Clips the model using the vtkClipPolyData method and set it to the model view and the model plane
    :return clipper
    """
    clipper = vtk.vtkClipPolyData()
    clipper.SetInputData(model_view)
    clipper.SetClipFunction(model_plane)
    clipper.SetValue(0)
    clipper.Update()
    return clipper


def cut_model():
    """
    Cuts the model plane using the vtkCutter method
    :return: cutter - cut-out model
    """
    cutter = vtk.vtkCutter()
    cutter.SetInputData(model_clipper.GetOutput())
    cutter.SetCutFunction(model_plane)
    cutter.Update()
    return cutter


def calculate_and_print_clipped_vertices():
    """
    Computes the clipped vertices count and prints them
    :return: count_clipped_vertices - vertices after clipping
    """
    count_clipped_vertices = model_clipper.GetOutput().GetNumberOfPoints()
    print(f"Actual Vertex Count = {stl_reader.GetOutput().GetNumberOfPoints()}")
    print(f"Vertices Count in clipped region = {count_clipped_vertices}")
    print(f"Vertices Count in remaining region = {vertex_count - count_clipped_vertices}")
    return count_clipped_vertices


def extract_triangles():
    """
    Extracts the triangles from the model_cutter using vtkTriangleFilter method
    :return: triangle_extractor - extracted triangles
    """
    triangle_extractor = vtk.vtkTriangleFilter()
    triangle_extractor.SetInputData(model_cutter.GetOutput())
    triangle_extractor.Update()
    return triangle_extractor


def strip_extracted_triangles():
    """
    Creates and strips region from the extracted triangles
    :return: stripper - stripped out region
    """
    stripper = vtk.vtkStripper()
    stripper.SetInputData(vtk_triangle_filter.GetOutput())
    stripper.Update()
    return stripper


def setup_display():
    """
    Prepares the vtk View
    :return: local_actor, local_clipper_actor, local_actor_intersection
    """
    mapper = vtk.vtkPolyDataMapper()
    clipped_mapper = vtk.vtkPolyDataMapper()
    mapper_intersection = vtk.vtkPolyDataMapper()

    mapper.SetInputData(model_view)
    local_actor = vtk.vtkActor()
    local_actor.SetMapper(mapper)
    local_actor.GetProperty().SetRepresentationToWireframe()

    # Display the clipped part of the model in surface representation
    clipped_mapper.SetInputData(model_clipper.GetOutput())
    local_clipper_actor = vtk.vtkActor()
    local_clipper_actor.SetMapper(clipped_mapper)

    # Display the intersection area
    mapper_intersection.SetInputData(model_stripper.GetOutput())
    local_actor_intersection = vtk.vtkActor()
    local_actor_intersection.SetMapper(mapper_intersection)
    local_actor_intersection.GetProperty().SetColor(0.57, 0.68, 0.8)

    return local_actor, local_clipper_actor, local_actor_intersection


def create_sample():
    """
    Creates a returns a sample using vtkSampleFunction on the model plane
    :return: sample_function
    """
    sample_function = vtk.vtkSampleFunction()
    sample_function.SetImplicitFunction(model_plane)
    sample_function.SetModelBounds(model_view.GetBounds())
    return sample_function


def create_contour_filter():
    """
    Prepares and returns the contour filter using vtkContourFilter method
    :return: contour_filter
    """
    contour_filter = vtk.vtkContourFilter()
    contour_filter.SetInputConnection(sample.GetOutputPort())
    contour_filter.SetValue(0, 0)
    return contour_filter


def generate_view_and_interactor():
    """
    Create a mapper plane, actor plane, sets up a renderer along with the window
    """
    mapper_plane = vtk.vtkPolyDataMapper()
    mapper_plane.SetInputConnection(vtk_contour_filter.GetOutputPort())
    actor_plane = vtk.vtkActor()
    actor_plane.SetMapper(mapper_plane)
    actor_plane.GetProperty().SetColor(0.57, 0.68, 0.8)
    actor_plane.GetProperty().SetOpacity(0.7)

    # Set up the render window and add actors to the renderer
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.AddActor(clipper_actor)
    renderer.AddActor(actor_intersection)
    renderer.AddActor(actor_plane)

    # Set up the render window and interactor
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(1366, 768)
    start_interactor(render_window)


def start_interactor(render_window):
    """
    Starts the interactor using the rendered window
    :param render_window: view to be rendered
    """
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Start the interaction and rendering loop
    interactor.Initialize()
    render_window.Render()
    interactor.Start()


# Reading the local STL file using vtkSTLReader()
stl_reader = vtk.vtkSTLReader()
stl_reader.SetFileName("/home/supreeths/work/winter/graphics/Graphics-Assignment/assignment_1/files/pug.stl")
stl_reader.Update()
vertex_count = stl_reader.GetOutput().GetNumberOfPoints()

# Setting up model representation
model_view = stl_reader.GetOutput()

# Setting up the plane
model_centre = model_view.GetCenter()
model_plane = vtk.vtkPlane()

# Adding origin at the centre of model_view and assigning normal
model_plane.SetOrigin(model_centre)
model_plane.SetNormal(1, 0, 1)

# Clipping and cutting the model using model_plane
model_clipper = clip_model()
model_cutter = cut_model()

# Calculating and Printing vertices
clipped_vertex_count = calculate_and_print_clipped_vertices()

# Extracting triangles from the model_cutter
vtk_triangle_filter = extract_triangles()

# Creating a stripper from extracted triangles
model_stripper = strip_extracted_triangles()

# Setup display
actor, clipper_actor, actor_intersection = setup_display()

# Create a Sample and apply contour filter on it
sample = create_sample()
vtk_contour_filter = create_contour_filter()

# Generate view and setup interactor
generate_view_and_interactor()
