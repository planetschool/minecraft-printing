import mcpi.minecraft as minecraft
mc = minecraft.Minecraft.create()
from time import sleep
from datetime import datetime
import os

GRID_MATERIAL = 41 #41 is gold, the mincraft material that has the highest electrical conductivity
COPY_MATERIAL = 35
PRINTING_BED_SIZE = 200 #The unit is millimeters and the bed is assumed to be square.
GOOGLE_DRIVE_FOLDER = "Minecraft-Printing-Files" #This cannot have any spaces in it
RCLONE_PATH = "minecraft-printing"

#grid_search coordinates everything

def grid_search():
	finding_grid = True
	os.system("echo Hello from the other side")
	while finding_grid:

		blockHits = mc.events.pollBlockHits()

		if blockHits:
			cube_corner1 = corner_loc_from_blockhits(blockHits)
			print "Cube_corner1 is %s" % cube_corner1
			grid_size = grid_height(cube_corner1)
			corner_pair = verify_cube(cube_corner1, grid_size)
			min_corner = corner_pair[0]
			max_corner = corner_pair[1]
#I just extracted two values (min_corner and max_corner) from verify_cube() using a list but is there a better way?	    
			
			print_copy(min_corner, max_corner, grid_size)
			print_or_edit()
			coordinate_export(min_corner, max_corner, grid_size)
			return

def grid_error():
	mc.postToChat("Looks like your transporter isn't a square or is incomplete. Check all the edges and then re-activate your transporter with your sword.")
	grid_search()				    	    

def grid_height(corner_loc):
#Establishes the height of the grid, which we will test to ensure the grid is a cube.
	x = corner_loc[0]
	y = corner_loc[1]
	z = corner_loc[2]
	grid_size = mc.getHeight(x,z)
	grid_height = mc.getHeight(x,z)
	height = True
	while height:
		if mc.getBlock(x,grid_height,z) == 0 or mc.getBlock(x,grid_height,z) == GRID_MATERIAL:
			grid_height -= 1
		else:
			grid_height += 1
			height = False
	grid_size = grid_size - grid_height - 1
	grid_height = grid_size + 1
	#print "Final grid size is", grid_size
	#print "Final grid height is", grid_height
	return grid_size

def corner_loc_from_blockhits(blockHits):
#Activates the search for the print grid
	for blockHit in blockHits:
		x = blockHit.pos.x
		y = blockHit.pos.y
		z = blockHit.pos.z
		if mc.getBlock(x,y,z) == GRID_MATERIAL:

#Hitting a corner
			if (mc.getBlock(x + 1,y,z) == GRID_MATERIAL or mc.getBlock(x-1,y,z) == GRID_MATERIAL) and (mc.getBlock(x,y+1,z) == GRID_MATERIAL or mc.getBlock(x,y-1,z) == GRID_MATERIAL) and (mc.getBlock(x,y,z+1) == GRID_MATERIAL or mc.getBlock(x,y,z-1) == GRID_MATERIAL):
				print "you hit a corner at", x,y,z

#Hitting a x beam
			elif mc.getBlock(x + 1,y,z) == GRID_MATERIAL:
				print "you hit a x beam at", x,y,z
				x_beam = True
				while x_beam:
					if mc.getBlock(x,y,z) == GRID_MATERIAL:
						x += 1
					else:
						x = x - 1
						x_beam = False

#Hitting a y beam
			elif mc.getBlock(x,y+1,z) == GRID_MATERIAL:
				print "you hit a y beam at", x,y,z
				y_beam = True
				while y_beam:
					if mc.getBlock(x,y,z) == GRID_MATERIAL:
						y += 1
					else:
						y = y - 1
						y_beam = False

#Hitting a z beam
			elif mc.getBlock(x,y,z+1) == GRID_MATERIAL:
				print "you hit a z beam at", x,y,z
				z_beam = True
				while z_beam:
					if mc.getBlock(x,y,z) == GRID_MATERIAL:
						z += 1
					else:
						z = z - 1
						z_beam = False
			corner_loc = [x,y,z]
			mc.postToChat("Got it. Checking your transporter.")
			return corner_loc

def verify_cube_edge(corner_loc, grid_size, axis):
#Verifies the length of a specified axis ("x", "y", "z") and returns the opposite corner along that axis
	if axis == "x":
		axis = 0
	elif axis == "y":
		axis = 1
	else: axis = 2

	end_corner = corner_loc[:]
	end_corner[axis] += 1
	if mc.getBlock(end_corner) == GRID_MATERIAL:
		#print "You hit a bottom beam."
		scan = True
		while scan:
			if mc.getBlock(end_corner) == GRID_MATERIAL:
				end_corner[axis] += 1
			else:
				end_corner[axis] -= 1
				scan = False
		if abs(end_corner[axis] - corner_loc[axis]) != grid_size:
			grid_error()
		else:
			return end_corner

	else:
		end_corner[axis] -= 1
		#print "You hit a top beam."
		scan = True
		while scan:
			if mc.getBlock(end_corner) == GRID_MATERIAL:
				end_corner[axis] -= 1
			else:
				end_corner[axis] += 1
				scan = False
				
		if abs(end_corner[axis] - corner_loc[axis]) != grid_size:
			grid_error()
		else:
			return end_corner

