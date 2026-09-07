import cv2
import numpy as np
import os

# ============================================================
# KRISHNA - SMOOTH COLOR PARTICLE REVEAL
# ============================================================

FINAL_W = 1080
FINAL_H = 1920

PREVIEW_W = 540
PREVIEW_H = 960

FPS = 30

# 10 second video
DURATION = 10.0

INPUT_FILE = "krishna.png"
OUTPUT_FILE = "krishna_smooth_color_reveal.mp4"

# Original image starts appearing here
IMAGE_REVEAL_START = 7.6


# ============================================================
# PATH
# ============================================================

folder = os.path.dirname(
    os.path.abspath(__file__)
)

input_path = os.path.join(
    folder,
    INPUT_FILE
)

output_path = os.path.join(
    folder,
    OUTPUT_FILE
)


# ============================================================
# LOAD IMAGE
# ============================================================

print("\nLoading Krishna image...")

original = cv2.imread(
    input_path,
    cv2.IMREAD_COLOR
)

if original is None:

    print("❌ Image not found:")
    print(input_path)

    raise SystemExit

print("✅ Image loaded!")


# ============================================================
# FIT IMAGE WITHOUT STRETCHING
# ============================================================

src_h, src_w = original.shape[:2]

scale = min(
    FINAL_W / src_w,
    FINAL_H / src_h
)

new_w = int(src_w * scale)
new_h = int(src_h * scale)

resized = cv2.resize(
    original,
    (new_w, new_h),
    interpolation=cv2.INTER_LANCZOS4
)

final_image = np.zeros(
    (FINAL_H, FINAL_W, 3),
    dtype=np.uint8
)

x = (FINAL_W - new_w) // 2
y = (FINAL_H - new_h) // 2

final_image[
    y:y + new_h,
    x:x + new_w
] = resized


# ============================================================
# PREVIEW VERSION
# ============================================================

preview = cv2.resize(
    final_image,
    (PREVIEW_W, PREVIEW_H),
    interpolation=cv2.INTER_AREA
)


# ============================================================
# EDGE DETECTION
# ============================================================

gray = cv2.cvtColor(
    preview,
    cv2.COLOR_BGR2GRAY
)

gray = cv2.GaussianBlur(
    gray,
    (3, 3),
    0
)

edges = cv2.Canny(
    gray,
    45,
    125
)


# ============================================================
# REMOVE VERY SMALL NOISE
# ============================================================

kernel = np.ones(
    (2, 2),
    np.uint8
)

edges = cv2.morphologyEx(
    edges,
    cv2.MORPH_OPEN,
    kernel
)


# ============================================================
# EDGE POINTS
# ============================================================

edge_y, edge_x = np.where(
    edges > 0
)

points = np.column_stack(
    (edge_x, edge_y)
)


print(
    "Edge points:",
    len(points)
)


# ============================================================
# LIMIT PARTICLES
# ============================================================

MAX_PARTICLES = 3500

rng = np.random.default_rng(42)

if len(points) > MAX_PARTICLES:

    indexes = rng.choice(
        len(points),
        MAX_PARTICLES,
        replace=False
    )

    points = points[indexes]


# ============================================================
# COLOR OF EACH PARTICLE
# ============================================================

particle_colors = []

for px, py in points:

    color = preview[
        int(py),
        int(px)
    ]

    particle_colors.append(
        color
    )

particle_colors = np.array(
    particle_colors,
    dtype=np.uint8
)


# ============================================================
# PARTICLE START POSITIONS
# ============================================================

target_points = points.astype(
    np.float32
)

start_points = np.zeros_like(
    target_points
)


for i in range(
    len(target_points)
):

    tx, ty = target_points[i]

    angle = rng.uniform(
        0,
        np.pi * 2
    )

    # Wider scatter
    distance = rng.uniform(
        80,
        300
    )

    sx = (
        tx +
        np.cos(angle) *
        distance
    )

    sy = (
        ty +
        np.sin(angle) *
        distance
    )

    # Keep particles inside screen
    sx = np.clip(
        sx,
        2,
        PREVIEW_W - 3
    )

    sy = np.clip(
        sy,
        2,
        PREVIEW_H - 3
    )

    start_points[i] = (
        sx,
        sy
    )


# ============================================================
# PRECOMPUTE PARTICLE ORDER
# ============================================================

# Reveal roughly from top to bottom,
# producing a more controlled motion.

order = np.argsort(
    target_points[:, 1]
    +
    target_points[:, 0] * 0.15
)

target_points = target_points[
    order
]

