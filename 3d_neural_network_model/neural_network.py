"""
Neural Network

https://blenderscripting.blogspot.com
https://docs.blender.org/api/current/
"""

import math

import bmesh
import bpy

bpyscene = bpy.context.scene

# Neural network node characteristics
NODE_RADIUS = 2
NODE_SEGMENT_RINGS = 100

# Node connection characteristics
CYLINDER_VERTICES = 100

# Create a dictionary to save node coordinates
node_coordinate_dict = {}


def cube(number):
    """
    Returns the cube of a number.
    """
    return number * number * number


def make_nn_nodes(network_layers, nodes_per_layer):
    """
    Creates neural network nodes and saves their coordinates for later connection
    """
    layer_iterations = list(range(network_layers))
    for iteration in layer_iterations:
        node_iterations = list(range(nodes_per_layer[iteration]))

        # Odd number of nodes
        if nodes_per_layer[iteration] % 2 != 0:
            iterations_center_val = math.floor(len(node_iterations) / 2)
            node_locations = [i - iterations_center_val for i in node_iterations]

        elif len(node_iterations) == 2:
            iterations_center_val = sum(node_iterations) / 2
            node_locations = [i - iterations_center_val for i in node_iterations]
        else:
            iterations_center_val = sum(node_iterations) / (len(node_iterations) / 2)
            node_locations = [i - (iterations_center_val / 2) for i in node_iterations]

        for i in node_iterations:
            # Coordinates for node
            coordinate_x = iteration * cube(NODE_RADIUS) * NODE_RADIUS
            coordinate_z = node_locations[0] * cube(NODE_RADIUS)

            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=NODE_SEGMENT_RINGS,
                ring_count=NODE_SEGMENT_RINGS,
                radius=NODE_RADIUS,
                calc_uvs=True,
                enter_editmode=False,
                align="WORLD",
                location=(coordinate_x, 0, coordinate_z),
                rotation=(0, 0, 0),
            )

            node_locations.pop(0)

            node_identifier = f"{str(iteration)}|{str(i)}"
            node_coordinate_dict[node_identifier] = [coordinate_x, 0, coordinate_z]


def cylinder_between(x1, y1, z1, x2, y2, z2, r):
    """
    Makes a cylinder connector between neural network nodes
    """
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    dist = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=CYLINDER_VERTICES,
        radius=r,
        depth=dist,
        location=(dx / 2 + x1, dy / 2 + y1, dz / 2 + z1),
        calc_uvs=False,
        enter_editmode=False,
    )

    phi = math.atan2(dy, dx)
    theta = math.acos(dz / dist)

    bpy.context.object.rotation_euler[1] = theta
    bpy.context.object.rotation_euler[2] = phi


def connect_nn_nodes(network_layers, nodes_per_layer):
    """
    Connects the nodes based on saved coordinates encoded into a dictionary
    """
    for i in list(range(network_layers))[:-1]:
        for index_left in list(range(nodes_per_layer[i])):
            for index_right in list(range(nodes_per_layer[i + 1])):
                cylinder_between(
                    node_coordinate_dict[f"{str(i)}|{str(index_left)}"][0],
                    node_coordinate_dict[f"{str(i)}|{str(index_left)}"][1],
                    node_coordinate_dict[f"{str(i)}|{str(index_left)}"][2],
                    node_coordinate_dict[f"{str(i + 1)}|{str(index_right)}"][0],
                    node_coordinate_dict[f"{str(i + 1)}|{str(index_right)}"][1],
                    node_coordinate_dict[f"{str(i + 1)}|{str(index_right)}"][2],
                    NODE_RADIUS / 4,
                )


def find_z_dims(network_layers):
    """
    Finds all layer lowest z-dimensions for adding the base
    """
    return [node_coordinate_dict[f"{str(i)}|0"][2] for i in list(range(network_layers))]


def create_base(network_layers, z_dims):
    """
    Adds a base based on the coordinates of the central nodes
    """
    # Determine odd or even number of layers to find the center
    if network_layers % 2 != 0:
        central_layer_index = math.floor(network_layers / 2)

        central_layer_bottom_node = node_coordinate_dict[
            f"{str(central_layer_index)}|0"
        ]

        bpy.ops.mesh.primitive_cylinder_add(
            vertices=CYLINDER_VERTICES * CYLINDER_VERTICES,
            radius=network_layers * network_layers,
            depth=NODE_RADIUS / 2,
            location=(
                central_layer_bottom_node[0],
                central_layer_bottom_node[1],
                min(z_dims) - NODE_RADIUS,
            ),
        )

    else:
        central_layers_index_left = round(network_layers / 2 - 1)
        central_layers_index_right = round(network_layers / 2)

        central_layers_bottom_node_left = node_coordinate_dict[
            f"{str(central_layers_index_left)}|0"
        ]

        central_layers_bottom_node_right = node_coordinate_dict[
            f"{str(central_layers_index_right)}|0"
        ]

        bpy.ops.mesh.primitive_cylinder_add(
            vertices=CYLINDER_VERTICES * CYLINDER_VERTICES,
            radius=network_layers * network_layers,
            depth=NODE_RADIUS / 2,
            location=(
                central_layers_bottom_node_left[0]
                + (
                    (
                        central_layers_bottom_node_right[0]
                        - central_layers_bottom_node_left[0]
                    )
                    / 2
                ),
                central_layers_bottom_node_left[1],
                min(z_dims) - NODE_RADIUS,
            ),
        )


# Define the number of nodes of the network and the node count per layer
num_layer_nodes = [3, 6, 6, 4, 2]
num_layers = len(num_layer_nodes)

# Run the functions to create the model
make_nn_nodes(num_layers, num_layer_nodes)

connect_nn_nodes(num_layers, num_layer_nodes)

layer_lower_z_dims = find_z_dims(num_layers)

create_base(num_layers, layer_lower_z_dims)
