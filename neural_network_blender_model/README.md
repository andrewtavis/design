<div align="center">
  <a href="https://github.com/andrewtavis/design/tree/main/neural_network_blender_model"><img src="https://github.com/andrewtavis/design/blob/main/resources/gh_images/neural_net_logo.png" width="638" height="200"></a>
</div>

--------------------------------------

### Making a 3D model of a nueral network using Python and Blender

**Jump to:** [Process](#process) • [Result](#result)

# Explanation
This directory takes you through the steps to make a 3D model of a [neural network](https://en.wikipedia.org/wiki/Neural_network) using Python and [Blender](https://www.blender.org/). The final result includes a base that it can stand on after being 3D printed.

# Process

### Imports and basics

```python
import bpy
import bmesh
import math

bpyscene = bpy.context.scene

# Neural network node charactaristics
node_radius = 2
node_segments_rings = 100

# Node connection charactaristics
cylander_vertices = 100

# Create a dictionary to save node coordinates
node_coordinate_dict = {}


def cube(number):
    return number * number * number
```

### Make the Nodes

```python
def make_nn_nodes(network_layers, nodes_per_layer):
    """
    Creates neural network nodes and saves their coordinates for later connection
    """
    layer_iterations = list(range(network_layers))
    for iteration in layer_iterations:
        node_iterations = list(range(nodes_per_layer[iteration]))

        # Odd number of nodes
        if nodes_per_layer[iteration] % 2 != 0:
            iterations_center_val = math.floor(len(node_iterations)/2)
            node_locations = [i-iterations_center_val for i in node_iterations]

            for i in node_iterations:
                # Coordinates for node
                coordinate_x = iteration*cube(node_radius)*node_radius
                coordinate_z = node_locations[0]*cube(node_radius)

                bpy.ops.mesh.primitive_uv_sphere_add(segments=node_segments_rings,
                    ring_count=node_segments_rings, radius=node_radius, calc_uvs=True,
                    enter_editmode=False, align='WORLD',
                    location=(coordinate_x, 0, coordinate_z),
                    rotation=(0, 0, 0))

                node_locations.pop(0)

                node_identifier = '{}|{}'.format(str(iteration), str(i))
                node_coordinate_dict[node_identifier] = [coordinate_x, 0, coordinate_z]

        # Even number of nodes
        else:
            # Two nodes
            if len(node_iterations) == 2:
                iterations_center_val = sum(node_iterations)/2
                node_locations = [i-iterations_center_val for i in node_iterations]
            # More than two
            else:
                iterations_center_val = sum(node_iterations)/(len(node_iterations)/2)
                node_locations = [i-(iterations_center_val/2) for i in node_iterations]

            for i in node_iterations:
                # Coordinates for node
                coordinate_x = iteration*cube(node_radius)*node_radius
                coordinate_z = node_locations[0]*cube(node_radius)

                bpy.ops.mesh.primitive_uv_sphere_add(segments=node_segments_rings,
                    ring_count=node_segments_rings, radius=node_radius, calc_uvs=True,
                    enter_editmode=False, align='WORLD',
                    location=(coordinate_x, 0, coordinate_z),
                    rotation=(0, 0, 0))

                node_locations.pop(0)

                node_identifier = '{}|{}'.format(str(iteration), str(i))
                node_coordinate_dict[node_identifier] = [coordinate_x, 0, coordinate_z]
```

### Connect Node Layers

```python
def cylinder_between(x1, y1, z1, x2, y2, z2, r):
  """
  Makes a cylander connector between neural network nodes
  """
  dx = x2 - x1
  dy = y2 - y1
  dz = z2 - z1
  dist = math.sqrt(dx**2 + dy**2 + dz**2)

  bpy.ops.mesh.primitive_cylinder_add(
      vertices = cylander_vertices,
      radius = r,
      depth = dist,
      location = (dx/2 + x1, dy/2 + y1, dz/2 + z1),
      calc_uvs=False,
      enter_editmode=False

  )

  phi = math.atan2(dy, dx)
  theta = math.acos(dz/dist)

  bpy.context.object.rotation_euler[1] = theta
  bpy.context.object.rotation_euler[2] = phi


def connect_nn_nodes(network_layers, nodes_per_layer):
    """
    Connects the nodes based on saved coordinates encoded into a dictionary
    """
    for i in list(range(network_layers))[:-1]:
        for index_left in list(range(nodes_per_layer[i])):
            for index_right in list(range(nodes_per_layer[i+1])):
                cylinder_between(node_coordinate_dict['{}|{}'.format(str(i), str(index_left))][0],
                                 node_coordinate_dict['{}|{}'.format(str(i), str(index_left))][1],
                                 node_coordinate_dict['{}|{}'.format(str(i), str(index_left))][2],
                                 node_coordinate_dict['{}|{}'.format(str(i+1), str(index_right))][0],
                                 node_coordinate_dict['{}|{}'.format(str(i+1), str(index_right))][1],
                                 node_coordinate_dict['{}|{}'.format(str(i+1), str(index_right))][2],
                                 node_radius/4)
```

### Make a Base (optional - for 3D printing)
```python
def find_z_dims(network_layers):
    """
    Finds all layer lowest z-dimensions for adding the base
    """
    z_dims = []
    for i in list(range(network_layers)):
        z_dims.append(node_coordinate_dict['{}|{}'.format(str(i),str(0))][2])

    return z_dims


def create_base(network_layers, z_dims):
    """
    Adds a base based on the coordinates of the central nodes
    """
    # Determine odd or even number of layers to find the center
    if network_layers % 2 != 0:
        central_layer_index = math.floor(network_layers/2)

        central_layer_bottom_node = node_coordinate_dict['{}|{}'.format(str(central_layer_index),str(0))]

        bpy.ops.mesh.primitive_cylinder_add(vertices = cylander_vertices*cylander_vertices,
                                            radius = network_layers*network_layers,
                                            depth = node_radius/2,
                                            location = (central_layer_bottom_node[0],
                                                        central_layer_bottom_node[1],
                                                        min(z_dims) - node_radius)
                                            )

    else:
        central_layers_index_left = round(network_layers/2-1)
        central_layers_index_right = round(network_layers/2)

        central_layers_bottom_node_left = node_coordinate_dict['{}|{}'.format(str(central_layers_index_left),str(0))]
        central_layers_bottom_node_right = node_coordinate_dict['{}|{}'.format(str(central_layers_index_right),str(0))]

        bpy.ops.mesh.primitive_cylinder_add(vertices = cylander_vertices*cylander_vertices,
                                            radius = network_layers*network_layers,
                                            depth = node_radius/2,
                                            location = (central_layers_bottom_node_left[0] + ((central_layers_bottom_node_right[0] - central_layers_bottom_node_left[0])/2),
                                                        central_layers_bottom_node_left[1],
                                                        min(z_dims) - node_radius)
                                            )
```

### Putting it All Together

The model is made by running all the previous functions with defined inputs. The inputs here make a very basic network that resembles the [Millennium Falcon](https://en.wikipedia.org/wiki/Millennium_Falcon) (not intentional, but awesome).

```python
# Define the number of nodes of the network and the node count per layer
num_layers = 5
num_layer_nodes = [3,6,6,4,2]

# Run the functions to create the model
make_nn_nodes(num_layers, num_layer_nodes)

connect_nn_nodes(num_layers, num_layer_nodes)

layer_lower_z_dims = find_z_dims(num_layers)

create_base(num_layers, layer_lower_z_dims)
```

# Result

A zip of the final .blend file can be found [here](https://github.com/andrewtavis/design/blob/main/neural_network_blender_model/neural_network.blend.zip), a .py file for the codes is [here](https://github.com/andrewtavis/design/blob/main/neural_network_blender_model/neural_network.py), and the .stl file below is [here](https://github.com/andrewtavis/design/blob/main/neural_network_blender_model/neural_network.stl).

![](https://raw.githubusercontent.com/andrewtavis/design/main/resources/gh_images/neural_network_stl.gif)
