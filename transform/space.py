__author__ = 'tonycastronova'

import stdlib
import space_base
from shapely.geometry import LineString, MultiPoint, Point, Polygon






# TODO!  These should utilize database queries, see test_spatial.py.  Also, they should take actionID as input?

# adapted from https://github.com/ojdo/python-tools.git
class spatial_nearest_neighbor(space_base.Space):

    def __init__(self):
        super(spatial_nearest_neighbor,self).__init__()
        self.__params = {'max_distance':10}

    def name(self):
        return 'Nearest Neighbor'

    def transform(self, ingeoms, outgeoms):

        if isinstance(ingeoms[0], stdlib.Geometry):
            ingeoms = [i.geom() for i in ingeoms]  # convert Geometry objects into a list of shapely geometries
        if isinstance(outgeoms[0], stdlib.Geometry):
            outgeoms = [i.geom() for i in outgeoms]  # convert Geometry objects into a list of shapely geometries

        # get parameters
        max_distance = self.__params['max_distance']

        # todo: this should map everything to point sets
        # create multipoint feature from ingeoms
        in_pts = MultiPoint(ingeoms)

        # create container for mapped geometries
        mapped_geoms = []

        # map each outgeom to its respective ingeom
        for point in outgeoms:

            # get the search region for this point
            search_region = point.buffer(max_distance)
            interesting_points = search_region.intersection(in_pts)

            if not interesting_points:
                closest_point = None
            elif isinstance(interesting_points, Point):
                closest_point = interesting_points
            else:
                distances = [point.distance(ip) for ip in interesting_points
                             if point.distance(ip) > 0]
                closest_point = interesting_points[distances.index(min(distances))]

            mapped_geoms.append((point,closest_point))

        return mapped_geoms

    def get_params(self):
        return self.__params

    def set_param(self, name, value):
        if name in self.__params.keys():
            self.__params[name] = value

class spatial_closest_object(space_base.Space):

    def __init__(self):
            super(spatial_closest_object,self).__init__()

    def name(self):
        return 'Nearest Object - Point to Polygon'

    def transform(self, ingeoms, outgeoms):
        """Find the nearest geometry among a list, measured from fixed point.

        Args:
            outgeoms: a list of shapely geometry objects
            ingeoms: list of shapely Points

        Returns:
            dictionary of mapped geometries: {ingeom:outgeom,...}
        """

        # isolate the shapely geometries
        points = [geom.geom() for geom in ingeoms]
        polygons = [geom.geom() for geom in outgeoms]

        mapped = []

        i = 0
        for polygon in polygons:
            min_dist, min_index = min((polygon.distance(geom), k) for (k, geom) in enumerate(points))

            mapped.append([ingeoms[min_index], outgeoms[i]])

            i += 1
        return mapped



class spatial_intersect_polygon_point(space_base.Space):

    def __init__(self):
            super(spatial_intersect_polygon_point,self).__init__()

    def name(self):
        return 'Intersection - Polygon to Point'

    def transform(self, ingeoms, outgeoms):

        # isolate the shapely geometries
        polygons = [geom.geom() for geom in ingeoms]
        points = [geom.geom() for geom in outgeoms]

        if len(polygons) ==  0 or len(points) == 0:
            raise Exception('Number of geometries must be greater than 0.')

        # todo: what about MultiPoint, MultiPolygon?
        # assert that the correct shapes have been provided
        if polygons[0].geom_type != 'Polygon':
            raise Exception('Incorrect geometry type provided')
        if points[0].geom_type != 'Point':
            raise Exception('Incorrect geometry type provided')

        mapped = []

        i = 0

        for polygon in polygons:

            min_dist, min_index = min((polygon.distance(geom), k) for (k, geom) in enumerate(points))
            mapped.append([ingeoms[min_index], outgeoms[i]])

            i += 1
        return mapped

class spatial_exact_match(space_base.Space):
    def __init__(self):
        super(spatial_exact_match,self).__init__()

    def name(self):
        return 'Exact Match'

    def transform(self, ingeoms, outgeoms):

        mapped_geoms = []

        igeoms = [ingeoms[i].geom().to_wkt() for i in range(0, len(ingeoms))]
        ogeoms = [outgeoms[i].geom().to_wkt() for i in range(0, len(outgeoms))]

        for i in range(0, len(igeoms)):
            igeom = igeoms[i]
            if igeom in ogeoms:
                o = ogeoms.index(igeom)
                mapped_geoms.append((ingeoms[i], outgeoms[o]))
        return mapped_geoms

class SpatialInterpolation():
    NearestNeighbor = spatial_nearest_neighbor()
    NearestObject = spatial_closest_object()
    ExactMatch = spatial_exact_match()
    IntersectPolygonPoint = spatial_intersect_polygon_point()

    def methods(self):
        return [self.NearestNeighbor,self.NearestObject, self.ExactMatch, self.IntersectPolygonPoint]