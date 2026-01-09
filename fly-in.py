from abc import ABC, abstractmethod
import re

class Point(ABC):
    def __init__(self, name: str, x: int, y: int, max_drone: int = 1, color: str = None, zone_type: str = "hub"):
        self.x = x
        self.y = y
        self.max_drone = max_drone
        self.color = color
        self.zone_type = zone_type
        self.name = name

    @abstractmethod
    def cost(self):
        pass

    @abstractmethod
    def priority(self):
        pass

    def get_position(self):
        return self.x, self.y

    def get_max_drones(self):
        return self.max_drone

    def get_color(self):
        return self.color

    def get_name(self):
        return self.name

    def get_zone_type(self):
        return self.zone_type

    def get_number_of_drones(self, drones: list):
        result = 0
        for i in range(len(drones)):
            if drones[i].get_position() == self.get_position():
                result += 1
        return result

class NormalPoint(Point):
    def __init__(self, name, x, y, max_drone, color = None, zone_type = "hub"):
        super().__init__(name, x, y, max_drone, color, zone_type)

    def cost(self):
        return 1

    def priority(self):
        return False

class BlockedPoint(Point):
    def __init__(self, name, x, y, max_drone, color = None, zone_type = "hub"):
        super().__init__(name, x, y, max_drone, color, zone_type)

    def cost(self):
        return False

    def priority(self):
        return False

class RestrictedPoint(Point):
    def __init__(self, name, x, y, max_drone, color = None, zone_type = "hub"):
        super().__init__(name, x, y, max_drone, color, zone_type)

    def cost(self):
        return 2

    def priority(self):
        return False

class PriorityPoint(Point):
    def __init__(self, name, x, y, max_drone, color = None, zone_type = "hub"):
        super().__init__(name, x, y, max_drone, color, zone_type)

    def cost(self):
        return 1

    def priority(self):
        return True

class Connections:
    def __init__(self, x: Point, y: Point, max_link_capacity: int = 1):
        self.x = x
        self.y = y
        self.max_link_capacity = max_link_capacity

    def get_points(self):
        return self.x.get_position(), self.y.get_position()

    def get_max_capacity(self):
        return self.max_link_capacity

    def get_destination(self, start: Point):
        if self.x.get_position() == start.get_position():
            return self.y
        else:
            return self.x

    def get_cost(self, start : Point):
        if self.x.get_position() == start.get_position():
            return self.y.cost()
        else:
            return self.x.cost()


class Drone:
    def __init__(self, id: int, position: Point):
        self.id = id
        self.position = position

    def move(self, direction: Connections):
        if direction.get_points()[0] == self.get_position():
            self.position = direction.y
            cost = direction.y.cost()
        else:
            self.position = direction.x
            cost = direction.x.cost()
        return cost


    def print_position(self):
        print(f"position is x = {self.position.x}, y = {self.position.y}")

    def get_position(self):
        return self.position.get_position()

    def print_id(self):
        print(f" drone id is {self.id}")

def create_drones_and_zones(filename: str):
    nb_drones = None
    drones = []
    zones = []
    pattern = r"hub:\s+(?P<name>\w+)\s+(?P<x>\d+)\s+(?P<y>\d+).+?\[(?=[^\]]*?color=(?P<color>\w+))?(?=[^\]]*?zone=(?P<zone>\w+))?(?=[^\]]*?max_drones=(?P<max>\d+))?.*\]"
    pattern2 = r"(?P<type>start|end)_hub:\s+(?P<name>\w+)\s+(?P<x>\d+)\s+(?P<y>\d+).+?\[(?=[^\]]*?color=(?P<color>\w+))?(?=[^\]]*?zone=(?P<zone>\w+))?.*\]"
    with open(filename, "r") as file:
        content = file.read()
        match = re.search(r'nb_drones:\s*(\d+)', content)
        nb_drones = int(match.group(1))
        content2 = content.splitlines()
        for line in content2:
            match = re.search(pattern, line)
            if match:
                name = match.group('name')
                x = match.group('x')
                y = match.group('y')
                color = match.group('color')
                zone_type = match.group('zone')
                max_drones = match.group('max')
                if zone_type == "priority":
                    zones.append(PriorityPoint(name, x, y, max_drones, color))
                elif zone_type == "blocked":
                    zones.append(BlockedPoint(name, x, y, max_drones, color))
                elif zone_type == "restricted":
                    zones.append(RestrictedPoint(name, x, y, max_drones, color))
                else:
                    zones.append(NormalPoint(name, x, y, max_drones, color))
        for line in content2:
            match = re.search(pattern2, line)
            if match:
                name = match.group('name')
                zone_type = match.group('type')
                x = match.group('x')
                y = match.group('y')
                color = match.group('color')
                max_drones = nb_drones
                if zone_type == "start":
                    zones.append(NormalPoint(name, x, y, max_drones, color, "start_hub"))
                else:
                    zones.append(NormalPoint(name, x, y, max_drones, color, "end_hub"))
    for i in range(nb_drones):
        drones.append(Drone(i + 1, zones[-2]))
    del zones[:2]
    return drones, zones

def create_connections(zones: list, input_file: str):
    connections = []
    with open(input_file, "r") as file:
        content = file.read()
        content = content.splitlines()
        for line in content:
            if line.startswith("connection:"):
                new_line = line.split(' ')
                zone_line = new_line[1].split('-')
                start = zone_line[0]
                end = zone_line[1]
                max_capacity = 1
                if len(new_line) > 2:
                    max_capacity = int(new_line[2].split('=')[1].strip(']'))
                chosen_zones = []
                for point in zones:
                    if point.get_name() == start or point.get_name() == end:
                        chosen_zones.append(point)
                connections.append(Connections(chosen_zones[0], chosen_zones[1], max_capacity))

    return connections

def find_zone_with_position(zones: list, position: tuple):
    result = 0
    for zone in zones:
        if zone.get_position() == position:
            return result
        else:
            result += 1

def find_paths(zones: list, drones: list, connections: list):
    cost = 0
    finished = False
    path = {}
    paths = {}
    start = zones[-2]
    end = zones[-1]
    current = start
    id = 0
    while finished == False:
        for connection in connections:
            if current.get_position() in connection.get_points():
                path[id] = [connection.get_destination(current).get_position(), connection.get_cost(current)]
                id += 1
            for index in path:
                if path[index][0] == end.get_position():
                    finished = True
                else:
                    current = zones[find_zone_with_position(zones, path[index][0])]
        finished = True
    print(path)






if __name__ == "__main__":
    drones, zones = create_drones_and_zones("input.txt")
    # for i in range(len(drones)):
    #     drones[i].print_id()
    #     drones[i].print_position()
    # for i in range(len(zones)):
    #     print(zones[i].get_position())
    #     print(zones[i].get_name())
    #     print(zones[i].get_zone_type())
    connections = create_connections(zones, "input.txt")
    # for i in range(len(connections)):
    #     print(connections[i].get_points())
    #     print(connections[i].get_max_capacity())
    # print(zones[-2].get_number_of_drones(drones))
    # print(drones[0].move(connections[0]))
    # print(drones[0].move(connections[2]))
    # print(drones[0].move(connections[3]))
    # drones[0].print_position()
    # print(zones[-2].get_number_of_drones(drones))
    find_paths(zones, drones, connections)







