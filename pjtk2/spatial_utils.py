'''
=============================================================
c:/1work/Python/djcode/pjtk2/pjtk2/spatial_fcts.py
Created: 10 Jul 2014 08:46:48


DESCRIPTION:



A. Cottrill
=============================================================
'''

from pjtk2.models import SamplePoint, Project


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
                    project__year_lte=last_year)

            #get list of disticnt project codes
            prj_cds = list(set([x.project.prj_cd for x in sample_points]))
            #and the points (and their labels) that will be passed to map
            map_points = [['{}-{}'.format(x.project.prj_cd, x.sam), x.geom]
                             for x in sample_points]

            contained=[]
            overlapping = []

            # now loop over project_codes, cacluate a convex hull for
            # the points associated with that project
            for prj in prj_cds:
                samples = SamplePoint.objects.filter(project__prj_cd=prj)
                samples = samples.collect()
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
