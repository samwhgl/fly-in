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
    def __init__(self, name: str, x: Point, y: Point, max_link_capacity: int = 1):
        self.x = x
        self.y = y
        self.max_link_capacity = max_link_capacity
        self.name = name

class Drone:
    def __init__(self, id: int, position: Point):
        self.id = id
        self.position = position

    def move(self, position: Point, direction: Connections):
        self.position = direction.y

    def print_position(self):
        print(f"position is x = {self.position.x}, y = {self.position.y}")

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
    return drones, zones


    #     for line in file:
    #         if "nb_drones:" in line:
    #             nb_drones = int(line.split(':')[1].strip())
    #         elif "start_hub:" in line:
    #             new_line = line.split(' ')
    #             x = int(new_line[2].strip())
    #             y = int(new_line[3].strip())
    #             color = None
    #             # print(len(new_line))
    #             # print(new_line[4])
    #             # print(new_line[4].split('=')[1].strip().strip(']'))
    #             if len(new_line) > 4 and new_line[4].startswith("[color="):
    #                 color = new_line[4].split('=')[1].strip().strip(']')
    # start_hub = NormalPoint(x, y, nb_drones, color, "start_hub")
    # for i in range(nb_drones):
    #     drones.append(Drone(i + 1, start_hub))
    # return drones, start_hub

# def create_end(filename: str, nb_drones: int):
#     with open(filename, "r") as file:
#         for line in file:
#             if "end_hub:" in line:
#                 new_line = line.split(' ')
#                 x = int(new_line[2].strip())
#                 y = int(new_line[3].strip())
#                 name = new_line[1]
#                 color = None
#                 if len(new_line) > 4 and new_line[4].startswith("[color="):
#                     color = new_line[4].split('=')[1].strip().strip(']')
#     end_hub = NormalPoint(x, y, nb_drones, color, name)
#     return end_hub

# def create_hubs(filename: str):
#     hubs = []
#     with open(filename, "r") as file:
#         for line in file:
#             if "hub:" in line:
#                 new_line = line.split(' ')
#                 name = new_line[1]
#                 x = int(new_line[2].strip())
#                 y = int(new_line[3].strip())
#                 color = None
#                 if len(new_line) > 5 and new_line[5].startswith("color="):
#                     color = new_line[4].split('=')[1].strip().strip(']')
#                 zone_type = new_line[4].split('=')[1]
#                 print(zone_type)
#                 if zone_type == "restricted":
#                     hubs.append(RestrictedPoint(x, y, ))



if __name__ == "__main__":
    drones, zones = create_drones_and_zones("input.txt")
    for i in range(len(drones)):
        drones[i].print_id()
        drones[i].print_position()
    for i in range(len(zones)):
        print(zones[i].get_position())
        print(zones[i].get_name())
        print(zones[i].get_zone_type())



