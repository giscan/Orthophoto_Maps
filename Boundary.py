import numpy as np
from osgeo import ogr

def boundary(image, eo, R, dem, pixel_size, focal_length):
    inverse_R = R.transpose()

    image_vertex = getVertices(image, pixel_size, focal_length)  # shape: 3 x 4

    proj_coordinates = projection(image_vertex, eo, inverse_R, dem)

    bbox = np.empty(shape=(4, 1))
    bbox[0] = min(proj_coordinates[0, :])  # X min
    bbox[1] = max(proj_coordinates[0, :])  # X max
    bbox[2] = min(proj_coordinates[1, :])  # Y min
    bbox[3] = max(proj_coordinates[1, :])  # Y max

    return bbox

def getVertices(image, pixel_size, focal_length):
    rows = image.shape[0]
    cols = image.shape[1]

    # (1) ------------ (2)
    #  |     image      |
    #  |                |
    # (4) ------------ (3)

    vertices = np.empty(shape=(3, 4))

    vertices[0, 0] = -cols * pixel_size / 2
    vertices[1, 0] = rows * pixel_size / 2

    vertices[0, 1] = cols * pixel_size / 2
    vertices[1, 1] = rows * pixel_size / 2

    vertices[0, 2] = cols * pixel_size / 2
    vertices[1, 2] = -rows * pixel_size / 2

    vertices[0, 3] = -cols * pixel_size / 2
    vertices[1, 3] = -rows * pixel_size / 2

    vertices[2, :] = -focal_length

    return vertices

def projection(vertices, eo, rotation_matrix, dem):
    coord_GCS = np.dot(rotation_matrix, vertices)
    scale = (dem - eo[2]) / coord_GCS[2]

    plane_coord_GCS = scale * coord_GCS[0:2] + [[eo[0]], [eo[1]]]

    return plane_coord_GCS

def export_bbox_to_wkt(bbox, dst):
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(bbox[0][0], bbox[2][0])   # Xmin, Ymin
    ring.AddPoint(bbox[0][0], bbox[3][0])   # Xmin, Ymax
    ring.AddPoint(bbox[1][0], bbox[3][0])   # Xmax, Ymax
    ring.AddPoint(bbox[1][0], bbox[2][0])   # Xmax, Ymin
    ring.AddPoint(bbox[0][0], bbox[2][0])   # Xmin, Ymin

    geom_poly = ogr.Geometry(ogr.wkbPolygon)
    geom_poly.AddGeometry(ring)
    wkt = geom_poly.ExportToWkt()

    f = open(dst + '.txt', 'w')
    f.write(wkt)
    f.close()
