from typing import ChainMap
import pygame   #   For visualization
import math
from queue import PriorityQueue  # List and algorithm that returns smallest value
import time
from tkinter import *   # Tkinter for option_menu interface
from tkinter import ttk

# from pygame.font import Font

# Define color codes:
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

# Pygame window setup
WIDTH = 800
HEIGHT = 800
WIN = pygame.display.set_mode((WIDTH, 800))   # Set up Window
pygame.display.set_caption("Path Finding Algorithm") # Window caption


def onsubmit():
    option_menu.quit()
    option_menu.withdraw()

# Tk window:
option_menu = Tk()
option_menu.title("Option menu")
option_menu.geometry('350x300+580+200')
# option_menu.config(bg="#447c84")
# Tk variables:
distance_radio = IntVar()    # Tkinter integer variable to know radiobutton option
algorithm_radio = IntVar()
# Tk objects
lbl_distance = Label(option_menu, text = 'Distance Calculation: ', anchor="w", width = 20)
r_euclidean = Radiobutton(option_menu, text = "Manhattan ", value = 1, var = distance_radio, anchor="w", width = 20)
r_manhattan = Radiobutton(option_menu, text = "Euclidean ", value = 2, var = distance_radio, anchor="w", width = 20)
lbl_algorithm = Label(option_menu, text ='Algorithm: ', anchor="w", width= 20)
r_A_star = Radiobutton(option_menu, text = "A* ", value = 1, var = algorithm_radio, anchor="w", width = 20)
r_A_star_bounded = Radiobutton(option_menu, text = "A* with Bounded relaxation ", value = 2, var = algorithm_radio, anchor="w", width = 20)
r_dijkstra = Radiobutton(option_menu, text = "Dijkstra's ", value = 3, var = algorithm_radio, anchor="w", width = 20)
btn_submit = Button(option_menu, text ='Submit', command=onsubmit, height = 2, width = 10)
# Tk placement  (Use grid instead of pack for placement on parent)
lbl_distance.grid(column = 0, row = 0, pady = 10, padx = 10)
r_euclidean.grid(column = 2, row = 0, pady = 10)
r_manhattan.grid(column = 2, row = 1, pady = 10)
lbl_algorithm.grid(column = 0, row = 2, pady = 10, padx = 10)
r_A_star.grid(column = 2, row = 2, pady = 10)
r_A_star_bounded.grid(column = 2, row = 3, pady = 10)
r_dijkstra.grid(column = 2, row = 4, pady = 10)
btn_submit.grid(columnspan = 3, pady = 20)
# Tk functionality
option_menu.update()
mainloop()

def onclose():
    results.quit()
    results.withdraw()

# Tk window
results = Tk()
results.title("Results")
results.geometry("300x160")
# Tk objects
lbl_distance = Label(results, text = "Distance: ", anchor="w", width = 20)
lbl_distance_a = Label(results, text = " ", anchor="w", width = 20)
lbl_time_taken = Label(results, text = "Time taken: ", anchor="w", width = 20)
lbl_time_taken_a = Label(results, text = " ", anchor="w", width = 20)
btn_close = Button(results, text ='Close', command=onclose, height = 2, width = 10)
# Tk placement
lbl_distance.grid(column = 0, row = 0, pady = 10, padx = 5)
lbl_distance_a.grid(column = 1, row = 0, pady = 10)
lbl_time_taken.grid(column = 0, row = 1, pady = 10, padx = 5)
lbl_time_taken_a.grid(column = 1, row = 1, pady = 10)
btn_close.grid(columnspan = 2, row = 2, pady = 20, padx = 5)


class node: # Class to keep track of nodes (Cubes)
    
    def __init__(self, row, col, width, total_rows):    # Attributes of the class "node"
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE  # Start with all white
        self.neighbors = [] # List for neighbors
        self.width = width
        self.total_rows = total_rows

    # Check status functions:

    def get_pos(self):  # Get position
        return self.row, self.col   # y, x

    def is_closed(self):    # Check if in closed set (Red)
        return self.color == RED

    def is_open(self):  # Check if in the open set (Green)
        return self.color == GREEN

    def is_barrier(self):  # Check if obstacle (Black)
        return self.color == BLACK

    def is_start(self): # If starting node
        return self.color == ORANGE
    
    def is_end(self): # If end node    
        return self.color == TURQUOISE

    def reset(self): # Reset color to status white   
        self.color = WHITE

    # Set status functions:

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN
    
    def make_barrier(self):
        self.color = BLACK
    
    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))   # draw rectangle in pygame 

    def update_neighbors(self, grid):   # Check satus of neighbors to make sure not barriers
        self.neighbors = []
        if self.row < (self.total_rows - 1) and not grid[self.row + 1][self.col].is_barrier(): # Check if not bottom edge and check if row below is not a barrier
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # Check if not top edge and check if row above is not a barrier
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < (self.total_rows - 1) and not grid[self.row][self.col + 1].is_barrier(): # Check if not right edge and check if row to right is not a barrier
            self.neighbors.append(grid[self.row][self.col + 1])        
        
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # Check if not left edge and check if row to left is not a barrier
            self.neighbors.append(grid[self.row][self.col - 1])


    def __lt__(self, other):    # Less than # To compare two nodes
        return False