def verify_cube(corner_loc, grid_size):
#verify all 12 edges of the cube for uniform length, if uniform, returns the min and max corners
	cube_corner1 = verify_cube_edge(corner_loc, grid_size, "y")
	cube_corner2 = verify_cube_edge(corner_loc, grid_size, "x")
	cube_corner3 = verify_cube_edge(cube_corner2, grid_size, "y")
	opposite_corner0 = verify_cube_edge(cube_corner3, grid_size, "z")
	opposite_corner1 = verify_cube_edge(opposite_corner0, grid_size, "y")
	opposite_corner2 = verify_cube_edge(opposite_corner0, grid_size, "x")
	opposite_corner3 = verify_cube_edge(opposite_corner2, grid_size, "y")
	cube_corner0 = verify_cube_edge(opposite_corner3, grid_size, "z")
#It feels like there should be a cleaner way to feed the return back into the function without creating all these variables.
	
	if cube_corner0 == corner_loc:
		min_corner = [min(cube_corner0[0], opposite_corner0[0]), min(cube_corner0[1], opposite_corner0[1]), min(cube_corner0[2], opposite_corner0[2])]
		max_corner = [max(cube_corner0[0], opposite_corner0[0]), max(cube_corner0[1], opposite_corner0[1]), max(cube_corner0[2], opposite_corner0[2])]
		corner_pair = [min_corner, max_corner]
		return corner_pair
	else:
		grid_error()

def print_copy(min_corner, max_corner, grid_height):
#prints a duplicate of the object inside the cube for the user to verify and initiate coordinate export
	mc.postToChat("Transporter verified. Pritning a virtual copy. Look next to your transporter to watch it print!")
	safe_distance = grid_height + 5

	min_x = min_corner[0]
	min_y = min_corner[1]
	min_z = min_corner[2]

	max_x = max_corner[0]
	max_y = max_corner[1]
	max_z = max_corner[2]

	mc.setBlocks(max_x, max_y, max_z+(safe_distance*2), min_x, min_y, min_z+safe_distance, 0)

	for y_location in range(min_y, max_y+1):
		for x_location in range(min_x+1, max_x):
			for z_location in range(min_z+1, max_z):
				if mc.getBlock(x_location, y_location, z_location) != 0:
					z_location += safe_distance
					mc.setBlock(x_location, y_location, z_location, COPY_MATERIAL)
	return
	
def print_or_edit():
#Activates the search for the print grid
	mc.postToChat("If the copy of your object looks good, hit the copy with your sword to commence printing. Otherwise, hit your transporter to stop the copying process and make edits.")
	finding_grid = True
	while finding_grid:
		blockHits = mc.events.pollBlockHits()
		if blockHits:
			for blockHit in blockHits:
				x = blockHit.pos.x
				y = blockHit.pos.y
				z = blockHit.pos.z
				if mc.getBlock(x,y,z) == GRID_MATERIAL:
					mc.postToChat("OK, you want to make some edits before you print. When you are ready, hit the transporter again to activate it.")
					grid_search()
				elif mc.getBlock(x,y,z) == COPY_MATERIAL:
					mc.postToChat("Sending your object to the printer. Stand by.")
					return

def coordinate_export(min_corner, max_corner, grid_height):
#Scanning the original object (again) and exporting the coordinates in OpenSCAD format.
#Bear in mind that in OpenSCAD the vertical axis is Z whereas in Minecraft vertical is Y. Since we are translating to OpenSCAD, we will change the variables accordingly.

	min_x = min_corner[0]+1
	min_z = min_corner[1]
	min_y = min_corner[2]+1
	
	max_x = max_corner[0]-1
	max_z = max_corner[1]
	max_y = max_corner[2]-1
	
	x_zero = 0 - min_x
	y_zero = 0 - min_y
	z_zero = 0 - min_z
	
	printable_area = grid_height - 2
	block = 1.05
	OpenSCAD_coordinates = []
	date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
	export_filename = "minecraft_object_transported_at_"+ date +".scad"
	file_path = "/home/pi/Desktop/Minecraft-Printing-Files/" + export_filename
	print export_filename
	
	file = open(file_path, "w")
	for y_location in range(min_y, max_y+1):
		for x_location in range(min_x, max_x+1):
			for z_location in range(min_z, max_z+1):
				if mc.getBlock(x_location, z_location, y_location) != 0:
					list_object = "translate([%s, %s, %s]) cube(%s);\n" % (x_location - min_x, y_location - min_y, z_location - min_z, block)
					file.write(list_object)
					
	print "File export complete."
	mc.postToChat("Object export complete. You can now hit a new transport cube to print a new object.")
	file.close()
	export_file(file_path)
	grid_search()


def convert_to_stl():
	pass
#project for next time!

def export_file(file_path):
    #runs a script to export the printing file to Google Drive using rdrive.
    #rdrive must already be installed or this function will error.
  #  try:
        print "rclone copy " + file_path + " "+ RCLONE_PATH + ":" + GOOGLE_DRIVE_FOLDER
        os.system("rclone copy " + file_path + " "+ RCLONE_PATH + ":" + GOOGLE_DRIVE_FOLDER) #GOOGLE_DRIVE_FOLDER
        print "Exported to Google Drive!"
   # except:
 #       print "Something went wrong"
  #      pass

grid_search()
print "Success!"
