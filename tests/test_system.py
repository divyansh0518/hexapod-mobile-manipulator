import unittest
import json
from pathlib import Path
import numpy as np
from hexapod.model import load_config,Legs,ServoMap
from hexapod.gait import Gait,GAITS,support_margin
from hexapod.arm import Arm,rotation_error
from hexapod.control import Controller
from hexapod.protocol import encode,decode,FRAME_SIZE
from hexapod.vision import pixel_to_plane,resolve_target

class SystemTests(unittest.TestCase):
    def setUp(self): self.cfg=load_config()
    def test_reference_measurements(self):
        self.assertEqual(self.cfg["geometry"]["links_mm"],[38.,86.25,160.5])
        self.assertEqual(self.cfg["geometry"]["mounts_mm"][0],[100.94,-57.11])
    def test_leg_round_trip_all_gaits(self):
        legs=Legs(self.cfg["geometry"]);gait=Gait(legs,self.cfg["gait"]);mapper=ServoMap(self.cfg["servo"])
        arm=Arm(self.cfg["arm"])
        for name in GAITS:
            for t in np.linspace(0,2,121):
                feet,stance=gait.targets(t,(.6,.25,.3),name)
                joints=[]
                for i,p in enumerate(feet):
                    q=legs.ik(i,p);np.testing.assert_allclose(legs.fk(i,q),p,atol=1e-8);joints.extend(q)
                mapper.encode(np.r_[joints,arm.home])
                self.assertGreaterEqual(stance.sum(),3)
                self.assertGreater(support_margin(feet,stance),0)
    def test_leg_rejects_unreachable_and_nan(self):
        legs=Legs(self.cfg["geometry"])
        for target in ([900,0,0],[np.nan,0,0]):
            with self.assertRaises(ValueError): legs.ik(0,target)
    def test_arm_pose_ik(self):
        arm=Arm(self.cfg["arm"])
        target=arm.fk(arm.home+np.deg2rad([5,4,-4,8,3,-4]))
        q=arm.ik(target[:3,3],target[:3,:3])
        T=arm.fk(q)
        self.assertLess(np.linalg.norm(T[:3,3]-target[:3,3]),.5)
        self.assertLess(np.linalg.norm(rotation_error(target[:3,:3],T[:3,:3])),.02)
    def test_arm_rejects_unreachable(self):
        with self.assertRaises(ValueError): Arm(self.cfg["arm"]).ik([10000,0,0])
    def test_protocol_crc_range_and_size(self):
        raw=encode(np.linspace(10,170,24),65535,True)
        self.assertEqual(len(raw),FRAME_SIZE);self.assertEqual(FRAME_SIZE,56)
        out=decode(raw);self.assertTrue(out["armed"]);self.assertEqual(out["seq"],65535)
        np.testing.assert_allclose(out["angles"],np.linspace(10,170,24),atol=.05)
        bad=bytearray(raw);bad[15]^=1
        with self.assertRaises(ValueError): decode(bad)
        with self.assertRaises(ValueError): encode([float("nan")]*24)
    def test_watchdog_inhibition_and_speed(self):
        c=Controller(self.cfg);before=c.servo.copy()
        for kwargs in ({"enabled":False,"distance_mm":1000},{"distance_mm":None},{"distance_mm":100}):
            a,s=c.tick(.02,(1,0,0),**kwargs);self.assertEqual(s,"inhibited");np.testing.assert_equal(a,before)
        for _ in range(400):
            a,s=c.tick(.02,(.5,0,0),distance_mm=1000)
            self.assertLessEqual(np.max(abs(a-before)),1.2+1e-9);before=a
    def test_projection_and_survey_lookup(self):
        cam=self.cfg["camera"]
        with self.assertRaises(ValueError): pixel_to_plane(160,120,cam)
        cam["calibrated"]=True
        np.testing.assert_allclose(pixel_to_plane(160,120,cam),[0,0,0])
        np.testing.assert_allclose(resolve_target({"kind":"qr","code":"DEMO_TARGET"},self.cfg),[220,20,150])
        with self.assertRaises(ValueError): resolve_target({"kind":"classification"},self.cfg)
    def test_stationary_arm_reaches_target(self):
        c=Controller(self.cfg);target=[220,20,150];c.set_target(target)
        for _ in range(300): c.tick(.02,distance_mm=1000)
        self.assertLess(np.linalg.norm(c.arm.fk(c.arm_q)[:3,3]-target),.5)
    def test_gait_trajectory_continuity(self):
        g=Gait(Legs(self.cfg["geometry"]),self.cfg["gait"])
        for name,(_,offsets) in GAITS.items():
            for t in np.linspace(0,2,241):
                a,_=g.targets(t,(.5,0,.2),name);b,_=g.targets(t+1e-6,(.5,0,.2),name)
                self.assertLess(np.max(abs(a-b)),.01)

if __name__=="__main__": unittest.main()
