def do_lines_intersect(line1_start:tuple, line1_end:tuple, line2_start:tuple, line2_end:tuple):
    """
    This function checks if two line segments defined by their start and end points intersect.

    Args:
        line1_start: Tuple (x, y) for the starting point of line 1.
        line1_end: Tuple (x, y) for the ending point of line 1.
        line2_start: Tuple (x, y) for the starting point of line 2.
        line2_end: Tuple (x, y) for the ending point of line 2.

    Returns:
        True if the lines intersect, False otherwise.
    """

    # Check for special cases
    if (line1_start[0] == line1_end[0] and line2_start[0] == line2_end[0]) and (line1_start[1] != line2_start[1]):
      # Lines are vertical and don't overlap
      return 0
    elif line1_start == line2_start and line1_end == line2_end:
      # Lines completely overlap
      return 1

    # Calculate the orientation for each line segment relative to other line's end point
    def orientation(p, q, r):
      val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
      return 0 if val == 0 else (1 if val > 0 else -1)

    # Check for opposing orientations of each line segment
    o1 = orientation(line1_start, line1_end, line2_start)
    o2 = orientation(line1_start, line1_end, line2_end)
    o3 = orientation(line2_start, line2_end, line1_start)
    o4 = orientation(line2_start, line2_end, line1_end)

    # If both orientations are different for each line, then lines intersect
    if o1 != o2 and o3 != o4:
      return 1

    # Check if the intersection falls on the segments
    # (needs modification if intersection point calculation is desired)
    return 0


  
def distance(pos, wall):
    if wall.x1 == wall.x2 :
        if pos[1] > wall.y2:
            return ((pos[0] - wall.x2)**2 + (pos[1] - wall.y2)**2)
        if pos[1] < wall.y1:
            return ((pos[0] - wall.x1)**2 + (pos[1] - wall.y1)**2)
        return abs(wall.x1 - pos[0])
    else:
        if pos[1] > wall.x2:
            return ((pos[0] - wall.x2)**2 + (pos[1] - wall.y2)**2)
        if pos[1] < wall.x1:
            return ((pos[0] - wall.x1)**2 + (pos[1] - wall.y1)**2)
        return abs(wall.y1 - pos[1])