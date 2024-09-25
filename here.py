import pygame
import requests
import math
import io
from requests_oauthlib import OAuth1
from mysecrets import HERE_ACCESS_ID, HERE_API_KEY

# Initialize Pygame
pygame.init()

# Set window size (in pixels)
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Map Tile Viewer")

# API credentials
key_id = HERE_ACCESS_ID
key_secret = HERE_API_KEY

# Obtain OAuth token
oauth = OAuth1(client_key=key_id, client_secret=key_secret, signature_type='auth_header')
r = requests.post('https://account.api.here.com/oauth2/token', 
                  data={'grant_type': 'client_credentials'}, 
                  auth=oauth, 
                  headers={'Content-Type': 'application/x-www-form-urlencoded'})

access_token = r.json()['access_token']

# Set up session with Authorization header
s = requests.Session()
s.headers = {'Authorization': f"Bearer {access_token}"}

# Function to calculate tile coordinates from latitude, longitude, and zoom level
def latlon_to_tilexy(lat, lon, zoom):
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)

# Function to fetch a tile from the HERE API
def fetch_tile(x, y, zoom, size):
    tile_url = f"https://1.aerial.maps.ls.hereapi.com/maptile/2.1/maptile/newest/satellite.day/{zoom}/{x}/{y}/{size}/png8?apiKey={key_secret}"
    response = s.get(tile_url)
    if response.status_code == 200:
        # Use io.BytesIO to convert the response content into an in-memory byte stream
        return pygame.image.load(io.BytesIO(response.content))  # Load image from byte stream
    else:
        print(f"Error fetching tile {x},{y}: {response.status_code}")
        return None

# Tile and map settings
tile_size = 256
zoom = 12
latitude, longitude = 50.72563, -3.52972  # Starting position (Devon, UK)
x_tile, y_tile = latlon_to_tilexy(latitude, longitude, zoom)

# Fetch tiles for initial zoom level
tiles = {}

def load_tiles(center_x, center_y, zoom):
    tiles.clear()
    for x in range(-2, 3):  # Load a 5x5 grid of tiles around the center
        for y in range(-2, 3):
            tile_image = fetch_tile(center_x + x, center_y + y, zoom, tile_size)
            if tile_image:
                tiles[(x, y)] = tile_image

# Initial tile loading
load_tiles(x_tile, y_tile, zoom)

# Set initial map position and zoom state
map_x, map_y = 0, 0

# Pygame loop
running = True
clock = pygame.time.Clock()
speed = 10  # How fast to move the map
zoom_speed = 1  # How much zoom changes per scroll event

# Mouse-based zooming
def zoom_at_point(zoom_in, mouse_pos):
    global zoom, x_tile, y_tile, tile_size
    prev_zoom = zoom
    if zoom_in:
        zoom += 1
    else:
        zoom -= 1

    zoom = max(0, min(20, zoom))  # Zoom range between 0 (world) and 20 (most detailed)
    
    # Recalculate tile position based on the new zoom
    center_tile_x, center_tile_y = latlon_to_tilexy(latitude, longitude, zoom)

    # Refetch tiles at the new zoom level
    load_tiles(center_tile_x, center_tile_y, zoom)

while running:
    screen.fill((0, 0, 0))

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Mouse wheel up
                zoom_at_point(zoom_in=True, mouse_pos=event.pos)
            if event.button == 5:  # Mouse wheel down
                zoom_at_point(zoom_in=False, mouse_pos=event.pos)

    # Handle arrow keys for map movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        map_x += speed
    if keys[pygame.K_RIGHT]:
        map_x -= speed
    if keys[pygame.K_UP]:
        map_y += speed
    if keys[pygame.K_DOWN]:
        map_y -= speed

    # Display tiles
    for (tile_x, tile_y), tile_image in tiles.items():
        screen.blit(tile_image, (tile_x * tile_size + map_x, tile_y * tile_size + map_y))

    # Refresh display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

pygame.quit()
