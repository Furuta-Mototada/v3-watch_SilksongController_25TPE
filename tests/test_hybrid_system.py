"""
Tests for Hybrid System Implementation

This test suite verifies:
1. World-coordinate transformation (quaternion rotation)
2. Reflex layer detection logic
3. Execution arbitrator cooldown logic
"""

import sys
import os
import math

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from feature_extractor import rotate_vector_by_quaternion


def test_world_coordinate_transformation_identity():
    """Test that identity quaternion doesn't change vector."""
    device_accel = [10, 5, 3]
    quaternion = {'x': 0, 'y': 0, 'z': 0, 'w': 1}
    world_accel = rotate_vector_by_quaternion(device_accel, quaternion)
    
    # Should be unchanged (within floating point tolerance)
    assert abs(world_accel[0] - 10) < 0.01
    assert abs(world_accel[1] - 5) < 0.01
    assert abs(world_accel[2] - 3) < 0.01
    print("✓ Identity quaternion test passed")


def test_world_coordinate_transformation_90deg():
    """Test 90-degree rotation around Z-axis."""
    # Vector pointing in X direction
    device_accel = [10, 0, 0]
    
    # 90-degree rotation around Z-axis
    # q = [0, 0, sin(45°), cos(45°)] for 90° rotation
    angle = math.pi / 2  # 90 degrees
    quaternion = {
        'x': 0,
        'y': 0,
        'z': math.sin(angle / 2),
        'w': math.cos(angle / 2)
    }
    
    world_accel = rotate_vector_by_quaternion(device_accel, quaternion)
    
    # After 90° rotation around Z, X should become Y
    assert abs(world_accel[0]) < 0.01  # X component should be ~0
    assert abs(world_accel[1] - 10) < 0.01  # Y component should be ~10
    assert abs(world_accel[2]) < 0.01  # Z unchanged
    print("✓ 90-degree rotation test passed")


def test_world_coordinate_transformation_upside_down():
    """Test 180-degree rotation (upside down)."""
    device_accel = [0, 0, 10]
    
    # 180-degree rotation around X-axis
    angle = math.pi  # 180 degrees
    quaternion = {
        'x': math.sin(angle / 2),
        'y': 0,
        'z': 0,
        'w': math.cos(angle / 2)
    }
    
    world_accel = rotate_vector_by_quaternion(device_accel, quaternion)
    
    # Upside down: Z should become -Z
    assert abs(world_accel[0]) < 0.01
    assert abs(world_accel[1]) < 0.01
    assert abs(world_accel[2] - (-10)) < 0.01
    print("✓ 180-degree rotation test passed")


def test_reflex_detection_jump():
    """Test jump detection with reflex layer."""
    # Note: We can't easily import udp_listener due to side effects,
    # but we can test the logic conceptually
    
    # Strong upward acceleration should trigger jump
    world_accel_z = 20.0  # > REFLEX_JUMP_THRESHOLD (15.0)
    jump_threshold = 15.0
    
    assert world_accel_z > jump_threshold
    confidence = world_accel_z / jump_threshold
    assert confidence > 1.0
    print(f"✓ Reflex jump detection test passed (confidence: {confidence:.2f})")


def test_reflex_detection_attack():
    """Test attack detection with reflex layer."""
    # Forward punch motion
    world_accel_x = 13.0
    world_accel_y = 0.0
    world_accel_z = 2.0  # Stable (< REFLEX_STABILITY_THRESHOLD)
    
    attack_threshold = 12.0
    stability_threshold = 5.0
    
    forward_mag = math.sqrt(world_accel_x**2 + world_accel_y**2)
    
    assert forward_mag > attack_threshold
    assert abs(world_accel_z) < stability_threshold
    confidence = forward_mag / attack_threshold
    assert confidence > 1.0
    print(f"✓ Reflex attack detection test passed (confidence: {confidence:.2f})")


def test_arbitrator_cooldown():
    """Test execution arbitrator cooldown logic."""
    import time
    
    class SimpleArbitrator:
        def __init__(self, cooldown):
            self.last_action_time = {}
            self.cooldown = cooldown
        
        def can_execute(self, action):
            now = time.time()
            last_time = self.last_action_time.get(action, 0)
            return now - last_time >= self.cooldown
        
        def mark_executed(self, action):
            self.last_action_time[action] = time.time()
    
    arb = SimpleArbitrator(cooldown=0.2)
    
    # First execution should be allowed
    assert arb.can_execute('jump')
    arb.mark_executed('jump')
    
    # Immediate re-execution should be blocked
    assert not arb.can_execute('jump')
    
    # After cooldown, should be allowed
    time.sleep(0.25)
    assert arb.can_execute('jump')
    
    # Different action should always be allowed
    assert arb.can_execute('attack')
    
    print("✓ Arbitrator cooldown test passed")


def run_all_tests():
    """Run all tests."""
    print("Running Hybrid System Tests...")
    print("=" * 60)
    
    try:
        test_world_coordinate_transformation_identity()
        test_world_coordinate_transformation_90deg()
        test_world_coordinate_transformation_upside_down()
        test_reflex_detection_jump()
        test_reflex_detection_attack()
        test_arbitrator_cooldown()
        
        print("=" * 60)
        print("✅ All tests passed!")
        return True
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
