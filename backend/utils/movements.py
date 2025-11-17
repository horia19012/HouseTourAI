import os
import re


def get_movements_for_images_numbered(folder_path, relations):
    def extract_number(filename):
        match = re.match(r"(\d+)", filename)
        return int(match.group(1)) if match else float('inf')

    images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    images.sort(key=extract_number)

    relation_to_moves = {
        "right-of": ["move-left", "move-right"],
        "left-of": ["move-right", "move-left"],
        "front-of": ["move-backward", "move-backward"]
    }

    result = {}
    for i, rel in enumerate(relations):
        if rel not in relation_to_moves:
            raise ValueError(f"Unsupported relation: {rel}")
        result[images[i]] = relation_to_moves[rel]

    return result


def split_and_reverse_moves(moves_dict, folder_path):
    def extract_number(filename):
        match = re.match(r"(\d+)", filename)
        return int(match.group(1)) if match else float('inf')

    import os
    images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    images.sort(key=extract_number)

    result = {}

    for i, img in enumerate(images):
        if img in moves_dict:
            current_first = moves_dict[img][0]
            current_moves = [current_first]

            if i > 0:
                prev_img = images[i - 1]
                if prev_img in moves_dict:
                    prev_second = moves_dict[prev_img][1]
                    reversed_move = prev_second + "-REVERSED"

                    if not (("move-backward" in current_first and "move-backward" in reversed_move)
                            or (current_first == reversed_move)):
                        current_moves.insert(0, reversed_move)

            result[img] = current_moves
        else:
            used_images = sorted(moves_dict.keys(), key=extract_number)
            last_used = used_images[-1]
            last_second = moves_dict[last_used][1]
            reversed_last = last_second + "-REVERSED"
            result[img] = [reversed_last]

    return result


def extract_number(filename):
    import re
    match = re.match(r"(\d+)", filename)
    return int(match.group(1)) if match else float('inf')
