

class SpatialHash(object):

    def __init__(self, cell_size=64):
        self.cell_size = cell_size
        self.contents = {}

    def _hash(self, point):
        return int(point[0] / self.cell_size), int(point[1] / self.cell_size)

    def insert_object_for_point(self, point, object):
        p = self._hash(point)
        self.contents.setdefault(p, []).append(object)
        return p

    def insert_object_for_rect(self, p1, p2, object):
        # hash the minimum and maximum points
        min, max = self._hash(p1), self._hash(p2)
        # iterate over the rectangular region
        for i in range(min[0], max[0] + 1):
            for j in range(min[1], max[1] + 1):
                # append to each intersecting cell
                self.contents.setdefault((i, j), []).append(object)

    def remove_object(self, object, key=None):
        if key:
            objectlist = self.contents[key]
            if object in objectlist:
                objectlist.remove(object)
        else:
            for key, objectlist in self.contents.items():
                if object in objectlist:
                    objectlist.remove(object)

    def clear_empty(self):
        to_delete = []
        for key, value in self.contents.items():
            if not value:
                to_delete.append(key)

        for key in to_delete:
            self.contents.pop(key, None)

    def get_objects_from_point(self, point, radius=None, type=None):
        if radius:
            result = []
            cells = []
            min = self._hash((point[0] - radius, point[1] - radius))
            max = self._hash((point[0] + radius, point[1] + radius))
            for i in range(min[0], max[0] + 1):
                for j in range(min[1], max[1] + 1):
                    if (i, j) in self.contents:
                        cells.append((i, j))
            for cell in cells:
                for object in self.contents[cell]:
                    if type:
                        if isinstance(object, type):
                            result.append(object)
                    else:
                        result.append(object)
            return result
        else:
            cell = self._hash(point)
            if type:
                if cell in self.contents:
                    result = []
                    for object in self.contents[cell]:
                        if isinstance(object, type):
                            result.append(object)
                    return result
            else:
                if cell in self.contents:
                    return self.contents[cell]
        return []

    def get_objects_from_line(self, p1, p2, type=None):
        start = self._hash(p1)
        stop = self._hash(p2)
        cells = self.get_line(start, stop)
        result = []
        for c in cells:
            if c in self.contents:
                for object in self.contents[c]:
                    if type:
                        if isinstance(object, type):
                            result.append(object)
                    else:
                        result.append(object)

        return result

    def get_objects_from_rect(self, p1, p2, type=None):
        pass

    def get_line(self, start, end):
        """Bresenham's Line Algorithm
        Produces a list of tuples from start and end

        >>> points1 = get_line((0, 0), (3, 4))
        >>> points2 = get_line((3, 4), (0, 0))
        >>> assert(set(points1) == set(points2))
        >>> print points1
        [(0, 0), (1, 1), (1, 2), (2, 3), (3, 4)]
        >>> print points2
        [(3, 4), (2, 3), (1, 2), (1, 1), (0, 0)]
        """
        # Setup initial conditions
        x1, y1 = start
        x2, y2 = end
        dx = x2 - x1
        dy = y2 - y1

        # Determine how steep the line is
        is_steep = abs(dy) > abs(dx)

        # Rotate line
        if is_steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2

        # Swap start and end points if necessary and store swap state
        swapped = False
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            swapped = True

        # Recalculate differentials
        dx = x2 - x1
        dy = y2 - y1

        # Calculate error
        error = int(dx / 2.0)
        ystep = 1 if y1 < y2 else -1

        # Iterate over bounding box generating points between start and end
        y = y1
        points = []
        for x in range(x1, x2 + 1):
            coord = (y, x) if is_steep else (x, y)
            points.append(coord)
            error -= abs(dy)
            if error < 0:
                y += ystep
                error += dx

        # Reverse the list if the coordinates were swapped
        if swapped:
            points.reverse()
        return points

# h = SpatialHash()
# e = "heyoo"
# e2 = 32
# e3 = "heyoo"

# h.insert_object_for_point((430, 90), e)
# h.insert_object_for_point((330, 70), e2)
# print(h.contents)
# h.remove_object(e3)
# print(h.contents)