import pygame
import os
import base64
import zlib
import xml.etree.ElementTree as ET
import pytmx  # Thư viện để xử lý tmx files

class BattleBase:
    def __init__(self, screen, level_name):
        self.screen = screen
        self.running = True
        self.level_name = level_name

        self.tile_size = 16
        self.tile_layers = []
        self.tile_layers_visibility = []
        self.tile_layers_names = []
        self.object_layers = []
        self.ground_objects = []
        self.wall_objects = []
        self.spawn_objects = []
        self.margin_data = []  # Thêm thuộc tính để lưu dữ liệu lớp margin

        self.load_level(level_name)
        self.load_tiles()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(os.path.dirname(current_dir))

        

    def load_level(self, level_name):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        path = os.path.join(project_root, "levels", f"{level_name}.tmx")

        tree = ET.parse(path)
        root = tree.getroot()

        self.tile_width = int(root.get('tilewidth'))
        self.tile_height = int(root.get('tileheight'))
        self.map_width = int(root.get('width'))
        self.map_height = int(root.get('height'))

        self.tilesets_info = []
        for ts in root.findall("tileset"):
            self.tilesets_info.append({
                'firstgid': int(ts.get("firstgid")),
                'source': ts.get("source")
            })

        self.tile_layers.clear()
        self.tile_layers_visibility.clear()
        self.tile_layers_names.clear()
        self.object_layers.clear()
        self.margin_data.clear()  # Xóa dữ liệu margin cũ
        for layer in root.findall("layer"):
            visible = layer.get("visible") != "0"
            data = layer.find("data")
            encoding = data.get("encoding")
            compression = data.get("compression")
            layer_name = layer.get("name")  # Lấy tên lớp

            if encoding == "base64" and compression == "zlib":
                raw_data = base64.b64decode(data.text.strip())
                decompressed = zlib.decompress(raw_data)
                tile_count = self.map_width * self.map_height
                tile_ids = [int.from_bytes(decompressed[i:i+4], byteorder='little') for i in range(0, tile_count * 4, 4)]
                if layer_name == "margin":
                    self.margin_data = tile_ids  # Lưu dữ liệu margin
                else:
                    self.tile_layers.append(tile_ids)
                    self.tile_layers_visibility.append(visible)
                    self.tile_layers_names.append(layer_name)
            elif encoding == "csv":
                raw_data = data.text.strip().replace('\n', '')
                tile_ids = [int(val) for val in raw_data.split(',') if val.strip().isdigit()]
                if layer_name == "margin":
                    self.margin_data = tile_ids  # Lưu dữ liệu margin
                else:
                    self.tile_layers.append(tile_ids)
                    self.tile_layers_visibility.append(visible)
                    self.tile_layers_names.append(layer_name)
            else:
                print(f"[ERROR] Unsupported encoding/compression: {encoding} / {compression}")

        for obj_group in root.findall("objectgroup"):
            objects = []
            for obj in obj_group.findall("object"):
                obj_data = {
                    "name": obj.get("name"),
                    "type": obj.get("type"),
                    "x": float(obj.get("x")),
                    "y": float(obj.get("y")),
                    "width": float(obj.get("width", 0)),
                    "height": float(obj.get("height", 0)),
                    "properties": {p.get("name"): p.get("value") for p in obj.findall("properties/property")}
                }
                objects.append(obj_data)

                # Phân loại object
                if obj_data["name"] == "gnd":
                    self.ground_objects.append(obj_data)
                elif obj_data["name"] == "wall":
                    self.wall_objects.append(obj_data)
                if (
                    obj_data["properties"].get("player") == "yes"
                    or obj_data["properties"].get("enemy") == "yes"
                    or obj_data["properties"].get("win") == "yes"
                ):
                    self.spawn_objects.append(obj_data)

            self.object_layers.append(objects)

    def load_tiles(self):
        self.tiles = {}
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))

        for tileset in self.tilesets_info:
            firstgid = tileset['firstgid']
            tsx_path = os.path.join(project_root, tileset['source'].replace("../", ""))

            tree = ET.parse(tsx_path)
            root = tree.getroot()

            image_elem = root.find('image')
            img_source = image_elem.get('source')

            if img_source.startswith("assets/"):
                img_full_path = os.path.join(project_root, img_source)
            else:
                img_full_path = os.path.join(os.path.dirname(tsx_path), img_source)

            img_full_path = os.path.normpath(img_full_path)

            if not os.path.isfile(img_full_path):
                raise FileNotFoundError(f"Không tìm thấy ảnh tileset: {img_full_path}")

            img_width = int(image_elem.get('width'))
            img_height = int(image_elem.get('height'))

            tilewidth = int(root.get('tilewidth'))
            tileheight = int(root.get('tileheight'))

            image = pygame.image.load(img_full_path).convert_alpha()

            tiles_x = img_width // tilewidth
            tiles_y = img_height // tileheight

            id_offset = 0
            for y in range(tiles_y):
                for x in range(tiles_x):
                    tile = pygame.Surface((tilewidth, tileheight), pygame.SRCALPHA)
                    tile.blit(image, (0, 0), (x * tilewidth, y * tileheight, tilewidth, tileheight))
                    self.tiles[firstgid + id_offset] = tile
                    id_offset += 1

    def draw(self, camera_offset=[0, 0]):
        self.screen.fill((0, 0, 0))  # Xóa màn hình
        bg_filename = f"{self.level_name}.jpg"
        bg_path = os.path.join(self.project_root, "assets", "backgrounds", bg_filename)
        if os.path.exists(bg_path):
            bg = pygame.image.load(bg_path).convert()
            bg = pygame.transform.scale(bg, (self.screen.get_width(), self.screen.get_height()))
            self.screen.blit(bg, (-camera_offset[0], -camera_offset[1]))

        for layer_idx, layer in enumerate(self.tile_layers):
            if layer_idx < len(self.tile_layers_visibility) and not self.tile_layers_visibility[layer_idx]:
                continue
            if self.level_name == "level1" and layer_idx < len(self.tile_layers_names) and self.tile_layers_names[layer_idx] == "ground":
                continue
            for idx, tile in enumerate(layer):
                tile = int(tile)
                if tile > 0:
                    col_idx = idx % self.map_width
                    row_idx = idx // self.map_width
                    img = self.tiles.get(tile)
                    if img:
                        self.screen.blit(
                            img,
                            (
                                col_idx * self.tile_width - camera_offset[0],
                                row_idx * self.tile_height - camera_offset[1]
                            )
                        )

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "menu"

            self.draw()
            pygame.display.flip()
            clock.tick(60)