def makeprevious(grid):
    for row in grid:
        for Node in row:    
            if Node.color == GREEN or Node.color == RED:
                Node.color = GREY


def h(p1, p2):  #Distance measurement. Use manhattan/ absolute distance_radio because easiest to compute
    x1, y1 = p1    # define tuple for position p1 = (1, 9) 
    x2, y2 = p2

    if (distance_radio.get() == 2):   # Euclidean distance           
        return math.sqrt(math.pow((x1 - x2), 2) + math.pow((y1 - y2), 2))     

    # elif (distance_radio.get() == 1):     # Manhattan distance 
    else: 
        return abs(x1 - x2) + abs (y1 - y2)
    
def reconstruct_path(came_from, current, draw):
    counter = 0
    while current in came_from:     # Loop through came_from and make all nodes purple
        current = came_from[current]    # From end node to start node
        current.make_path()
        draw()
        counter += 1
    print("\nPath ength: ", counter)
    lbl_distance_a.config(text = counter)


def A_star(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()  # Create open set   (use the priority que to always get the smallest element (Smallest f_score))
    open_set.put((0, count, start)) # Add start node to open set # 0 is F score of start (Use count for tiebreakers)
    came_from = {}  # Keep track of previous node to keep track of best path

    # Current shortest distance_radio from start node to current node (each node increases the g_score by one)
    g_score = {Node: float("inf") for row in grid for Node in row}  # g_scores initialized as infinity for all nodes
    g_score[start] = 0  # Start node has g_score of 0

    # f_score  = g_score + h    (h is the predicted distance_radio to node from current node to end node)
    f_score = {Node: float("inf") for row in grid for Node in row}  # f_scores initialized as infinity for all nodes    (length = 2500 from ROWS x ROWS)

    # Add start to open set (priority que) and open set hash (keep track of nodes)
    f_score[start] = h(start.get_pos(), end.get_pos())  # Start has no g_score (Just approximation for distance_radio (h_score))
    open_set_hash = {start} # Keep track of which nodes are in priority que (open set)

    while not open_set.empty(): # Go through nodes in open set and if empty then we considered all nodes

        for event in pygame.event.get():
            if event.type == pygame.QUIT:   # Because executing loop inside main while we still need to check if user quit
                pygame.quit()

        current = open_set.get()[2]  # Get node with smallest f_score  # (f_score, count, node)  # In beginnning wil be start node because no other nodes yet
        open_set_hash.remove(current)   # Remove current node from open set hash to syncronize 2 sets

        if current == end:  # Found the end node and can make path
            reconstruct_path(came_from, end, draw)
            end.make_end()  # Turn end node back to turqoise
            start.make_start()  # Tuen start node back to orange
            return True

        for neighbor in current.neighbors: # Loop through all 4 neighbors of current node   # Check which path to neighbor its the fastest 
            temp_g_score = g_score[current] + 1     # neighbors is 1 from current node

            if temp_g_score < g_score[neighbor]:  # If g_score improves then we update path to the neighbor
                came_from[neighbor] = current   # Came from is a list to that node
                g_score[neighbor] = temp_g_score    # Neighbor is 1 position away
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos()) # h distnace is distnace to end 

                if neighbor not in open_set_hash:   # Check if neighbor in open set. If not then add to open set
                    count += 1  
                    open_set.put((f_score[neighbor], count, neighbor))  # Add neighbor node to path (open set) because have a better score
                    open_set_hash.add(neighbor) # Also add to open set hash to keep track of which Nodes is in set
                    neighbor.make_open()    # Node is now in the open set

        draw()

        if current != start:    # If the current node is not the start node then we make it red and not added to open set.
            current.make_closed()   

    return False    # Open set is empty but goal was never reached   


def A_star_bounded(draw, grid, start, end):
    return True


