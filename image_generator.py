from PIL import Image, ImageOps
import random

# #opens an image:
# im = Image.open("1_tree.jpg")
# #creates a new empty image, RGB mode, and size 400 by 400.
# new_im = Image.new('RGB', (400,400))

# #Here I resize my opened image, so it is no bigger than 100,100
# im.thumbnail((100,100))
# #Iterate through a 4 by 4 grid with 100 spacing, to place my image
# for i in xrange(0,500,100):
#     for j in xrange(0,500,100):
#         #I change brightness of the images, just to emphasise they are unique copies.
#         im=Image.eval(im,lambda x: x+(i+j)/30)
#         #paste the image at location i,j:
#         new_im.paste(im, (i,j))

# new_im.show()

# dimensions = 128, 128
# grid = [
#     (0, 0), (0, 32), (32, 0), (32, 32)
# ]
tiles = dict(
    wall1=(39, 15),
    wall2=(40, 18),
    wall3=(40, 19),
    wall4=(40, 20),
    wall_b1=(34, 15),
    wall_b2=(38, 18),
    wall_b3=(38, 20),
    wall_bl1=(35, 15),
    wall_bl2=(37, 20),
    wall_br1=(37, 15),
    wall_br2=(39, 20),
    wall_top1=(39, 16),
    wall_top2=(38, 19),
    wall_tl1=(38, 16),
    wall_tl2=(37, 19),
    wall_tr1=(40, 16),
    wall_tr2=(39, 19),
    wall_left=(38, 15),
    wall_right=(40, 15),
    wall_s_h=(34, 16),
    wall_s_v=(32, 24),
    wall_s_l=(35, 16),
    wall_s_r=(37, 16),
    wall_s_b=(36, 15),
    wall_s_t=(33, 24),
    wall_s=(36, 16),
    floor1=(8, 10),
    floor2=(6, 0),
    floor3=(6, 1),
    floor4=(5, 6),
    floor5=(6, 6),
    floor_bottom=(6, 1),
    pillar=(35, 20),
    pillar_top=(34, 20),
    clutter=(
        (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (7, 1),
        (7, 0), (0, 3), (1, 3), (2, 3), (3, 3), (0, 4), (1, 4), (2, 4), (3, 4),
        (14, 10), (14, 14), (14, 15), (13, 15),
        (8, 8), (9, 8), (10, 8), (11, 8), (12, 8), (13, 8), (14, 8), (15, 8)
    ),
    rare_clutter=(
        (0, 0), (1, 0), (2, 0),
        (14, 11), (14, 12), (14, 13), (14, 16), (13, 16),
        (15, 10), (15, 11), (15, 12), (15, 13), (15, 14), (15, 15), (15, 16),
    ),
    col_obj=(
        (15, 0), (19, 0), (15, 8), (14, 8), (41, 10), (42, 10), (43, 10),
        (42, 11), (43, 11),
    ),
)


def get_tile_from_sheet(x, y, image, tile_size, separator=0):
    return image.crop(
        (
            x * tile_size + separator * x,
            y * tile_size + separator * y,
            x * tile_size + separator * x + tile_size,
            y * tile_size + separator * y + tile_size
        )
    )


def grid_to_image(grid, target, dimensions):
    # img = Image.open(image + ".png")
    # img_b = Image.open(image + "_b" + ".png")
    spritesheet = Image.open("spritesheet.png")
    spritesheet2 = Image.open("spritesheet2.png")
    new_img = Image.new("RGBA", dimensions)
    new_img_l2 = Image.new("RGBA", dimensions)
    new_img_overlay = Image.new("RGBA", dimensions)
    # l_tiles, r_tiles, t_tiles, b_tiles, tiles = analyze_grid(grid)
    # for tile in tiles:
    #     new_img.paste(img, (tile[0], dimensions[1] - tile[1] - 32))
    # for tile in b_tiles:
    #     new_img.paste(img_b, (tile[0], dimensions[1] - tile[1] - 32))
    for key, value in grid.items():
        rotate = 0
        clutter = False
        rare_clutter = False
        flip = False
        c_flip = False
        if value == "floor":
            value = random.choice(
                ["floor1", "floor2", "floor3", "floor4", "floor5"]
            )
            if not random.randint(0, 16):
                if not random.randint(0, 8):
                    rare_clutter = True
                else:
                    clutter = True
                if random.randint(0, 1):
                    c_flip = True
            if not random.randint(0, 2):
                flip = True
        elif value == "wall":
            if not random.randint(0, 2):
                value = random.choice(["wall2", "wall3", "wall4"])
            else:
                value = "wall1"
        elif value == "wall_top":
            value = random.choice(["wall_top1", "wall_top2"])
        elif value == "wall_topleft":
            value = random.choice(["wall_tl1", "wall_tl2"])
        elif value == "wall_topright":
            value = random.choice(["wall_tr1", "wall_tr2"])
        elif value == "wall_bottom":
            value = random.choice(["wall_b1", "wall_b2", "wall_b3"])
        elif value == "wall_bottomleft":
            value = random.choice(["wall_bl1", "wall_bl2"])
        elif value == "wall_bottomright":
            value = random.choice(["wall_br1", "wall_br2"])

        if value == "pillar":
            img = get_tile_from_sheet(
                *tiles["floor1"], spritesheet, 32, separator=2
            )
            new_img.paste(img, (key[0], dimensions[1] - key[1] - 32))
            img = get_tile_from_sheet(
                *tiles["pillar"], spritesheet, 32, separator=2
            )
            new_img_l2.paste(img, (key[0], dimensions[1] - key[1] - 32))
            img = get_tile_from_sheet(
                *tiles["pillar_top"], spritesheet, 32, separator=2
            )
            new_img_overlay.paste(img, (key[0], dimensions[1] - key[1] - 64))
        elif value == "col_obj":
            img = get_tile_from_sheet(
                *tiles["floor1"], spritesheet, 32, separator=2
            )
            new_img.paste(img, (key[0], dimensions[1] - key[1] - 32))
            tile = random.choice(tiles["col_obj"])
            img = get_tile_from_sheet(
                *tile, spritesheet, 32, separator=2
            )
            new_img_l2.paste(img, (key[0], dimensions[1] - key[1] - 32))
        else:
            img = get_tile_from_sheet(
                *tiles[value], spritesheet, 32, separator=2
            )
            if rotate:
                img = img.rotate(rotate)
                # if random.randint(0, 1):
                #     img.rotate(random.choice([0, 90, 180, 270]))
            if flip:
                img = ImageOps.mirror(img)
            new_img.paste(img, (key[0], dimensions[1] - key[1] - 32))
            if clutter:
                tile = random.choice(tiles["clutter"])
            elif rare_clutter:
                tile = random.choice(tiles["rare_clutter"])
            if clutter or rare_clutter:
                img = get_tile_from_sheet(
                    *tile, spritesheet2, 32, separator=2
                )
                if c_flip:
                    img = ImageOps.mirror(img)
                new_img_l2.paste(img, (key[0], dimensions[1] - key[1] - 32))

    # new_img.paste(new_img_l2, (0, 0), new_img_l2)
    Image.alpha_composite(new_img, new_img_l2).save(
        "resources/{0}.png".format(target)
    )
    new_img_overlay.save("resources/{0}_overlay.png".format(target))
    # return new_img

# result = grid_to_image(grid, img, dimensions)
