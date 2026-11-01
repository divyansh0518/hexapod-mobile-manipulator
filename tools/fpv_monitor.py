"""Preview a separate USB capture receiver or RTSP link; no NRF video transport."""
import argparse
import time
import cv2
p=argparse.ArgumentParser();p.add_argument("--source",default="0");p.add_argument("--record")
a=p.parse_args();source=int(a.source) if a.source.isdigit() else a.source
cap=cv2.VideoCapture(source);cap.set(cv2.CAP_PROP_BUFFERSIZE,1)
writer=None
try:
    if not cap.isOpened(): raise RuntimeError("Video receiver unavailable")
    while True:
        ok,frame=cap.read()
        if not ok: break
        if a.record:
            if writer is None:
                h,w=frame.shape[:2];writer=cv2.VideoWriter(a.record,cv2.VideoWriter_fourcc(*"mp4v"),30,(w,h))
            writer.write(frame)
        cv2.imshow("Independent FPV receiver - Q to quit",frame)
        if cv2.waitKey(1)&255==ord("q"): break
finally:
    cap.release()
    if writer: writer.release()
    cv2.destroyAllWindows()
