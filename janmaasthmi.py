import cv2
import numpy as np
import os

# ---------- SETTINGS ----------
W, H = 1080, 1920
PW, PH = 540, 960
FPS = 30
DURATION = 10
PARTICLES = 2500

INPUT = "krishna.png"
OUTPUT = "krishna_reveal.mp4"

folder = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(folder, INPUT)
out_path = os.path.join(folder, OUTPUT)

# ---------- IMAGE ----------
img = cv2.imread(img_path)

if img is None:
    print("❌ krishna.png nahi mili!")
    print(img_path)
    exit()

# Fit image without stretching
ih, iw = img.shape[:2]
scale = min(W / iw, H / ih)

nw = int(iw * scale)
nh = int(ih * scale)

img = cv2.resize(
    img, (nw, nh),
    interpolation=cv2.INTER_LANCZOS4
)

full = np.zeros((H, W, 3), np.uint8)

x = (W - nw) // 2
y = (H - nh) // 2

full[y:y+nh, x:x+nw] = img

# Small working image = faster animation
small = cv2.resize(
    full, (PW, PH),
    interpolation=cv2.INTER_AREA
)

# ---------- EDGES ----------
gray = cv2.cvtColor(
    small, cv2.COLOR_BGR2GRAY
)

gray = cv2.GaussianBlur(
    gray, (3, 3), 0
)

edges = cv2.Canny(
    gray, 45, 120
)

ys, xs = np.where(edges > 0)

points = np.column_stack(
    (xs, ys)
)

# ---------- PARTICLES ----------
rng = np.random.default_rng(10)

if len(points) > PARTICLES:
    ids = rng.choice(
        len(points),
        PARTICLES,
        replace=False
    )
    points = points[ids]

target = points.astype(np.float32)

# Color comes from original image
colors = np.array([
    small[int(y), int(x)]
    for x, y in target
], dtype=np.uint8)

# Random starting positions
angles = rng.random(len(target)) * np.pi * 2
distance = rng.uniform(120, 320, len(target))

start = target.copy()

start[:, 0] += np.cos(angles) * distance
start[:, 1] += np.sin(angles) * distance

start[:, 0] = np.clip(
    start[:, 0], 0, PW - 1
)

start[:, 1] = np.clip(
    start[:, 1], 0, PH - 1
)

# ---------- CONNECTIONS ----------
# Connect nearby target points
grid = {}
cell = 15

for i, (px, py) in enumerate(target):
    key = (
        int(px // cell),
        int(py // cell)
    )
    grid.setdefault(key, []).append(i)

lines = []

for i, (px, py) in enumerate(target):

    gx = int(px // cell)
    gy = int(py // cell)

    found = 0

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):

            ids = grid.get(
                (gx + dx, gy + dy),
                []
            )

            for j in ids:

                if j <= i:
                    continue

                qx, qy = target[j]

                if (
                    (px-qx)**2 +
                    (py-qy)**2
                ) < 14**2:

                    lines.append((i, j))
                    found += 1

                    if found >= 2:
                        break

            if found >= 2:
                break

        if found >= 2:
            break

# ---------- VIDEO ----------
fourcc = cv2.VideoWriter_fourcc(
    *"mp4v"
)

video = cv2.VideoWriter(
    out_path,
    fourcc,
    FPS,
    (W, H)
)

# ---------- WINDOW ----------
window = "Krishna Reveal"

cv2.namedWindow(
    window,
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    window,
    PW,
    PH
)

# ---------- SMOOTH FUNCTION ----------
def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)

# ---------- ANIMATION ----------
total = FPS * DURATION

# 0 - 7.5 sec = particles
# 7.5 - 10 sec = original image reveal
reveal_frame = int(FPS * 7.5)

for frame in range(total):

    canvas = np.zeros(
        (PH, PW, 3),
        dtype=np.uint8
    )

    if frame < reveal_frame:

        p = frame / (reveal_frame - 1)
        p = smooth(p)

        # Particle movement
        pos = start + (
            target - start
        ) * p

        # Show particles gradually
        visible = int(
            len(pos) * min(1, p * 1.25)
        )

        # Particles
        for i in range(visible):

            px, py = pos[i].astype(int)

            if (
                0 <= px < PW and
                0 <= py < PH
            ):

                cv2.circle(
                    canvas,
                    (px, py),
                    2,
                    tuple(
                        map(
                            int,
                            colors[i]
                        )
                    ),
                    -1,
                    cv2.LINE_AA
                )

        # Connecting lines
        if p > 0.35:

            line_p = smooth(
                (p - 0.35) / 0.65
            )

            count = int(
                len(lines) * line_p
            )

            for a, b in lines[:count]:

                x1, y1 = pos[a].astype(int)
                x2, y2 = pos[b].astype(int)

                if (
                    0 <= x1 < PW and
                    0 <= y1 < PH and
                    0 <= x2 < PW and
                    0 <= y2 < PH
                ):

                    cv2.line(
                        canvas,
                        (x1, y1),
                        (x2, y2),
                        (180, 220, 255),
                        1,
                        cv2.LINE_AA
                    )

    else:

        # ---------- ORIGINAL IMAGE REVEAL ----------
        p = (
            frame - reveal_frame
        ) / max(
            1,
            total - reveal_frame - 1
        )

        p = smooth(p)

        pos = target

        # Particle layer
        for i in range(len(pos)):

            px, py = pos[i].astype(int)

            cv2.circle(
                canvas,
                (px, py),
                2,
                tuple(
                    map(
                        int,
                        colors[i]
                    )
                ),
                -1,
                cv2.LINE_AA
            )

        # Fade into actual image
        canvas = cv2.addWeighted(
            canvas,
            1 - p,
            small,
            p,
            0
        )

    # ---------- GLOW ----------
    glow = cv2.GaussianBlur(
        canvas,
        (0, 0),
        5
    )

    result = cv2.addWeighted(
        canvas,
        1.0,
        glow,
        0.65,
        0
    )

    # ---------- FINAL RESOLUTION ----------
    final = cv2.resize(
        result,
        (W, H),
        interpolation=cv2.INTER_CUBIC
    )

    # Last few frames = original quality
    if frame >= total - 15:
        final = full.copy()

    video.write(final)

    # ---------- LIVE PREVIEW ----------
    cv2.imshow(
        window,
        result
    )

    key = cv2.waitKey(1) & 0xFF

    if key == 27:
        break

    # F = fullscreen
    if key == ord("f"):
        cv2.setWindowProperty(
            window,
            cv2.WND_PROP_FULLSCREEN,
            cv2.WINDOW_FULLSCREEN
        )

    # W = normal window
    if key == ord("w"):
        cv2.setWindowProperty(
            window,
            cv2.WND_PROP_FULLSCREEN,
            cv2.WINDOW_NORMAL
        )
        cv2.resizeWindow(
            window,
            PW,
            PH
        )

    print(
        f"\rRendering: "
        f"{(frame + 1) * 100 // total}%",
        end=""
    )

video.release()
cv2.destroyAllWindows()

print("\n\n✅ DONE!")
print("Video:", out_path)
print("Resolution: 1080 x 1920")
print("Duration: 10 seconds")