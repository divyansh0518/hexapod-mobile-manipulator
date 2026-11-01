import argparse
import csv
import json
from pathlib import Path
import time
import numpy as np
from .model import load_config
from .control import Controller
from .gait import GAITS,support_margin
from .protocol import encode
from .vision import resolve_target

def simulate(args,cfg):
    if not 0<args.seconds<=600: raise ValueError("Choose duration in (0,600]")
    c=Controller(cfg);rate=cfg["control"]["rate_hz"];rows=[]
    for n in range(int(args.seconds*rate)):
        angles,state=c.tick(1/rate,(args.speed,0,args.yaw),args.gait,1000)
        feet,stance=c.gait.targets(c.phase_time,c.last_command,args.gait)
        rows.append([n/rate,state,int(stance.sum()),support_margin(feet,stance),*angles])
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["time_s","state","stance_legs","ideal_support_margin_mm"]+[f"servo_{i}_deg" for i in range(24)]);w.writerows(rows)
    print(f"Simulation: {len(rows)} frames -> {out}. No physical dynamics or hardware measurements.")

def arm_demo(args,cfg):
    c=Controller(cfg);target=np.array(args.target)
    c.set_target(target)
    for _ in range(300): c.tick(.02,distance_mm=1000)
    actual=c.arm.fk(c.arm_q)[:3,3]
    print(json.dumps({"target_mm":target.tolist(),"achieved_mm":actual.tolist(),"error_mm":float(np.linalg.norm(actual-target)),"joint_deg":np.rad2deg(c.arm_q).tolist()},indent=2))

def run(args,cfg):
    import serial
    if not args.enable_motion or not cfg["servo"]["hardware_calibrated"]:
        raise ValueError("Live operation requires --enable-motion and hardware_calibrated=true after calibration")
    c=Controller(cfg);seq=0;last_status=0.;status={};event_buffer=bytearray();rx=bytearray()
    rate=cfg["control"]["rate_hz"];interval=1/rate
    vision=serial.Serial(args.vision_port,115200,timeout=0) if args.vision_port else None
    with serial.Serial(args.port,115200,timeout=0,write_timeout=.2) as link:
        time.sleep(2) # Mega USB auto-reset. No arm frames during startup.
        link.write(encode(c.servo,seq));seq+=1  # Explicit startup disarm clears a restored stop loop.
        started=time.monotonic();previous=started
        try:
            while args.seconds<=0 or time.monotonic()-started<args.seconds:
                now=time.monotonic();dt=now-previous
                if dt<interval: time.sleep(min(interval-dt,.005));continue
                if dt>.1: raise ValueError("Host missed control deadline")
                previous=now
                rx.extend(link.read(link.in_waiting))
                if len(rx)>8192: raise ValueError("Telemetry overflow")
                while b"\n" in rx:
                    line,_,rx=rx.partition(b"\n")
                    try:
                        obj=json.loads(line)
                        if obj.get("type")=="status": status=obj;last_status=now
                    except (ValueError,TypeError): pass
                live=now-last_status<cfg["control"]["watchdog_s"]
                enabled=live and status.get("radio_ok",False) and status.get("deadman",False) and status.get("physical_enable",False) and not status.get("estop",True)
                cmd=np.array(status.get("axes",[0,0,0]))/1000 if enabled else np.zeros(3)
                events=[]
                if vision:
                    event_buffer.extend(vision.read(vision.in_waiting))
                    if len(event_buffer)>8192: raise ValueError("Vision stream overflow")
                    while b"\n" in event_buffer:
                        line,_,event_buffer=event_buffer.partition(b"\n")
                        try: events.append(json.loads(line))
                        except ValueError: pass
                # Latest serial event only. Position lookup / camera projection are
                # opt-in; no autonomous base motion and no unobserved grasp claim.
                if enabled and args.allow_vision_targets and np.linalg.norm(cmd)<.01 and events:
                    try: c.set_target(resolve_target(events[-1],cfg))
                    except (ValueError,KeyError,TypeError) as e: print(f"Target rejected: {e}")
                dist=status.get("distance_mm") if live else None
                gait=list(GAITS)[min(2,max(0,int(status.get("gait",0))))]
                angles,state=c.tick(dt,cmd,gait,dist,enabled)
                link.write(encode(angles,seq,armed=enabled and state=="active"));seq+=1
        finally:
            try: link.write(encode(c.servo,seq,stop=True));link.flush()
            finally:
                if vision: vision.close()

def vision_host(args,cfg):
    import cv2
    from .vision import OnnxDetector
    labels=Path(args.labels).read_text().splitlines();detector=OnnxDetector(args.model,labels)
    cap=cv2.VideoCapture(args.camera)
    if not cap.isOpened(): raise ValueError("Camera unavailable")
    try:
        while True:
            ok,frame=cap.read()
            if not ok: break
            for d in detector.detect(frame):
                print(json.dumps({"kind":"detection",**d}),flush=True)
    finally: cap.release()

def main():
    p=argparse.ArgumentParser(description="Hexapod research platform; simulation by default")
    p.add_argument("--config",default="config/robot.json")
    sub=p.add_subparsers(dest="action",required=True)
    s=sub.add_parser("simulate");s.add_argument("--gait",choices=list(GAITS),default="tripod")
    s.add_argument("--seconds",type=float,default=10);s.add_argument("--speed",type=float,default=.5);s.add_argument("--yaw",type=float,default=0)
    s.add_argument("--output",default="logs/simulation.csv")
    a=sub.add_parser("arm-demo");a.add_argument("--target",nargs=3,type=float,default=[220,20,150])
    r=sub.add_parser("run");r.add_argument("--port",required=True);r.add_argument("--vision-port")
    r.add_argument("--enable-motion",action="store_true");r.add_argument("--allow-vision-targets",action="store_true");r.add_argument("--seconds",type=float,default=30)
    v=sub.add_parser("vision-host");v.add_argument("--model",required=True);v.add_argument("--labels",required=True);v.add_argument("--camera",type=int,default=0)
    args=p.parse_args()
    try: {"simulate":simulate,"arm-demo":arm_demo,"run":run,"vision-host":vision_host}[args.action](args,load_config(args.config))
    except (ValueError,KeyError) as e: p.exit(2,f"Error: {e}\n")
    except KeyboardInterrupt: pass

if __name__=="__main__": main()
