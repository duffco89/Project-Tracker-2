'''
=============================================================
c:/1work/Python/djcode/pjtk2/pjtk2/spatial_fcts.py
Created: 10 Jul 2014 08:46:48


DESCRIPTION:



A. Cottrill
=============================================================
'''
from django.contrib.gis.db.models import Collect

from pjtk2.models import SamplePoint, Project
from olwidget.widgets import InfoMap, InfoLayer, Map



def empty_map(map_options=dict()):
    """Return an empty info map object.  Options is an optional
    dictionary that control basic attributes of the map - different
    maps can be returned by diffent users/projects

    """

    lat = map_options.get('lat', 45)
    lon = map_options.get('lon', -82)
    zoom = map_options.get('zoom', 7)
    zoom2extent = map_options.get('zoom2extent', False)
    height = map_options.get('height', '600px')
    width = map_options.get('width', '600px')

    mymap = InfoMap(
        None,
        {'default_lat': lat,
         'default_lon': lon,
         'default_zoom': zoom,
         'zoom_to_data_extent': zoom2extent,
         'map_div_style': {'width': width, 'height': height}}
    )
    return mymap




def get_map(points, roi=None, map_options={}):
    """

    Arguments:
    - `points`:
    """
    lat = map_options.get('lat', 45)
    lon = map_options.get('lon', -82)
    zoom = map_options.get('zoom', 7)
    zoom2extent = map_options.get('zoom2extent', False)
    height = map_options.get('height', '600px')
    width = map_options.get('width', '600px')

    layers = []

    if len(points)>0:
        if roi:
            style = {'overlay_style': {'fill_color': '#0000FF',
                               'fill_opacity': 0,
                               'stroke_color':'#0000FF'},
                     'name':'Region of Interest'}
            #polygon = InfoLayer([roi,style])
            polygon =  InfoLayer([[roi.wkt, "Region Of Interest"]] ,style)
            try:
                layers.extend(polygon)
            except TypeError:
                layers.append(polygon)
            zoom2extent = True

        for pt in points:
            pt_layer = InfoLayer([[pt[1].wkt, str(pt[0])]],{'name':str(pt[0])})
            try:
                layers.extend(pt_layer)
            except TypeError:
                layers.append(pt_layer)

        mymap = Map(
            layers,
            {'default_lat': lat,
             'default_lon': lon,
             'default_zoom': zoom,
             'zoom_to_data_extent': zoom2extent,
             'map_div_style': {'width': width, 'height': height}}
            )
    else:
        mymap = empty_map(map_options)
    return mymap




def find_roi_projects(roi, project_types=None, first_year=None, last_year=None):
    """Return a three element dictionary containing lists of projects that
       are entirely contained within and overlap with the region-of-interest
       (roi), and a list of points to be plotted on mapping widget.

    Arguments:
    - `roi`: - region of interest a polygon

    """

    projects = {'contained':[], 'overlapping':[], 'map_points':[]}
    try:
        if roi.geom_type=='Polygon' or roi.geom_type=='MultiPolygon':
            #get the sample points that fall within the region of interest
            sample_points = SamplePoint.objects.filter(geom__within=roi)
            if project_types:
                sample_points=sample_points.filter(
                    project__project_type__in=project_types)
            if first_year:
                sample_points=sample_points.filter(
                    project__year__gte=first_year)
            if last_year:
                sample_points=sample_points.filter(
                    project__year__lte=last_year)

            sample_points = sample_points.order_by('-project__year')

            #get list of disticnt project codes
            prj_cds = list(set([x.project.prj_cd for x in sample_points]))
            #and the points (and their labels) that will be passed to map
            map_points = [['{}-{}'.format(x.project.prj_cd, x.sam), x.geom]
                             for x in sample_points]

            contained=[]
            overlapping = []

            #import pdb;pdb.set_trace()

            # now loop over project_codes, cacluate a convex hull for
            # the points associated with that project
            for prj in prj_cds:
                samples = SamplePoint.objects.filter(project__prj_cd=prj)
                #samples = samples.collect()
                #this is ugly but works for now:
                samples = list(samples.aggregate(Collect('geom')).values())[0]
                hull = samples.convex_hull
                #if the convex hull for that project is contained
                #in roi add it to contained
                if roi.contains(hull):
                    contained.append(Project.objects.get(
                        prj_cd=prj))
                else:
                    #otherwise it's just overlapping
                    overlapping.append(Project.objects.get(
                        prj_cd=prj))
            projects['contained'] = contained
            projects['overlapping'] = overlapping
            projects['map_points'] = map_points

    except AttributeError:
        pass

    return(projects)
