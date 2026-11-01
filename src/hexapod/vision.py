"""Calibrated planar projection; host ONNX detector with explicit model contract."""
import numpy as np
from .model import finite

def pixel_to_plane(u,v,cfg):
    if not cfg["calibrated"]: raise ValueError("Camera calibration required")
    K=finite(cfg["K"]);T=finite(cfg["T_body_camera"])
    ray=T[:3,:3]@np.linalg.solve(K,np.array([u,v,1.]))
    origin=T[:3,3]
    if abs(ray[2])<1e-8: raise ValueError("Ray parallel to plane")
    scale=(cfg["plane_z_mm"]-origin[2])/ray[2]
    if scale<=0: raise ValueError("Plane behind camera")
    return origin+scale*ray

class OnnxDetector:
    """Contract: float32 RGB NCHW 1x3xHxW -> [1,N,6] xyxy,score,class_id.

    Coordinates in resized input pixels. Use a model exported WITH NMS; raw
    YOLO output requires a separate decoder and is deliberately rejected.
    """
    def __init__(self,path,labels):
        import onnxruntime as ort
        self.session=ort.InferenceSession(path,providers=["CPUExecutionProvider"])
        self.input=self.session.get_inputs()[0]; self.labels=labels
        self.h,self.w=self.input.shape[2:]
        if not isinstance(self.h,int) or not isinstance(self.w,int):
            raise ValueError("Export fixed input resolution")
    def detect(self,frame,threshold=.5):
        import cv2
        h,w=frame.shape[:2]
        img=cv2.resize(frame,(self.w,self.h))[:,:,::-1].transpose(2,0,1).copy()
        output=np.asarray(self.session.run(None,{self.input.name:img[None].astype(np.float32)/255})[0])
        if output.ndim!=3 or output.shape[0]!=1 or output.shape[2]!=6:
            raise ValueError("Model must return [1,N,6] post-NMS detections")
        detections=[]
        for x1,y1,x2,y2,score,cid in output[0]:
            if not np.all(np.isfinite([x1,y1,x2,y2,score,cid])): continue
            if score<threshold or x2<=x1 or y2<=y1: continue
            cid=int(cid)
            if not 0<=cid<len(self.labels): continue
            detections.append({"label":self.labels[cid],"confidence":float(score),
                 "pixel":[float((x1+x2)/2*w/self.w),float((y1+y2)/2*h/self.h)]})
        return detections

def resolve_target(event,cfg):
    if event.get("kind")=="qr":
        code=event["code"]
        if code not in cfg["targets"]: raise ValueError("Unknown target label")
        # Surveyed lookup, NOT monocular depth estimation.
        return finite(cfg["targets"][code])
    if event.get("kind")=="detection":
        if event.get("confidence",0)<.7: raise ValueError("Low detection confidence")
        return pixel_to_plane(*finite(event["pixel"]),cfg["camera"])
    raise ValueError("Event is not a spatial manipulation target")
