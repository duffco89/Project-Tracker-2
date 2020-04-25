from .project_lists import urlpatterns as project_lists
from .project_crud import urlpatterns as project_crud
from .project_management import urlpatterns as project_management
from .project_images import urlpatterns as project_images
from .bookmarks import urlpatterns as bookmarks
from .misc import urlpatterns as misc

# app_name = "pjtk2"

urlpatterns = []

urlpatterns.extend(project_lists)
urlpatterns.extend(project_management)
urlpatterns.extend(project_crud)
urlpatterns.extend(project_images)
urlpatterns.extend(bookmarks)
urlpatterns.extend(misc)