def Dijkstra(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()  # Create open set   (use the priority que to always get the smallest element (Smallest g-score))
    open_set.put((0, count, start)) # Add start node to open set # 0 is g-score of start (Use count for tiebreakers)
    came_from = {}  # Keep track of previous node to keep track of best path

    # Current shortest distance_radio from start node to current node (each node increases the g_score by one)
    g_score = {Node: float("inf") for row in grid for Node in row}  # g_scores initialized as infinity for all nodes
    g_score[start] = 0  # Start node has g-score of 0

    # Add start to open set (priority que) and open set hash (keep track of nodes)
    open_set_hash = {start} # Keep track of which nodes are in priority que (open set)

    while not open_set.empty(): # Go through nodes in open set and if empty then we considered all nodes

        for event in pygame.event.get():
            if event.type == pygame.QUIT:   # Because executing loop inside main while we still need to check if user quit
                pygame.quit()

        current = open_set.get()[2]  # Get node with smallest g-score  # (g_score, count, node)  # In beginnning wil be start node because no other nodes yet
        open_set_hash.remove(current)   # Remove current node from open set hash to syncronize 2 sets

        if current == end:  # Found the end node and can make path
            reconstruct_path(came_from, end, draw)
            end.make_end()  # Turn end node back to turqoise
            start.make_start()  # Tuen start node back to orange
            return True

        for neighbor in current.neighbors: # Loop through all 4 neighbors of current node   # Check which path to neighbor its the fastest 
            temp_g_score = g_score[current] + 1     # neighbors is 1 from current node

            if temp_g_score < g_score[neighbor]:  # If g_score improves then we update path to the neighbor
                came_from[neighbor] = current   # Came from is a list to that node
                g_score[neighbor] = temp_g_score    # Neighbor is 1 position away

                if neighbor not in open_set_hash:   # Check if neighbor in open set. If not then add to open set
                    count += 1  
                    open_set.put((g_score[neighbor], count, neighbor))  # Add neighbor node to path (open set) because have a better score
                    open_set_hash.add(neighbor) # Also add to open set hash to keep track of which Nodes is in set
                    neighbor.make_open()    # Node is now in the open set

        draw()

        if current != start:    # If the current node is not the start node then we make it red and not added to open set.
            current.make_closed()   

    return False    # Open set is empty but goal was never reached   



def make_grid(rows, width):     # Grid of nodes
    grid = []
    gap = width // rows     # integer devision to get integer as answer

    for i in range (rows):  # Rows
        grid.append([])
        for j in range(rows):   # Columns
            Node = node(i, j, gap, rows)
            grid[i].append(Node)    # Add node to grid

    return grid

def draw_grid(win, rows, width):    # Draw grid lines
    gap = width // rows
    
    for i in range(rows):   # Horizontal lines
        pygame.draw.line(win, GREY, (0, i*gap), (width, i*gap))

        for j in range(rows):
            pygame.draw.line(win, GREY, (j*gap, 0), (j*gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)  # At each frame  start with blank white page

    # Draw all the nodes's colors:
    for row in grid:
        for Node in row:
            Node.draw(win)
    
    draw_grid(win, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):   # Mouse position to grid position
    gap = width // rows
    y, x = pos

    row = y // gap  # y divide by cube height
    col = x // gap  # x divide by cube width

    return row, col
    

def main(win, width):
    ROWS = 50       # Can be changed danamically 
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    done = False


    while run:
        draw(win, grid, ROWS, width)    # Draw grid
        # WIN.blit(text, textRect)      # Display text on screen

        for event in pygame.event.get():    # Loop through events that happend and check what they are
            if event.type == pygame.QUIT:   # If press x then stop game
                run = False  

            if pygame.mouse.get_pressed()[0]:   # If leftclick then set 
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)    # Use defined function to get row and col clicked on    
                Node = grid[row][col]

                if not start and Node != end:   # If start not chosen and not end then choose start
                    start = Node
                    start.make_start()

                elif not end and Node != start:   # Else if end is not chosen and not start then make end 
                    end = Node
                    end.make_end()
                
                elif Node != end and Node != start:     # If node not start or end then make barrier
                    Node.make_barrier()

            elif pygame.mouse.get_pressed()[2]:   # If rightclick then reset
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)    # Use defined function to get row and col clicked on    
                Node = grid[row][col]
                Node.reset()

                if Node == start:
                    start = None
                
                elif Node == end:
                    end = None

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE and start and end: # Use space to start algorithm and make sure we have a start and end node

                    for row in grid:    
                       for Node in row:
                           Node.update_neighbors(grid)  # Update Neighbors of nodes in grid

                    start_time = time.time()

                    if (algorithm_radio.get() == 2):
                        done = A_star_bounded(lambda: draw(win, grid, ROWS, width), grid, start, end) 
                    elif (algorithm_radio.get() == 3):
                        done = Dijkstra(lambda: draw(win, grid, ROWS, width), grid, start, end) 
                    else:    # A-star     
                        done = A_star(lambda: draw(win, grid, ROWS, width), grid, start, end)    # Use lamda (Anonymous function to pass the function to use it directly)

                    stop_time = time.time()
                    print("Time taken: ",stop_time - start_time)
                    # lbl_time_taken.text.set(stop_time - start_time) 
                    lbl_time_taken_a.config(text = stop_time - start_time)

                if event.key == pygame.K_c: # Clear if c is pressed
                    start = None    # Reset start node
                    end = None  # Reset the end node
                    grid = make_grid(ROWS, width)   # Reset the grid
                    # Call the options menu:
                    option_menu.deiconify()
                    option_menu.update()
                    mainloop()

                if event.key == pygame.K_r:
                    # Call the options menu:
                    makeprevious(grid)
                    option_menu.deiconify()
                    option_menu.update()
                    mainloop()
        
        if (done == True):
            results.deiconify()
            results.update()
            mainloop()    
            done = False


    pygame.quit()           

main(WIN, WIDTH)
      