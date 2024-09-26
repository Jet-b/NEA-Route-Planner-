import math
import requests
from mysecrets import TOMTOM_API_KEY
import pygame
import io


def lat_lon_to_tile(lat, lon, zoom):
    lat_rad = math.radians(lat)
    n = 2 ** zoom
    x_tile = int((lon + 180.0) / 360.0 * n)
    y_tile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return x_tile, y_tile


def fetch_tile(lat, lon, zoom, size):
    x, y = lat_lon_to_tile(lat, lon, zoom)
    tile_url = f"https://api.tomtom.com/map/1/tile/sat/main/{zoom}/{x}/{y}.jpg?key={API_KEY}"
    response = requests.get(tile_url)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Error fetching tile {x},{y}: {response.status_code}")
        return None

if __name__ == "__main__":
    API_KEY = TOMTOM_API_KEY
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    running = True
    zoom = 12
    image_pos = (0, 0)
    speed = 10
    tile = fetch_tile(50.72563, -3.52972, zoom, 256)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    zoom += 1
                    tile = fetch_tile(50.72563, -3.52972, zoom, 256)
                if event.key == pygame.K_DOWN:
                    zoom -= 1
                    tile = fetch_tile(50.72563, -3.52972, zoom, 256)
                if event.key == pygame.K_w:
                    image_pos = (image_pos[0], image_pos[1] - speed)
                if event.key == pygame.K_s:
                    image_pos = (image_pos[0], image_pos[1] + speed)
                if event.key == pygame.K_a:
                    image_pos = (image_pos[0] - speed, image_pos[1])
                if event.key == pygame.K_d:
                    image_pos = (image_pos[0] + speed, image_pos[1])
        
        
        screen.fill((0, 0, 0))
        if tile:
            image = pygame.image.load(io.BytesIO(tile))
            screen.blit(image, image_pos)
            pygame.display.flip()