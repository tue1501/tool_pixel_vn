import sys
import time
from pathlib import Path

import pyautogui


# Change these filenames to match where you save the reference images.
# Expected files:
#   images/challenge.png
#   images/fight.png
#   images/play.png
#   images/close.png
IMAGE_STEPS = [
    ("challenge", Path("images/challenge.png")),
    ("fight", Path("images/fight.png")),
    ("play", Path("images/play.png")),
    ("close", Path("images/close.png")),
]


def wait_and_click(tag: str, image_path: Path, timeout: float = 20.0, interval: float = 0.6) -> bool:
    """
    Look for image on screen within timeout; click when found.
    Returns True on success, False on timeout.
    """
    # Try multiple confidences to be less strict if colors/scale differ slightly
    confidences = [0.85, 0.8, 0.75, 0.7, 0.65, 0.6]

    start = time.time()
    while time.time() - start < timeout:
        for conf in confidences:
            try:
                found = pyautogui.locateCenterOnScreen(
                    str(image_path),
                    confidence=conf,
                    grayscale=True,
                )
            except pyautogui.ImageNotFoundException:
                found = None

            if found:
                pyautogui.click(found)
                print(f"[OK] Clicked '{tag}' at {found} (conf={conf})")
                return True

        time.sleep(interval)

    print(f"[TIMEOUT] Could not find '{tag}' using {image_path}")
    return False


def run_once() -> bool:
    """
    Run the sequence once.
    If a step is missing, stop the sequence and return False (do not click next steps).
    """
    # Pre-resolve the close button image so we can try a fallback click on failure
    close_path = dict(IMAGE_STEPS).get("close")

    for idx, (tag, path) in enumerate(IMAGE_STEPS, start=1):
        if not path.exists():
            print(f"[MISSING] {path} not found. Save the reference image first.")
            return False

        ok = wait_and_click(tag, path)
        if not ok:
            # Try clicking "close" once before restarting the cycle
            if close_path and close_path.exists() and tag != "close":
                print("[RECOVER] Không thấy nút, thử bấm 'close' rồi chạy lại chu kỳ.")
                wait_and_click("close", close_path, timeout=6.0, interval=0.4)
            # Stop this cycle; we will retry from the first button on next loop
            return False

        # Thời gian chờ giữa các nút
        # Sau nút 2 ("fight") chờ lâu hơn một chút
        if idx == 2:
            time.sleep(3.5)
        # Sau nút 3 chờ 2 giây rồi mới sang nút 4
        elif idx == 3:
            time.sleep(2.0)
        # Các nút khác chờ ngắn
        else:
            time.sleep(1.0)  # brief pause before next step

    return True


def main() -> int:
    print("Bắt đầu sau 3 giây... Di chuyển chuột ra khỏi vùng nút.")
    time.sleep(3)

    cycle = 0
    try:
        while True:
            cycle += 1
            print(f"\n[LOOP] Chu kỳ {cycle}")
            finished = run_once()
            if finished:
                print("[DONE] Đã bấm đủ 4 bước.")
            else:
                print("[RETRY] Chưa đủ nút, sẽ thử lại từ bước 1.")
            time.sleep(1.0)  # nhỏ để tránh spam CPU
    except KeyboardInterrupt:
        print("\nĐã dừng theo yêu cầu.")
        return 130


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nStopped by user.")
        sys.exit(130)