start_points = start_points[
    order
]

particle_colors = particle_colors[
    order
]


# ============================================================
# PRECOMPUTE CONNECTIONS
# ============================================================

print("Preparing particle connections...")

connection_pairs = []

# Grid based spatial grouping
GRID = 12

grid = {}

for i, (px, py) in enumerate(
    target_points
):

    gx = int(px // GRID)
    gy = int(py // GRID)

    key = (
        gx,
        gy
    )

    if key not in grid:
        grid[key] = []

    grid[key].append(i)


for key, indexes in grid.items():

    gx, gy = key

    nearby = []

    for dx in (-1, 0, 1):

        for dy in (-1, 0, 1):

            neighbour_key = (
                gx + dx,
                gy + dy
            )

            if neighbour_key in grid:

                nearby.extend(
                    grid[neighbour_key]
                )

    for i in indexes:

        px, py = target_points[i]

        count = 0

        for j in nearby:

            if i == j:
                continue

            qx, qy = target_points[j]

            distance = (
                (px - qx) ** 2
                +
                (py - qy) ** 2
            )

            if distance < 15 ** 2:

                connection_pairs.append(
                    (i, j)
                )

                count += 1

                if count >= 2:
                    break


# Remove duplicate connections

connection_pairs = list(
    set(connection_pairs)
)

print(
    "Connections:",
    len(connection_pairs)
)


# ============================================================
# VIDEO WRITER
# ============================================================

fourcc = cv2.VideoWriter_fourcc(
    *"mp4v"
)

video = cv2.VideoWriter(
    output_path,
    fourcc,
    FPS,
    (FINAL_W, FINAL_H)
)

if not video.isOpened():

    print("❌ Video writer failed!")

    raise SystemExit


# ============================================================
# PREVIEW WINDOW
# ============================================================

window_name = (
    "Krishna Smooth Particle Reveal"
)

cv2.namedWindow(
    window_name,
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    window_name,
    PREVIEW_W,
    PREVIEW_H
)


# ============================================================
# SMOOTHSTEP
# ============================================================

def smoothstep(t):

    t = np.clip(
        t,
        0.0,
        1.0
    )

    return (
        t * t *
        (3.0 - 2.0 * t)
    )


# ============================================================
# TOTAL FRAMES
# ============================================================

total_frames = int(
    FPS * DURATION
)

image_reveal_frame = int(
    FPS * IMAGE_REVEAL_START
)


print("\n======================================")
print("      KRISHNA PARTICLE REVEAL")
print("======================================")
print("Resolution :", "1080 x 1920")
print("Preview    :", "540 x 960")
print("FPS        :", FPS)
print("Duration   :", DURATION, "seconds")
print("Particles  :", len(target_points))
print("\nStarting...\n")


# ============================================================
# MAIN LOOP
# ============================================================

for frame_no in range(
    total_frames
):

    # --------------------------------------------------------
    # BLACK CANVAS
    # --------------------------------------------------------

    canvas = np.zeros(
        (
            PREVIEW_H,
            PREVIEW_W,
            3
        ),
        dtype=np.uint8
    )


    # --------------------------------------------------------
    # MAIN PARTICLE PROGRESS
    # --------------------------------------------------------

    if frame_no < image_reveal_frame:

        progress = (
            frame_no /
            max(
                1,
                image_reveal_frame - 1
            )
        )

        progress = smoothstep(
            progress
        )

        # Slightly cinematic timing
        movement_progress = (
            progress ** 0.72
        )


        # ----------------------------------------------------
        # CALCULATE CURRENT PARTICLE POSITIONS
        # ----------------------------------------------------

        current_points = (
            start_points
            +
            (
                target_points
                -
                start_points
            )
            *
            movement_progress
        )


        # ----------------------------------------------------
        # PARTICLE DRAWING
        # ----------------------------------------------------

        visible = int(
            len(current_points)
            *
            min(
                1.0,
                progress * 1.15
            )
        )

        visible = max(
            1,
            visible
        )


        for i in range(
            visible
        ):

            px = int(
                current_points[i][0]
            )

            py = int(
                current_points[i][1]
            )

            if (
                px < 0
                or
                px >= PREVIEW_W
                or
                py < 0
                or
                py >= PREVIEW_H
            ):
                continue


            color = (
                int(particle_colors[i][0]),
                int(particle_colors[i][1]),
                int(particle_colors[i][2])
            )


            # Small particle
            cv2.circle(
                canvas,
                (px, py),
                2,
                color,
                -1,
                cv2.LINE_AA
            )


        # ----------------------------------------------------
        # CONNECTIONS
        # ----------------------------------------------------

        if progress > 0.38:

            line_alpha = (
                progress - 0.38
            ) / 0.62

            line_alpha = np.clip(
                line_alpha,
                0,
                1
            )

            connection_limit = int(
                len(connection_pairs)
                *
                line_alpha
            )


            for i in range(
                connection_limit
            ):

                a, b = (
                    connection_pairs[i]
                )

                x1 = int(
                    current_points[a][0]
                )

                y1 = int(
                    current_points[a][1]
                )

                x2 = int(
                    current_points[b][0]
                )

                y2 = int(
                    current_points[b][1]
                )


                if (
                    0 <= x1 < PREVIEW_W
                    and
                    0 <= y1 < PREVIEW_H
                    and
                    0 <= x2 < PREVIEW_W
                    and
                    0 <= y2 < PREVIEW_H
                ):

                    cv2.line(
                        canvas,
                        (x1, y1),
                        (x2, y2),
                        (
                            170,
                            210,
                            255
                        ),
                        1,
                        cv2.LINE_AA
                    )


    # ========================================================
    # ORIGINAL IMAGE REVEAL
    # ========================================================

    else:

        fade_progress = (
            frame_no
            -
            image_reveal_frame
        ) / max(
            1,
            total_frames
            -
            image_reveal_frame
            -
            1
        )

        fade_progress = smoothstep(
            fade_progress
        )


        # Keep particle silhouette
        current_points = target_points


        for i in range(
            len(current_points)
        ):

            px = int(
                current_points[i][0]
            )

            py = int(
                current_points[i][1]
            )

            color = (
                int(particle_colors[i][0]),
                int(particle_colors[i][1]),
                int(particle_colors[i][2])
            )

            cv2.circle(
                canvas,
                (px, py),
                2,
                color,
                -1,
                cv2.LINE_AA
            )


        # Fade into real image
        canvas = cv2.addWeighted(
            canvas,
            1.0 - fade_progress,
            preview,
            fade_progress,
            0
        )


    # ========================================================
    # COLOR GLOW
    # ========================================================

    glow = cv2.GaussianBlur(
        canvas,
        (0, 0),
        5
    )

    result_preview = cv2.addWeighted(
        canvas,
        1.0,
        glow,
        0.65,
        0
    )


    # ========================================================
    # UPSCALE
    # ========================================================

    result = cv2.resize(
        result_preview,
        (
            FINAL_W,
            FINAL_H
        ),
        interpolation=cv2.INTER_CUBIC
    )


    # ========================================================
    # FINAL FEW FRAMES = REAL HIGH QUALITY IMAGE
    # ========================================================

    if frame_no >= total_frames - 12:

        result = final_image.copy()


    # ========================================================
    # WRITE
    # ========================================================

    video.write(
        result
    )


    # ========================================================
    # LIVE PREVIEW
    # ========================================================

    cv2.imshow(
        window_name,
        result_preview
    )


    # ========================================================
    # CONTROLS
    # ========================================================

    key = cv2.waitKey(1) & 0xFF

    # ESC
    if key == 27:

        print(
            "\n\n⛔ Stopped by user."
        )

        break


    # F = Fullscreen
    if key == ord("f"):

        cv2.setWindowProperty(
            window_name,
            cv2.WND_PROP_FULLSCREEN,
            cv2.WINDOW_FULLSCREEN
        )


    # W = Window mode
    if key == ord("w"):

        cv2.setWindowProperty(
            window_name,
            cv2.WND_PROP_FULLSCREEN,
            cv2.WINDOW_NORMAL
        )

        cv2.resizeWindow(
            window_name,
            PREVIEW_W,
            PREVIEW_H
        )


    # ========================================================
    # PROGRESS
    # ========================================================

    percent = int(
        (
            (frame_no + 1)
            /
            total_frames
        )
        *
        100
    )

    print(
        f"\rRendering: {percent}%",
        end=""
    )


# ============================================================
# CLEANUP
# ============================================================

video.release()

cv2.destroyAllWindows()


# ============================================================
# DONE
# ============================================================

print("\n\n======================================")
print("          ✅ VIDEO COMPLETE")
print("======================================")

print("\nFile:")
print(output_path)

print("\nResolution:")
print("1080 x 1920")

print("\nDuration:")
print(f"{DURATION} seconds")

print("\nFPS:")
print(FPS)

print("\nColor particles:")
print("YES")

print("\nFull-screen preview:")
print("Press F")

print("\nExit:")
print("Press ESC")